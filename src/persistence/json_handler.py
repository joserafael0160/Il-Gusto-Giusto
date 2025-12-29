import json
import os
from datetime import datetime
from dataclasses import asdict
from src.models.restaurant import Restaurant, Employee, Table, Dish, Ingredient, Order, EmployeeRole
from src.models.events import Event

class JSONHandler:
    @staticmethod
    def save_restaurant(restaurant: Restaurant, scheduler_events: list, filepath: str):
        def json_serial(obj):
            if isinstance(obj, datetime):
                return obj.isoformat()
            if isinstance(obj, EmployeeRole):
                return obj.value
            raise TypeError(f"Type {type(obj)} not serializable")

        data = {
            "name": restaurant.name,
            "balance": restaurant.balance,
            "employees": {k: asdict(v) for k, v in restaurant.employees.items()},
            "tables": {k: asdict(v) for k, v in restaurant.tables.items()},
            "menu": {k: asdict(v) for k, v in restaurant.menu.items()},
            "ingredients": {k: asdict(v) for k, v in restaurant.ingredients.items()},
            "active_orders": [asdict(o) for o in restaurant.active_orders],
            "history": [asdict(o) for o in restaurant.history],
            "scheduled_events": [asdict(e) for e in scheduler_events]
        }

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, default=json_serial, indent=4)

    @staticmethod
    def load_restaurant(filepath: str):
        if not os.path.exists(filepath):
            return None, []

        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)

        rest = Restaurant(name=data["name"], balance=data["balance"])
        
        # Cargar diccionarios básicos
        for k, v in data["employees"].items():
            busy = datetime.fromisoformat(v["busy_until"]) if v.get("busy_until") else None
            rest.employees[k] = Employee(
                id=v["id"], name=v["name"], role=EmployeeRole(v["role"]),
                specialties=v["specialties"], is_available=v["is_available"], busy_until=busy
            )
        
        for k, v in data["tables"].items():
            rest.tables[k] = Table(id=v["id"], number=v["number"], capacity=v["capacity"], is_occupied=v["is_occupied"])
            
        for k, v in data["menu"].items():
            rest.menu[k] = Dish(**v)
            
        for k, v in data["ingredients"].items():
            rest.ingredients[k] = Ingredient(**v)

        # Reconstruir Eventos
        events = []
        for e_data in data.get("scheduled_events", []):
            events.append(Event.from_dict(e_data))
            
        return rest, events