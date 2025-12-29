import sys
import os
import pytest
from pathlib import Path
from datetime import datetime, timedelta

from src.persistence.json_handler import JSONHandler
# 1. Configuración robusta del path
# Esto asegura que 'src' sea la raíz para todas las importaciones
root_path = Path(__file__).parent.parent
src_path = str(root_path / "src")
if src_path not in sys.path:
    sys.path.insert(0, src_path)

# 2. Importaciones consistentes
from src.models.restaurant import Restaurant, Order, Dish, Employee, Ingredient, Table, EmployeeRole
from src.models.events import Event
from src.core.scheduler import EventScheduler

@pytest.fixture
def sample_restaurant():
    """Crea un restaurante básico con todos los requisitos para que los tests pasen"""
    r = Restaurant(name="Test Rest", balance=1000.0)
    
    # Ingredientes necesarios para evitar errores de Constraints
    r.ingredients["rice"] = Ingredient("rice", "Arroz", 10.0, "kg")
    r.ingredients["wasabi"] = Ingredient("wasabi", "Wasabi", 5.0, "kg")
    
    # Plato de Sushi
    dish = Dish(
        id="d1", 
        name="Sushi Test", 
        price=10.0, 
        prep_time=30,
        ingredients={"rice": 0.1, "wasabi": 0.01}, 
        base_ingredients=["rice"], 
        category="sushi",
        requires_specialty="sushi"
    )
    r.menu["d1"] = dish
    
    # Chef especialista
    chef = Employee(
        id="chef1", 
        name="Chef Test", 
        role=EmployeeRole.CHEF, 
        specialties=["sushi"],
        is_available=True
    )
    r.employees["chef1"] = chef
    
    # Mesa disponible
    table = Table(id="t1", number=1, capacity=4, is_occupied=False)
    r.tables["t1"] = table
    
    return r

@pytest.fixture
def scheduler(sample_restaurant):
    return EventScheduler(sample_restaurant)

def test_schedule_valid_order(scheduler, sample_restaurant):
    """Prueba que una orden válida se planifica correctamente"""
    order = Order(
        id="ord1",
        table_id="t1",
        dishes={"d1": 1}
    )
    
    start_time = datetime.now()
    success, msg, event = scheduler.schedule_order(order, start_time)
    
    # Verificación
    assert success is True, f"Fallo en scheduler: {msg}"
    # Si isinstance falla por temas de importación, esto al menos verificará el tipo por nombre
    assert type(event).__name__ == "Event"
    assert event.assigned_chef_id == "chef1"
    
    # Verificar que los recursos se marcaron como ocupados
    assert sample_restaurant.tables["t1"].is_occupied is True
    assert sample_restaurant.employees["chef1"].is_available is False

def test_schedule_order_no_chef(scheduler, sample_restaurant):
    """Prueba fallo cuando el chef no tiene la especialidad"""
    sample_restaurant.employees["chef1"].specialties = ["pizza"] # No sabe hacer sushi
    
    order = Order(id="ord2", table_id="t1", dishes={"d1": 1})
    success, msg, event = scheduler.schedule_order(order, datetime.now())
    
    assert success is False
    assert "chef" in msg.lower() or "disponible" in msg.lower()

def test_find_next_slot(scheduler, sample_restaurant):
    """Prueba la búsqueda de huecos"""
    order = Order(id="ord3", table_id="t1", dishes={"d1": 1})
    slot = scheduler.find_next_available_slot(order)
    assert isinstance(slot, datetime)

