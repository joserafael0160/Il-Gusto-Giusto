import os
import pytest
from datetime import datetime, timedelta

from src.models.restaurant import (
    Restaurant, Order, Dish, Employee, Ingredient, Table,
    EmployeeRole, ExperienceLevel
)
from src.core.scheduler import EventScheduler
from src.core.constraints import ConstraintValidator, MutualExclusionConstraint, CoRequirementConstraint
from src.persistence.json_handler import JSONHandler
from src.services.restaurant_service import calculate_role_deficit

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def sample_restaurant():
    """Restaurante de prueba con ingredientes, menú, empleados y mesas."""
    r = Restaurant(name="Il Gusto Giusto Test", balance=2000.0)

    r.ingredients["pasta"] = Ingredient("pasta", "Pasta", 10.0, "kg", 2.0, 3.0)
    r.ingredients["truffle_oil"] = Ingredient("truffle_oil", "Aceite de Trufa", 5.0, "l", 0.5, 45.0)
    r.ingredients["seafood_mix"] = Ingredient("seafood_mix", "Frutti di Mare", 5.0, "kg", 1.0, 18.0)
    r.ingredients["gorgonzola"] = Ingredient("gorgonzola", "Gorgonzola", 3.0, "kg", 0.5, 12.0)

    r.menu["d1"] = Dish(
        id="d1", name="Truffle Pasta", price=28.0, prep_time=30,
        ingredients={"pasta": 0.15, "truffle_oil": 0.05},
        base_ingredients=["pasta"],
        category="truffle_specialty",
        requires_specialty="pasta"
    )
    r.menu["d2"] = Dish(
        id="d2", name="Frittura", price=20.0, prep_time=20,
        ingredients={"seafood_mix": 0.3, "truffle_oil": 0.02},
        base_ingredients=["seafood_mix"],
        category="seafood"
    )
    r.menu["d3"] = Dish(
        id="d3", name="Gnocchi Gorgonzola", price=18.0, prep_time=25,
        ingredients={"pasta": 0.2, "gorgonzola": 0.15},
        base_ingredients=["pasta"],
        category="cheese_heavy",
        requires_specialty="pasta"
    )

    r.employees["chef1"] = Employee(
        id="chef1", name="Chef Luigi", role=EmployeeRole.CHEF,
        experience=ExperienceLevel.SENIOR, specialties=["pasta"],
        daily_wage=150.0, is_available=True
    )
    r.employees["chef2"] = Employee(
        id="chef2", name="Chef Mario", role=EmployeeRole.CHEF,
        experience=ExperienceLevel.JUNIOR, specialties=[],
        daily_wage=100.0, is_available=True
    )
    r.employees["waiter1"] = Employee(
        id="waiter1", name="Camilla", role=EmployeeRole.WAITER,
        experience=ExperienceLevel.JUNIOR, specialties=[],
        daily_wage=60.0, is_available=True
    )

    r.tables["t1"] = Table(id="t1", number=1, capacity=4, is_occupied=False)
    r.tables["t2"] = Table(id="t2", number=2, capacity=2, is_occupied=False)
    r.tables["t3"] = Table(id="t3", number=3, capacity=6, is_occupied=False)
    return r

@pytest.fixture
def scheduler(sample_restaurant):
    return EventScheduler(sample_restaurant)

# ---------------------------------------------------------------------------
# 1. Pedidos válidos y fallos básicos
# ---------------------------------------------------------------------------

