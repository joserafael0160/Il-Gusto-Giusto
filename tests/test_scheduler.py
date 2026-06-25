# tests/test_scheduler.py
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

@pytest.fixture
def sample_restaurant():
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

class TestBasicScheduling:
    def test_valid_order(self, scheduler, sample_restaurant):
        order = Order(id="ord1", table_id="t1", dishes={"d1": 1})
        success, msg, event = scheduler.schedule_order(order, datetime.now())
        assert success
        assert event is not None
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
        order = Order(id="ord", table_id="t1", dishes={"d2": 1})
        success, _, event = scheduler.schedule_order(order, datetime.now())
        assert success
        assert event is not None
        assert event.assigned_chef_id != "waiter1"

    def test_overlap_boundary_exact_end_start(self, scheduler, sample_restaurant):
        start1 = datetime.now()
        order1 = Order(id="ord1", table_id="t1", dishes={"d1": 1})
        scheduler.schedule_order(order1, start1)
        start2 = start1 + timedelta(minutes=30)
        order2 = Order(id="ord2", table_id="t1", dishes={"d1": 1})
        success, msg, _ = scheduler.schedule_order(order2, start2)
        assert success

class TestCancellation:
    def test_cancel_frees_table_and_chef(self, scheduler, sample_restaurant):
        order = Order(id="ord_cancel", table_id="t1", dishes={"d1": 1})
        _, _, event = scheduler.schedule_order(order, datetime.now())
        assert event is not None
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
        assert event is not None
        assert sample_restaurant.tables["t1"].is_occupied
        assert not sample_restaurant.employees["chef1"].is_available

        scheduler.cancel_event(event.id)
        assert not sample_restaurant.tables["t1"].is_occupied
        assert sample_restaurant.employees["chef1"].is_available

    def test_cancel_refunds_ingredients(self, scheduler, sample_restaurant):
        initial_pasta = sample_restaurant.ingredients["pasta"].quantity
        initial_truffle = sample_restaurant.ingredients["truffle_oil"].quantity

        order = Order(id="ord", table_id="t1", dishes={"d1": 2})
        success, _, event = scheduler.schedule_order(order, datetime.now())
        assert success
        assert event is not None
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
        assert event is not None
        assert sample_restaurant.ingredients["seafood_mix"].quantity == initial_seafood - 0.6
        assert sample_restaurant.ingredients["truffle_oil"].quantity == initial_truffle

        scheduler.cancel_event(event.id)
        assert sample_restaurant.ingredients["seafood_mix"].quantity == initial_seafood
        assert sample_restaurant.ingredients["truffle_oil"].quantity == initial_truffle

    def test_cancel_refunds_revenue(self, scheduler, sample_restaurant):
        initial_balance = sample_restaurant.balance
        order = Order(id="ord", table_id="t1", dishes={"d1": 1})
        _, _, event = scheduler.schedule_order(order, datetime.now())
        # Después de la venta, el balance subió 28.0 (precio de d1)
        assert sample_restaurant.balance == initial_balance + 28.0
        scheduler.cancel_event(event.id)
        # El balance debe regresar al valor original
        assert sample_restaurant.balance == initial_balance

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
        success, _, _ = scheduler.schedule_order(order, datetime.now())
        assert success

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
        assert "tradición" in msg.lower() or "mar" in msg.lower() or "queso" in msg.lower()

class TestFindNextSlot:
    def test_find_slot_after_event(self, scheduler, sample_restaurant):
        order1 = Order(id="ord1", table_id="t1", dishes={"d1": 1})
        scheduler.schedule_order(order1, datetime.now())
        order2 = Order(id="ord2", table_id="t1", dishes={"d1": 1})
        slot = scheduler.find_next_available_slot(order2)
        event1 = scheduler.scheduled_events[0]
        assert slot is not None
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

class TestPersistence:
    def test_save_load_roundtrip(self, scheduler, sample_restaurant):
        test_file = "data/test_persistence_temp.json"
        JSONHandler.save(sample_restaurant, scheduler.scheduled_events, test_file)

        loaded_rest, loaded_events = JSONHandler.load(test_file)
        assert loaded_rest is not None
        assert loaded_rest.name == sample_restaurant.name
        assert loaded_rest.balance == sample_restaurant.balance
        assert len(loaded_events) == len(scheduler.scheduled_events)

        if os.path.exists(test_file):
            os.remove(test_file)

    def test_load_nonexistent_file(self):
        rest, events = JSONHandler.load("data/fantasma.json")
        assert rest is None
        assert events == []

class TestServices:
    def test_calculate_role_deficit(self, sample_restaurant):
        # 3 mesas -> target waiter: max(1, 3//2)=1, actual 1 -> déficit 0
        assert calculate_role_deficit(sample_restaurant, EmployeeRole.WAITER) == 0
        # target chef: max(1, 3//3)=1, actual 2 -> déficit -1 (sobra un chef)
        assert calculate_role_deficit(sample_restaurant, EmployeeRole.CHEF) == -1