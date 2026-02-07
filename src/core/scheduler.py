import uuid
from datetime import datetime, timedelta
from typing import Tuple, Optional, List

from src.models.restaurant import Restaurant, Order, EmployeeRole
from src.models.events import Event
from src.core.constraints import ConstraintValidator

class EventScheduler:
    def __init__(self, restaurant: Restaurant):
        self.restaurant = restaurant
        self.scheduled_events: List[Event] = []
        self.validator = ConstraintValidator()

    def schedule_order(self, order: Order, start_time: datetime) -> Tuple[bool, str, Optional[Event]]:
        """
        Intenta planificar una orden validando recursos, tiempo y reglas.
        """
        # 1. Validar Mesa y conflicto de horario
        table = self.restaurant.tables.get(order.table_id)
        if not table:
            return False, "Mesa inválida", None
        
        # Obtenemos duración para calcular end_time
        max_prep_time = 0
        required_specialty = None
        order_dishes_objs = []

        for dish_id, qty in order.dishes.items():
            dish = self.restaurant.menu.get(dish_id)
            if not dish: continue
            order_dishes_objs.append(dish)
            if dish.prep_time > max_prep_time:
                max_prep_time = dish.prep_time
            if dish.requires_specialty:
                required_specialty = dish.requires_specialty

        duration = timedelta(minutes=max_prep_time)
        end_time = start_time + duration

        # 2. Verificar si la mesa está libre en ese intervalo
        if not self._is_resource_free(table.id, start_time, end_time, "table"):
             return False, f"La mesa {table.number} ya está reservada o ocupada en ese horario.", None

        # 3. Validar Reglas de Negocio (Constraints de ingredientes base)
        valid, msg = self.validator.validate(order_dishes_objs, self.restaurant.ingredients)
        if not valid:
            return False, f"Regla violada: {msg}", None

        # 4. Validar Stock Real (Cantidades exactas)
        stock_ok, stock_msg = self._check_ingredients_stock(order.dishes)
        if not stock_ok:
            return False, stock_msg, None

        # 5. Asignar Chef disponible y con especialidad
        chef = self._find_available_chef(start_time, end_time, required_specialty)
        if not chef:
            return False, "No hay chef disponible con la especialidad necesaria en ese horario.", None

        # 6. ÉXITO: Crear Evento y Actualizar Recursos
        event = Event(
            id=f"evt_{uuid.uuid4().hex[:8]}",
            order_id=order.id,
            table_id=table.id,
            assigned_chef_id=chef.id,
            start_time=start_time,
            end_time=end_time
        )
        
        # Descontar stock definitivamente
        self._subtract_stock(order.dishes)
        
        self.scheduled_events.append(event)
        
        # Marcar estados para la UI
        chef.is_available = False
        chef.busy_until = end_time
        table.is_occupied = True
        
        return True, "Orden planificada correctamente.", event

    def find_next_available_slot(self, order: Order) -> Optional[datetime]:
        """
        Busca el próximo hueco libre analizando el futuro cada 5 minutos.
        (Soluciona el fallo de NoneType en los tests)
        """
        current_search = datetime.now()
        limit = current_search + timedelta(hours=24) # Límite de búsqueda: 1 día

        while current_search < limit:
            # Simulamos validación básica (Mesa + Stock + Chef)
            success, _, _ = self._dry_run_validation(order, current_search)
            if success:
                return current_search
            current_search += timedelta(minutes=5)
        
        return None

    def cancel_event(self, event_id: str):
        """Libera los recursos y elimina el evento de la planificación."""
        event_to_remove = next((e for e in self.scheduled_events if e.id == event_id), None)
        if event_to_remove:
            table = self.restaurant.tables.get(event_to_remove.table_id)
            if table: table.is_occupied = False
        
            chef = self.restaurant.employees.get(event_to_remove.assigned_chef_id)
            if chef:
                chef.is_available = True
                chef.busy_until = None
            
            self.scheduled_events.remove(event_to_remove)
            return True, "Evento cancelado."
        return False, "No se encontró el evento."

    # --- MÉTODOS PRIVADOS DE APOYO ---

    def _dry_run_validation(self, order, start_time):
        table = self.restaurant.tables.get(order.table_id)
        if not table: return False, "", None
        
        # Calcular end_time
        max_t = max([self.restaurant.menu[d].prep_time for d in order.dishes if d in self.restaurant.menu] or [0])
        end_time = start_time + timedelta(minutes=max_t)
        
        if not self._is_resource_free(table.id, start_time, end_time, "table"): return False, "", None
        if not self._check_ingredients_stock(order.dishes)[0]: return False, "", None
        
        spec = next((self.restaurant.menu[d].requires_specialty for d in order.dishes if d in self.restaurant.menu and self.restaurant.menu[d].requires_specialty), None)
        if not self._find_available_chef(start_time, end_time, spec): return False, "", None
        
        return True, "", None

    def _is_resource_free(self, res_id, start, end, res_type="table"):
        """Lógica de colisión de intervalos: (StartA < EndB) y (StartB < EndA)"""
        for evt in self.scheduled_events:
            compare_id = evt.table_id if res_type == "table" else evt.assigned_chef_id
            if compare_id == res_id:
                if start < evt.end_time and end > evt.start_time:
                    return False
        return True

    def _find_available_chef(self, start, end, specialty=None):
        """Busca un chef ignorando el booleano 'is_available' y basándose solo en su agenda real."""
        for chef in self.restaurant.employees.values():
            if chef.role == EmployeeRole.CHEF:
                # 1. Validar Especialidad (Si el plato la pide)
                if specialty and specialty not in chef.specialties:
                    continue
                
                # 2. Validar Agenda (¿Tiene algún evento que choque con este horario?)
                if self._is_resource_free(chef.id, start, end, res_type="chef"):
                    return chef

        return None

    def _is_resource_free(self, res_id, start, end, res_type="table"):
        """
        Comprueba si un recurso está libre en un intervalo.
        Añadimos un pequeño margen de 1 minuto para evitar errores de precisión.
        """
        for evt in self.scheduled_events:
            compare_id = evt.table_id if res_type == "table" else evt.assigned_chef_id
            if compare_id == res_id:
                # Lógica de solapamiento: (InicioA < FinB) AND (FinA > InicioB)
                if start < evt.end_time and end > evt.start_time:
                    return False
        return True

    def _check_ingredients_stock(self, dishes_requested):
        """Verifica cantidades exactas """
        for d_id, qty in dishes_requested.items():
            dish = self.restaurant.menu.get(d_id)
            if not dish: continue
            for ing_id, amt in dish.ingredients.items():
                ing = self.restaurant.ingredients.get(ing_id)
                if not ing or ing.quantity < (amt * qty):
                    return False, f"Stock insuficiente de {ing.name if ing else ing_id}."
        return True, ""

    def _subtract_stock(self, dishes_requested):
        """Resta los ingredientes tras confirmar la orden"""
        for d_id, qty in dishes_requested.items():
            dish = self.restaurant.menu.get(d_id)
            for ing_id, amt in dish.ingredients.items():
                self.restaurant.ingredients[ing_id].quantity -= (amt * qty)