def test_schedule_collision(scheduler, sample_restaurant):
    """Verifica que no se puedan solapar dos eventos en el mismo recurso"""
    order1 = Order(id="ord1", table_id="t1", dishes={"d1": 1})
    start_time = datetime.now()
    
    # Agendamos la primera orden con éxito
    scheduler.schedule_order(order1, start_time)
    
    # Intentamos agendar otra orden en la misma mesa 5 minutos después 
    # (El sushi tarda 30 min, así que debería fallar)
    order2 = Order(id="ord2", table_id="t1", dishes={"d1": 1})
    start_collision = start_time + timedelta(minutes=5)
    
    success, msg, event = scheduler.schedule_order(order2, start_collision)
    
    assert success is False
    assert "reservada" in msg.lower() or "ocupada" in msg.lower()
def test_cancel_event_releases_resources(scheduler, sample_restaurant):
    """Verifica que al cancelar un evento los recursos queden libres de nuevo"""
    order = Order(id="ord_cancel", table_id="t1", dishes={"d1": 1})
    _, _, event = scheduler.schedule_order(order, datetime.now())
    
    # Verificamos que esté ocupado
    assert sample_restaurant.tables["t1"].is_occupied is True
    
    # Cancelamos
    success, msg = scheduler.cancel_event(event.id)
    
    assert success is True
    assert sample_restaurant.tables["t1"].is_occupied is False
    assert sample_restaurant.employees["chef1"].is_available is True
def test_missing_co_requirement(scheduler, sample_restaurant):
    """Verifica que falle si falta un ingrediente co-requisito (Wasabi)"""
    # Vaciamos el wasabi del inventario
    sample_restaurant.ingredients["wasabi"].quantity = 0
    
    order = Order(id="ord_no_wasabi", table_id="t1", dishes={"d1": 1})
    success, msg, event = scheduler.schedule_order(order, datetime.now())
    
    assert success is False
    assert "wasabi" in msg.lower()
def test_smart_search_future_slot(scheduler, sample_restaurant):
    """Verifica que el buscador de huecos encuentre tiempo después de un evento activo"""
    # 1. Agendamos una orden que dura 30 min empezando ahora
    now = datetime.now()
    order1 = Order(id="ord_busy", table_id="t1", dishes={"d1": 1})
    scheduler.schedule_order(order1, now)
    
    # 2. Buscamos hueco para otra orden que necesita los mismos recursos
    order2 = Order(id="ord_waiting", table_id="t1", dishes={"d1": 1})
    next_slot = scheduler.find_next_available_slot(order2)
    
    # 3. El hueco debería ser al menos 30 minutos después de 'now'
    assert next_slot >= now + timedelta(minutes=30)

def test_inventory_depletion(scheduler, sample_restaurant):
    """Verifica que el inventario disminuya y bloquee órdenes cuando se agota"""
    # El plato usa 0.1 de arroz. Tenemos 10.0. 
    # Si bajamos el arroz a 0.05, no debería poder hacer ni un plato.
    sample_restaurant.ingredients["rice"].quantity = 0.05
    
    order = Order(id="ord_no_rice", table_id="t1", dishes={"d1": 1})
    success, msg, _ = scheduler.schedule_order(order, datetime.now())
    
    assert success is False
    assert "arroz" in msg.lower() or "ingredientes" in msg.lower()

def test_persistence_integrity(sample_restaurant, scheduler):
    """Verifica que el estado se mantenga idéntico tras guardar y cargar"""
    test_file = "data/test_persistence.json"
    
    # 1. Agendamos algo para tener eventos
    order = Order(id="ord_persist", table_id="t1", dishes={"d1": 1})
    scheduler.schedule_order(order, datetime.now())
    
    # 2. Guardamos
    JSONHandler.save_restaurant(sample_restaurant, scheduler.scheduled_events, test_file)
    
    # 3. Cargamos en una instancia nueva
    loaded_rest, loaded_events = JSONHandler.load_restaurant(test_file)
    
    # 4. Comprobamos datos clave
    assert loaded_rest.name == sample_restaurant.name
    assert len(loaded_events) == len(scheduler.scheduled_events)
    assert loaded_events[0].order_id == "ord_persist"
    
    # Limpieza
    if os.path.exists(test_file):
        os.remove(test_file)