class TestBasicScheduling:
    def test_valid_order(self, scheduler, sample_restaurant):
        order = Order(id="ord1", table_id="t1", dishes={"d1": 1})
        success, msg, event = scheduler.schedule_order(order, datetime.now())
        assert success
        assert event.assigned_chef_id == "chef1"
        assert sample_restaurant.tables["t1"].is_occupied
        assert not sample_restaurant.employees["chef1"].is_available

    def test_invalid_table(self, scheduler):
        order = Order(id="ord", table_id="no_existe", dishes={"d1": 1})
        success, msg, _ = scheduler.schedule_order(order, datetime.now())
        assert not success
        assert "mesa" in msg.lower()

    def test_invalid_dish(self, scheduler, sample_restaurant):
        order = Order(id="ord", table_id="t1", dishes={"fantasma": 1})
        success, msg, _ = scheduler.schedule_order(order, datetime.now())
        assert not success
        assert "no existe" in msg.lower()

    def test_table_collision(self, scheduler, sample_restaurant):
        start = datetime.now()
        order1 = Order(id="ord1", table_id="t1", dishes={"d1": 1})
        scheduler.schedule_order(order1, start)
        order2 = Order(id="ord2", table_id="t1", dishes={"d1": 1})
        success, msg, _ = scheduler.schedule_order(order2, start + timedelta(minutes=5))
        assert not success
        assert "mesa" in msg.lower() or "ocupada" in msg.lower()

    def test_chef_unavailable_same_interval(self, scheduler, sample_restaurant):
        start = datetime.now()
        order1 = Order(id="ord1", table_id="t1", dishes={"d1": 1})
        scheduler.schedule_order(order1, start)
        order2 = Order(id="ord2", table_id="t2", dishes={"d1": 1})
        success, msg, _ = scheduler.schedule_order(order2, start + timedelta(minutes=10))
        assert not success
        assert "chef" in msg.lower() or "libres" in msg.lower()

    def test_chef_without_specialty(self, scheduler, sample_restaurant):
        order1 = Order(id="ord1", table_id="t1", dishes={"d1": 1})
        scheduler.schedule_order(order1, datetime.now())
        order2 = Order(id="ord2", table_id="t2", dishes={"d1": 1})
        success, msg, _ = scheduler.schedule_order(order2, datetime.now() + timedelta(minutes=10))
        assert not success

    def test_zero_quantity_order(self, scheduler, sample_restaurant):
        order = Order(id="ord_zero", table_id="t1", dishes={"d1": 0})
        success, msg, _ = scheduler.schedule_order(order, datetime.now())
        assert not success
        assert "plato" in msg.lower() or "selecciona" in msg.lower()

    def test_does_not_assign_waiter_as_chef(self, scheduler, sample_restaurant):
        order = Order(id="ord", table_id="t1", dishes={"d2": 1})  # d2 no requiere especialidad
        success, _, event = scheduler.schedule_order(order, datetime.now())
        assert success
        assert event.assigned_chef_id != "waiter1"

    def test_overlap_boundary_exact_end_start(self, scheduler, sample_restaurant):
        start1 = datetime.now()
        order1 = Order(id="ord1", table_id="t1", dishes={"d1": 1})  # 30 min
        scheduler.schedule_order(order1, start1)
        start2 = start1 + timedelta(minutes=30)
        order2 = Order(id="ord2", table_id="t1", dishes={"d1": 1})
        success, msg, _ = scheduler.schedule_order(order2, start2)
        assert success

# ---------------------------------------------------------------------------
# 2. Cancelación y liberación de recursos (incluye reembolso)
# ---------------------------------------------------------------------------

class TestCancellation:
    def test_cancel_frees_table_and_chef(self, scheduler, sample_restaurant):
        order = Order(id="ord_cancel", table_id="t1", dishes={"d1": 1})
        _, _, event = scheduler.schedule_order(order, datetime.now())
        assert sample_restaurant.tables["t1"].is_occupied
        assert not sample_restaurant.employees["chef1"].is_available

        success, _ = scheduler.cancel_event(event.id)
        assert success
        assert not sample_restaurant.tables["t1"].is_occupied
        assert sample_restaurant.employees["chef1"].is_available

    def test_cancel_nonexistent_event(self, scheduler):
        success, msg = scheduler.cancel_event("fake_id")
        assert not success
        assert "no encontrado" in msg.lower()

    def test_cancel_future_event_liberates_resources(self, scheduler, sample_restaurant):
        start = datetime.now() + timedelta(hours=2)
        order = Order(id="ord_future", table_id="t1", dishes={"d1": 1})
        success, _, event = scheduler.schedule_order(order, start)
        assert success
        assert sample_restaurant.tables["t1"].is_occupied
        assert not sample_restaurant.employees["chef1"].is_available

        scheduler.cancel_event(event.id)
        assert not sample_restaurant.tables["t1"].is_occupied
        assert sample_restaurant.employees["chef1"].is_available

    def test_cancel_refunds_ingredients(self, scheduler, sample_restaurant):
        initial_pasta = sample_restaurant.ingredients["pasta"].quantity
        initial_truffle = sample_restaurant.ingredients["truffle_oil"].quantity

        order = Order(id="ord", table_id="t1", dishes={"d1": 2})  # consume pasta 0.3, truffle 0.1
        _, _, event = scheduler.schedule_order(order, datetime.now())
        assert sample_restaurant.ingredients["pasta"].quantity == initial_pasta - 0.3
        assert sample_restaurant.ingredients["truffle_oil"].quantity == initial_truffle - 0.1

        scheduler.cancel_event(event.id)
        assert sample_restaurant.ingredients["pasta"].quantity == initial_pasta
        assert sample_restaurant.ingredients["truffle_oil"].quantity == initial_truffle

    def test_cancel_with_optional_removal_refunds_correctly(self, scheduler, sample_restaurant):
        order = Order(id="ord", table_id="t1", dishes={"d2": 2},
                      customized_removals={"d2": ["truffle_oil"]})
        initial_seafood = sample_restaurant.ingredients["seafood_mix"].quantity
        initial_truffle = sample_restaurant.ingredients["truffle_oil"].quantity

        success, _, event = scheduler.schedule_order(order, datetime.now())
        assert success
        # Solo se consumió seafood_mix (0.3 * 2 = 0.6)
        assert sample_restaurant.ingredients["seafood_mix"].quantity == initial_seafood - 0.6
        assert sample_restaurant.ingredients["truffle_oil"].quantity == initial_truffle

        scheduler.cancel_event(event.id)
        assert sample_restaurant.ingredients["seafood_mix"].quantity == initial_seafood
        assert sample_restaurant.ingredients["truffle_oil"].quantity == initial_truffle

