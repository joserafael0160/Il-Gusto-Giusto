import sys
import os
import pytest
from pathlib import Path
from datetime import datetime, timedelta

root_path = Path(__file__).parent.parent
src_path = str(root_path / "src")
if src_path not in sys.path:
    sys.path.insert(0, src_path)

from src.models.restaurant import Restaurant, Order, Dish, Employee, Ingredient, Table, EmployeeRole, ExperienceLevel
from src.core.scheduler import EventScheduler
from src.persistence.json_handler import JSONHandler

@pytest.fixture
def sample_restaurant():
    r = Restaurant(name="Il Gusto Giusto Test", balance=2000.0)

    r.ingredients["pasta"] = Ingredient("pasta", "Pasta", 10.0, "kg", 2.0, 3.0)
    r.ingredients["truffle_oil"] = Ingredient("truffle_oil", "Aceite de Trufa", 5.0, "l", 0.5, 45.0)

    dish = Dish(
        id="d1",
        name="Truffle Pasta Test",
        price=28.0,
        prep_time=30,
        ingredients={"pasta": 0.15, "truffle_oil": 0.05},
        base_ingredients=["pasta"],
        category="truffle_specialty",
        requires_specialty="pasta"
    )
    r.menu["d1"] = dish

    chef = Employee(
        id="chef1",
        name="Chef Giovanni",
        role=EmployeeRole.CHEF,
        experience=ExperienceLevel.SENIOR,
        specialties=["pasta"],
        daily_wage=150.0,
        is_available=True
    )
    r.employees["chef1"] = chef

    table = Table(id="t1", number=1, capacity=4, is_occupied=False)
    r.tables["t1"] = table

    return r

@pytest.fixture
def scheduler(sample_restaurant):
    return EventScheduler(sample_restaurant)

def test_schedule_valid_order(scheduler, sample_restaurant):
    order = Order(id="ord1", table_id="t1", dishes={"d1": 1})
    success, msg, event = scheduler.schedule_order(order, datetime.now())

    assert success is True
    assert event.assigned_chef_id == "chef1"
    assert sample_restaurant.tables["t1"].is_occupied is True
    assert sample_restaurant.employees["chef1"].is_available is False

def test_schedule_collision(scheduler, sample_restaurant):
    order1 = Order(id="ord1", table_id="t1", dishes={"d1": 1})
    start = datetime.now()
    scheduler.schedule_order(order1, start)

    # El plato demora 30 min, agendar otra orden en la misma mesa 5 min después debe fallar
    order2 = Order(id="ord2", table_id="t1", dishes={"d1": 1})
    collision_start = start + timedelta(minutes=5)
    success, msg, _ = scheduler.schedule_order(order2, collision_start)

    assert success is False
    assert "ocupada" in msg or "mesa" in msg or "reservada" in msg

def test_cancel_releases_resources(scheduler, sample_restaurant):
    order = Order(id="ord_cancel", table_id="t1", dishes={"d1": 1})
    _, _, event = scheduler.schedule_order(order, datetime.now())

    assert sample_restaurant.tables["t1"].is_occupied is True

    success, _ = scheduler.cancel_event(event.id)
    assert success is True
    assert sample_restaurant.tables["t1"].is_occupied is False
    assert sample_restaurant.employees["chef1"].is_available is True

def test_missing_co_requirement(scheduler, sample_restaurant):
    # Agotamos el aceite de trufa para forzar violación de Co-requisito
    sample_restaurant.ingredients["truffle_oil"].quantity = 0.0

    order = Order(id="ord_fail", table_id="t1", dishes={"d1": 1})
    success, msg, _ = scheduler.schedule_order(order, datetime.now())

    assert success is False
    assert "trufa" in msg or "oil" in msg or "violada" in msg

def test_persistence_integrity(sample_restaurant, scheduler):
    test_file = "data/test_persistence_temp.json"
    order = Order(id="ord_persist", table_id="t1", dishes={"d1": 1})
    scheduler.schedule_order(order, datetime.now())

    JSONHandler.save_restaurant(sample_restaurant, scheduler.scheduled_events, test_file)
    loaded_rest, loaded_events = JSONHandler.load_restaurant(test_file)

    assert loaded_rest.name == sample_restaurant.name
    assert len(loaded_events) == len(scheduler.scheduled_events)
    assert loaded_events[0].order_id == "ord_persist"

    if os.path.exists(test_file):
        os.remove(test_file)