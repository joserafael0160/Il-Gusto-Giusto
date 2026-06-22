import json
import os
from datetime import datetime
from dataclasses import asdict
from src.models.restaurant import Restaurant, Employee, Table, Dish, Ingredient, Order, EmployeeRole, ExperienceLevel
from src.models.events import Event

class JSONHandler:
    @staticmethod
    def save_restaurant(restaurant: Restaurant, scheduler_events: list, filepath: str):
        def json_serial(obj):
            if isinstance(obj, datetime):
                return obj.isoformat()
            raise TypeError(f"Tipo no serializable: {type(obj)}")

        # Empleados
        employees_serialized = {}
        for k, v in restaurant.employees.items():
            employees_serialized[k] = {
                "id": v.id,
                "name": v.name,
                "role": v.role.value,
                "experience": v.experience.value,
                "specialties": v.specialties,
                "daily_wage": v.daily_wage,
                "is_available": v.is_available,
                "busy_until": v.busy_until.isoformat() if v.busy_until else None
            }

        # Candidatos: convertir enums a cadenas manualmente
        applicants_serialized = []
        for cand in restaurant.applicants:
            applicants_serialized.append({
                "name": cand["name"],
                "role": cand["role"].value,          # ← cadena
                "experience": cand["experience"].value,  # ← cadena
                "specialties": cand["specialties"],
                "daily_wage": cand["daily_wage"],
                "bio": cand["bio"]
            })

        data = {
            "name": restaurant.name,
            "balance": restaurant.balance,
            "employees": employees_serialized,
            "tables": {k: asdict(v) for k, v in restaurant.tables.items()},
            "menu": {k: asdict(v) for k, v in restaurant.menu.items()},
            "ingredients": {k: asdict(v) for k, v in restaurant.ingredients.items()},
            "history": restaurant.history,
            "applicants": applicants_serialized,
            "scheduled_events": [e.to_dict() for e in scheduler_events]
        }

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, default=json_serial, indent=4, ensure_ascii=False)

    @staticmethod
    def load_restaurant(filepath: str):
        if not os.path.exists(filepath):
            return None, []

        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            return None, []

        rest = Restaurant(name=data["name"], balance=data["balance"])
        rest.history = data.get("history", [])

        # Cargar applicants convirtiendo las cadenas a enums
        applicants_loaded = []
        for cand in data.get("applicants", []):
            applicants_loaded.append({
                "name": cand["name"],
                "role": EmployeeRole(cand["role"]),           # cadena -> enum
                "experience": ExperienceLevel(cand["experience"]),  # cadena -> enum
                "specialties": cand["specialties"],
                "daily_wage": cand["daily_wage"],
                "bio": cand["bio"]
            })
        rest.applicants = applicants_loaded

        for k, v in data["employees"].items():
            busy = datetime.fromisoformat(v["busy_until"]) if v.get("busy_until") else None
            rest.employees[k] = Employee(
                id=v["id"],
                name=v["name"],
                role=EmployeeRole(v["role"]),
                experience=ExperienceLevel(v["experience"]),
                specialties=v["specialties"],
                daily_wage=v["daily_wage"],
                is_available=v["is_available"],
                busy_until=busy
            )

        for k, v in data["tables"].items():
            rest.tables[k] = Table(**v)

        for k, v in data["menu"].items():
            rest.menu[k] = Dish(**v)

        for k, v in data["ingredients"].items():
            rest.ingredients[k] = Ingredient(**v)

        events = []
        for e_data in data.get("scheduled_events", []):
            events.append(Event.from_dict(e_data))

        return rest, events