# ---------------------------------------------------------------------------
# 3. Stock y restricciones
# ---------------------------------------------------------------------------

class TestStockAndConstraints:
    def test_insufficient_stock(self, scheduler, sample_restaurant):
        sample_restaurant.ingredients["pasta"].quantity = 0.01
        order = Order(id="ord", table_id="t1", dishes={"d1": 2})
        success, msg, _ = scheduler.schedule_order(order, datetime.now())
        assert not success
        assert "stock" in msg.lower() or "insuficiente" in msg.lower()

    def test_optional_removal_does_not_consume(self, scheduler, sample_restaurant):
        order = Order(id="ord", table_id="t1", dishes={"d2": 1},
                      customized_removals={"d2": ["truffle_oil"]})
        initial_truffle = sample_restaurant.ingredients["truffle_oil"].quantity
        success, _, _ = scheduler.schedule_order(order, datetime.now())
        assert success
        assert sample_restaurant.ingredients["truffle_oil"].quantity == initial_truffle

    def test_base_ingredient_removal_ignored(self, scheduler, sample_restaurant):
        order = Order(id="ord", table_id="t1", dishes={"d1": 1},
                      customized_removals={"d1": ["pasta"]})
        sample_restaurant.ingredients["pasta"].quantity = 0.0
        success, msg, _ = scheduler.schedule_order(order, datetime.now())
        assert success  # no se consume pasta

    def test_co_requirement_truffle(self, scheduler, sample_restaurant):
        sample_restaurant.ingredients["truffle_oil"].quantity = 0.0
        order = Order(id="ord", table_id="t1", dishes={"d1": 1})
        success, msg, _ = scheduler.schedule_order(order, datetime.now())
        assert not success
        assert "trufa" in msg.lower() or "oil" in msg.lower()

    def test_mutual_exclusion_seafood_cheese(self, scheduler, sample_restaurant):
        order = Order(id="ord_mix", table_id="t1", dishes={"d2": 1, "d3": 1})
        success, msg, _ = scheduler.schedule_order(order, datetime.now())
        assert not success
        assert ("tradición" in msg.lower()) or ("mar" in msg.lower()) or ("queso" in msg.lower())

    def test_no_exclusion_if_only_one_category(self, scheduler, sample_restaurant):
        order = Order(id="ord", table_id="t1", dishes={"d2": 1})
        success, _, _ = scheduler.schedule_order(order, datetime.now())
        assert success

    def test_co_requirement_with_multiple_dishes(self, scheduler, sample_restaurant):
        sample_restaurant.ingredients["truffle_oil"].quantity = 0.0
        order = Order(id="ord", table_id="t1", dishes={"d1": 1, "d2": 1})
        success, msg, _ = scheduler.schedule_order(order, datetime.now())
        assert not success

    def test_stock_deduction_on_multiple_orders(self, scheduler, sample_restaurant):
        initial_pasta = sample_restaurant.ingredients["pasta"].quantity
        order1 = Order(id="ord1", table_id="t1", dishes={"d1": 2})
        order2 = Order(id="ord2", table_id="t2", dishes={"d3": 3})
        scheduler.schedule_order(order1, datetime.now())
        scheduler.schedule_order(order2, datetime.now() + timedelta(minutes=40))
        expected_pasta = initial_pasta - (0.15*2) - (0.20*3)
        assert sample_restaurant.ingredients["pasta"].quantity == expected_pasta

    def test_customized_removal_does_not_affect_stock_check(self, scheduler, sample_restaurant):
        sample_restaurant.ingredients["truffle_oil"].quantity = 0.0
        order = Order(id="ord", table_id="t1", dishes={"d2": 1},
                      customized_removals={"d2": ["truffle_oil"]})
        success, _, _ = scheduler.schedule_order(order, datetime.now())
        assert success

