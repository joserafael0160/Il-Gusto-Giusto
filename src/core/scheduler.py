# src/core/scheduler.py
import uuid
from datetime import datetime, timedelta
from typing import Tuple, Optional, List, Dict, Any

from src.models.restaurant import Restaurant, Order, EmployeeRole, Dish
from src.models.events import Event
from src.core.constraints import ConstraintValidator

class EventScheduler:
    def __init__(self, restaurant: Restaurant):
        self.restaurant = restaurant
        self.scheduled_events: List[Event] = []
        self.validator = ConstraintValidator()

    def schedule_order(self, order: Order, start_time: datetime) -> Tuple[bool, str, Optional[Event]]:
        """Handles scheduling validation, resource checks, and updates state upon success."""
        table = self.restaurant.tables.get(order.table_id)
        if not table:
            return False, "Mesa inválida", None

        max_prep_time = 0
        required_specialty = None
        ordered_dishes_objs: List[Dish] = []

        for dish_id, qty in order.dishes.items():
            dish = self.restaurant.menu.get(dish_id)
            if not dish:
                return False, f"Plato {dish_id} no existe", None
            if qty > 0:
                ordered_dishes_objs.append(dish)
                if dish.prep_time > max_prep_time:
                    max_prep_time = dish.prep_time
                if dish.requires_specialty:
                    required_specialty = dish.requires_specialty

        if not ordered_dishes_objs:
            return False, "Debe seleccionar al menos un plato con cantidad mayor a cero.", None

        duration = timedelta(minutes=max_prep_time)
        end_time = start_time + duration

        # 1. Resource collision: Table occupied
        if not self._is_resource_free(table.id, start_time, end_time, "table"):
            return False, f"La mesa {table.number} ya está reservada u ocupada en ese intervalo.", None

        # 2. Domain Constraints check
        valid, msg = self.validator.validate(ordered_dishes_objs, self.restaurant.ingredients)
        if not valid:
            return False, msg, None

        # 3. Pantry Stock check
        stock_ok, stock_msg = self._check_ingredients_stock(order)
        if not stock_ok:
            return False, stock_msg, None

        # 4. Chef Assignment check
        chef = self._find_available_chef(start_time, end_time, required_specialty)
        if not chef:
            return False, "No hay chefs calificados o libres para preparar este pedido en el horario solicitado.", None

        # 5. Success: Deduct pantry resources, assign event, adjust states
        self._subtract_stock(order)

        event = Event(
            id=f"evt_{uuid.uuid4().hex[:8]}",
            order_id=order.id,
            table_id=table.id,
            assigned_chef_id=chef.id,
            start_time=start_time,
            end_time=end_time,
            dishes=order.dishes,
            customized_removals=order.customized_removals
        )
        self.scheduled_events.append(event)

        chef.is_available = False
        chef.busy_until = end_time
        table.is_occupied = True

        revenue = sum(self.restaurant.menu[d_id].price * qty for d_id, qty in order.dishes.items())
        self.restaurant.add_transaction(revenue, f"Venta de Comanda {order.id} en Mesa {table.number}")

        return True, "Pedido agendado y cocinado exitosamente.", event

    def find_next_available_slot(self, order: Order) -> Optional[datetime]:
        """Finds the next clean interval within 24h where the order has no conflicts."""
        current_search = datetime.now()
        limit = current_search + timedelta(hours=24)

        while current_search < limit:
            success, _ = self._dry_run_validation(order, current_search)
            if success:
                return current_search
            current_search += timedelta(minutes=5)
        return None

    def cancel_event(self, event_id: str) -> Tuple[bool, str]:
        """Releases assigned table and chef, refunds ingredients and money."""
        event = next((e for e in self.scheduled_events if e.id == event_id), None)
        if not event:
            return False, "Evento no encontrado."

        table = self.restaurant.tables.get(event.table_id)
        if table:
            table.is_occupied = False

        chef = self.restaurant.employees.get(event.assigned_chef_id)
        if chef:
            chef.is_available = True
            chef.busy_until = None

        # Precise pantry refund
        for dish_id, qty in event.dishes.items():
            dish = self.restaurant.menu.get(dish_id)
            if not dish:
                continue
            removed = event.customized_removals.get(dish_id, [])
            for ing_id, amt in dish.ingredients.items():
                if ing_id in removed:
                    continue
                if ing_id in self.restaurant.ingredients:
                    self.restaurant.ingredients[ing_id].quantity += (amt * qty)

        # ✅ Revertir el ingreso económico
        revenue = sum(self.restaurant.menu[d_id].price * qty for d_id, qty in event.dishes.items())
        self.restaurant.add_transaction(-revenue, f"Reembolso por cancelación de Comanda {event.order_id}")

        self.scheduled_events.remove(event)
        return True, "Evento cancelado y recursos devueltos con éxito al inventario."

    def _dry_run_validation(self, order: Order, start_time: datetime) -> Tuple[bool, str]:
        table = self.restaurant.tables.get(order.table_id)
        if not table:
            return False, "Mesa inválida"

        ordered_dishes_objs = []
        for dish_id, qty in order.dishes.items():
            dish = self.restaurant.menu.get(dish_id)
            if not dish:
                return False, f"Plato {dish_id} no existe"
            if qty > 0:
                ordered_dishes_objs.append(dish)

        if not ordered_dishes_objs:
            return False, "Debe seleccionar al menos un plato."

        max_t = max(d.prep_time for d in ordered_dishes_objs)
        end_time = start_time + timedelta(minutes=max_t)

        if not self._is_resource_free(table.id, start_time, end_time, "table"):
            return False, "Mesa ocupada en ese intervalo"

        valid, msg = self.validator.validate(ordered_dishes_objs, self.restaurant.ingredients)
        if not valid:
            return False, msg

        if not self._check_ingredients_stock(order)[0]:
            return False, "Stock insuficiente"

        spec = next((d.requires_specialty for d in ordered_dishes_objs if d.requires_specialty), None)
        if not self._find_available_chef(start_time, end_time, spec):
            return False, "Sin chef calificado libre"

        return True, ""

    def _is_resource_free(self, res_id: str, start: datetime, end: datetime, res_type: str = "table") -> bool:
        for evt in self.scheduled_events:
            compare_id = evt.table_id if res_type == "table" else evt.assigned_chef_id
            if compare_id == res_id:
                if start < evt.end_time and end > evt.start_time:
                    return False
        return True

    def _find_available_chef(self, start: datetime, end: datetime, specialty: Optional[str] = None) -> Optional[Any]:
        for chef in self.restaurant.employees.values():
            if chef.role == EmployeeRole.CHEF:
                if specialty and specialty not in chef.specialties:
                    continue
                if self._is_resource_free(chef.id, start, end, res_type="chef"):
                    return chef
        return None

    def _check_ingredients_stock(self, order: Order) -> Tuple[bool, str]:
        needed: Dict[str, float] = {}
        for dish_id, qty in order.dishes.items():
            dish = self.restaurant.menu.get(dish_id)
            if not dish:
                continue
            removed = order.customized_removals.get(dish_id, [])
            for ing_id, amt in dish.ingredients.items():
                if ing_id in removed:
                    continue
                needed[ing_id] = needed.get(ing_id, 0.0) + (amt * qty)

        for ing_id, qty_needed in needed.items():
            ing = self.restaurant.ingredients.get(ing_id)
            if not ing or ing.quantity < qty_needed:
                name = ing.name if ing else ing_id
                return False, f"Stock insuficiente del ingrediente: {name}."
        return True, ""

    def _subtract_stock(self, order: Order) -> None:
        for dish_id, qty in order.dishes.items():
            dish = self.restaurant.menu.get(dish_id)
            if not dish:
                continue
            removed = order.customized_removals.get(dish_id, [])
            for ing_id, amt in dish.ingredients.items():
                if ing_id in removed:
                    continue
                self.restaurant.ingredients[ing_id].quantity -= (amt * qty)