# ---------------------------------------------------------------------------
# 4. Búsqueda automática de hueco
# ---------------------------------------------------------------------------

class TestFindNextSlot:
    def test_find_slot_after_event(self, scheduler, sample_restaurant):
        order1 = Order(id="ord1", table_id="t1", dishes={"d1": 1})
        scheduler.schedule_order(order1, datetime.now())
        order2 = Order(id="ord2", table_id="t1", dishes={"d1": 1})
        slot = scheduler.find_next_available_slot(order2)
        event1 = scheduler.scheduled_events[0]
        assert slot >= event1.end_time

    def test_find_slot_respects_constraints(self, scheduler, sample_restaurant):
        sample_restaurant.ingredients["truffle_oil"].quantity = 0.0
        order = Order(id="ord", table_id="t1", dishes={"d1": 1})
        slot = scheduler.find_next_available_slot(order)
        assert slot is None

    def test_find_slot_no_event_scheduled(self, scheduler):
        order = Order(id="ord", table_id="t1", dishes={"d1": 1})
        slot = scheduler.find_next_available_slot(order)
        assert slot is not None
        assert abs((slot - datetime.now()).total_seconds()) < 10

    def test_find_slot_respects_chef_specialty(self, scheduler, sample_restaurant):
        start = datetime.now()
        order1 = Order(id="ord1", table_id="t1", dishes={"d1": 1})
        scheduler.schedule_order(order1, start)
        order2 = Order(id="ord2", table_id="t2", dishes={"d1": 1})
        slot = scheduler.find_next_available_slot(order2)
        assert slot is not None
        assert slot >= start + timedelta(minutes=30)

    def test_find_slot_with_chef_busy(self, scheduler, sample_restaurant):
        start = datetime.now()
        order1 = Order(id="ord1", table_id="t1", dishes={"d1": 1})  # chef1
        scheduler.schedule_order(order1, start)
        order2 = Order(id="ord2", table_id="t2", dishes={"d2": 1})  # chef2
        scheduler.schedule_order(order2, start)
        order3 = Order(id="ord3", table_id="t3", dishes={"d3": 1})  # requiere pasta -> chef1
        slot = scheduler.find_next_available_slot(order3)
        assert slot is not None
        assert slot >= start + timedelta(minutes=30)

# ---------------------------------------------------------------------------
# 5. Persistencia JSON (ida y vuelta)
# ---------------------------------------------------------------------------

class TestPersistence:
    def test_save_load_roundtrip(self, scheduler, sample_restaurant):
        test_file = "data/test_persistence_temp.json"
        JSONHandler.save_restaurant(sample_restaurant, scheduler.scheduled_events, test_file)

        loaded_rest, loaded_events = JSONHandler.load_restaurant(test_file)
        assert loaded_rest.name == sample_restaurant.name
        assert loaded_rest.balance == sample_restaurant.balance
        assert len(loaded_events) == len(scheduler.scheduled_events)
        assert "chef1" in loaded_rest.employees
        assert loaded_rest.employees["chef1"].role == EmployeeRole.CHEF
        assert loaded_rest.ingredients["pasta"].quantity == sample_restaurant.ingredients["pasta"].quantity

        if os.path.exists(test_file):
            os.remove(test_file)

    def test_load_nonexistent_file(self):
        rest, events = JSONHandler.load_restaurant("data/fantasma.json")
        assert rest is None
        assert events == []

    def test_persistence_with_candidates(self, sample_restaurant):
        sample_restaurant.applicants = [
            {
                "name": "Test Candidate",
                "role": EmployeeRole.CHEF,
                "experience": ExperienceLevel.SENIOR,
                "specialties": ["test"],
                "daily_wage": 200.0,
                "bio": "Test bio"
            }
        ]
        test_file = "data/test_persistence_cands.json"
        JSONHandler.save_restaurant(sample_restaurant, [], test_file)
        loaded_rest, _ = JSONHandler.load_restaurant(test_file)
        assert len(loaded_rest.applicants) == 1
        assert loaded_rest.applicants[0]["name"] == "Test Candidate"
        if os.path.exists(test_file):
            os.remove(test_file)

    def test_corrupted_json_falls_back(self, tmp_path):
        bad_file = tmp_path / "corrupt.json"
        bad_file.write_text("{ esto no es json")
        rest, events = JSONHandler.load_restaurant(str(bad_file))
        assert rest is None

    def test_complex_state_persistence(self, scheduler, sample_restaurant):
        order1 = Order(id="o1", table_id="t1", dishes={"d1": 2})
        order2 = Order(id="o2", table_id="t2", dishes={"d2": 1})
        scheduler.schedule_order(order1, datetime.now())
        scheduler.schedule_order(order2, datetime.now() + timedelta(hours=1))
        sample_restaurant.add_transaction(-50, "Compra")
        sample_restaurant.applicants = []
        test_file = "data/test_complex.json"
        JSONHandler.save_restaurant(sample_restaurant, scheduler.scheduled_events, test_file)
        loaded_rest, loaded_events = JSONHandler.load_restaurant(test_file)
        assert loaded_rest.balance == sample_restaurant.balance
        assert len(loaded_events) == 2
        assert loaded_rest.ingredients["pasta"].quantity == sample_restaurant.ingredients["pasta"].quantity
        if os.path.exists(test_file):
            os.remove(test_file)

# ---------------------------------------------------------------------------
# 6. Modelo de negocio y transacciones
# ---------------------------------------------------------------------------

class TestRestaurantModel:
    def test_add_transaction_updates_balance(self, sample_restaurant):
        initial = sample_restaurant.balance
        sample_restaurant.add_transaction(500, "Venta")
        assert sample_restaurant.balance == initial + 500
        assert len(sample_restaurant.history) == 1
        assert sample_restaurant.history[-1]["description"] == "Venta"

    def test_dish_profit_calculation(self, sample_restaurant):
        dish = sample_restaurant.menu["d1"]
        cost = (sample_restaurant.ingredients["pasta"].price_per_unit * dish.ingredients["pasta"] +
                sample_restaurant.ingredients["truffle_oil"].price_per_unit * dish.ingredients["truffle_oil"])
        assert dish.price - cost > 0

    def test_employee_roles(self):
        e = Employee("x", "Test", EmployeeRole.CHEF, ExperienceLevel.SENIOR, [], 100)
        assert e.role.value == "chef"
        assert e.experience.value == "senior"

    def test_table_occupancy(self):
        t = Table("t", 1, 4)
        assert not t.is_occupied
        t.is_occupied = True
        assert t.is_occupied

    def test_add_and_remove_dish(self, sample_restaurant):
        new_dish = Dish("d_new", "Test Dish", 10.0, 10, {"pasta": 0.1}, ["pasta"], "test")
        sample_restaurant.menu["d_new"] = new_dish
        assert "d_new" in sample_restaurant.menu
        del sample_restaurant.menu["d_new"]
        assert "d_new" not in sample_restaurant.menu

    def test_ingredient_min_quantity_alert(self, sample_restaurant):
        ing = sample_restaurant.ingredients["pasta"]
        ing.quantity = ing.min_quantity - 0.1
        assert ing.quantity <= ing.min_quantity

# ---------------------------------------------------------------------------
# 7. Múltiples mesas y chefs en paralelo
# ---------------------------------------------------------------------------

class TestParallelUsage:
    def test_two_tables_independent(self, scheduler, sample_restaurant):
        start = datetime.now()
        order1 = Order(id="o1", table_id="t1", dishes={"d1": 1})
        order2 = Order(id="o2", table_id="t2", dishes={"d2": 1})
        s1, _, _ = scheduler.schedule_order(order1, start)
        s2, _, _ = scheduler.schedule_order(order2, start)
        assert s1
        assert s2
        assert sample_restaurant.tables["t1"].is_occupied
        assert sample_restaurant.tables["t2"].is_occupied

    def test_chef_can_serve_two_tables_sequentially(self, scheduler, sample_restaurant):
        start = datetime.now()
        order1 = Order(id="o1", table_id="t1", dishes={"d1": 1})
        scheduler.schedule_order(order1, start)
        order2 = Order(id="o2", table_id="t2", dishes={"d3": 1})
        success, _, _ = scheduler.schedule_order(order2, start + timedelta(minutes=35))
        assert success

    def test_chef2_can_take_non_specialty_order(self, scheduler, sample_restaurant):
        order = Order(id="o", table_id="t1", dishes={"d2": 1})
        success, _, event = scheduler.schedule_order(order, datetime.now())
        assert success
        assert event.assigned_chef_id in ["chef1", "chef2"]

# ---------------------------------------------------------------------------
# 8. Servicio de personal (staffing)
# ---------------------------------------------------------------------------

class TestStaffingService:
    def test_calculate_deficit_chef(self, sample_restaurant):
        deficit = calculate_role_deficit(sample_restaurant, EmployeeRole.CHEF)
        assert deficit == -1  # 2 chefs, target 1

    def test_calculate_deficit_waiter(self, sample_restaurant):
        deficit = calculate_role_deficit(sample_restaurant, EmployeeRole.WAITER)
        assert deficit == 0

    def test_deficit_no_employees(self):
        r = Restaurant("Empty", 1000)
        r.tables["t1"] = Table("t1", 1, 2)
        r.tables["t2"] = Table("t2", 2, 2)
        deficit_chef = calculate_role_deficit(r, EmployeeRole.CHEF)
        deficit_waiter = calculate_role_deficit(r, EmployeeRole.WAITER)
        assert deficit_chef == 1
        assert deficit_waiter == 1

    def test_deficit_with_many_tables(self):
        r = Restaurant("Big", 5000)
        for i in range(10):
            r.tables[f"t{i}"] = Table(f"t{i}", i, 4)
        deficit_c = calculate_role_deficit(r, EmployeeRole.CHEF)
        deficit_w = calculate_role_deficit(r, EmployeeRole.WAITER)
        assert deficit_c == 3
        assert deficit_w == 5

# ---------------------------------------------------------------------------
# 9. Validación de constraints adicionales
# ---------------------------------------------------------------------------

class TestConstraints:
    def test_mutual_exclusion_different_categories_ok(self):
        c = MutualExclusionConstraint("test", "a", "b", "no mezclar")
        dish1 = Dish("x", "X", 10, 10, {}, [], "c")
        dish2 = Dish("y", "Y", 10, 10, {}, [], "d")
        valid, _ = c.validate([dish1, dish2], {})
        assert valid

    def test_co_requirement_missing_ingredient(self):
        c = CoRequirementConstraint("test", "cat", "ing1", "falta ing1")
        dish = Dish("x", "X", 10, 10, {}, [], "cat")
        valid, msg = c.validate([dish], {})
        assert not valid

    def test_co_requirement_ingredient_quantity_zero(self):
        c = CoRequirementConstraint("test", "cat", "ing1", "falta ing1")
        dish = Dish("x", "X", 10, 10, {}, [], "cat")
        ing = Ingredient("ing1", "Ing1", 0.0, "kg", 0.1, 5.0)
        valid, msg = c.validate([dish], {"ing1": ing})
        assert not valid

    def test_validator_with_both_constraints(self, sample_restaurant):
        validator = ConstraintValidator()
        dishes = [
            sample_restaurant.menu["d2"],  # seafood
            sample_restaurant.menu["d3"]   # cheese_heavy
        ]
        valid, msg = validator.validate(dishes, sample_restaurant.ingredients)
        assert not valid

    def test_add_remove_constraint_dynamically(self):
        validator = ConstraintValidator()
        initial_count = len(validator.constraints)
        new_rule = MutualExclusionConstraint("test", "a", "b", "msg")
        validator.constraints.append(new_rule)
        assert len(validator.constraints) == initial_count + 1
        validator.constraints.remove(new_rule)
        assert len(validator.constraints) == initial_count