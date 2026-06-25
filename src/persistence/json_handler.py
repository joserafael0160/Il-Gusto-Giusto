# src/persistence/json_handler.py
import json
import os
from datetime import datetime
from dataclasses import asdict
from typing import Tuple, List, Dict, Any, Optional
from src.models.restaurant import Restaurant, Employee, Table, Dish, Ingredient, EmployeeRole, ExperienceLevel
from src.models.events import Event

class JSONHandler:
    @staticmethod
    def save(restaurant: Restaurant, scheduler_events: List[Event], filepath: str) -> None:
        """Serializes current domain state cleanly to a target JSON file."""
        def json_serial(obj: Any) -> str:
            if isinstance(obj, datetime):
                return obj.isoformat()
            if hasattr(obj, 'value'):
                return obj.value
            raise TypeError(f"Type not serializable: {type(obj)}")

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

        applicants_serialized = []
        for cand in restaurant.applicants:
            applicants_serialized.append({
                "name": cand["name"],
                "role": getattr(cand["role"], 'value', cand["role"]),
                "experience": getattr(cand["experience"], 'value', cand["experience"]),
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
    def load(filepath: str) -> Tuple[Optional[Restaurant], List[Event]]:
        """Safely loads domain models from a JSON file, resolving custom Enums."""
        if not os.path.exists(filepath):
            return None, []
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except (json.JSONDecodeError, IOError):
            return None, []
        return JSONHandler._parse_data(data)

    @staticmethod
    def loads(json_str: str) -> Tuple[Optional[Restaurant], List[Event]]:
        """Loads domain models from a JSON string (useful for file upload)."""
        try:
            data = json.loads(json_str)
        except json.JSONDecodeError:
            return None, []
        return JSONHandler._parse_data(data)

    @staticmethod
    def _parse_data(data: Dict[str, Any]) -> Tuple[Optional[Restaurant], List[Event]]:
        """Internal parser for the loaded dictionary."""
        restaurant = Restaurant(name=data["name"], balance=data["balance"])
        restaurant.history = data.get("history", [])

        applicants_loaded = []
        for cand in data.get("applicants", []):
            applicants_loaded.append({
                "name": cand["name"],
                "role": EmployeeRole(cand["role"]),
                "experience": ExperienceLevel(cand["experience"]),
                "specialties": cand["specialties"],
                "daily_wage": cand["daily_wage"],
                "bio": cand["bio"]
            })
        restaurant.applicants = applicants_loaded

        for k, v in data["employees"].items():
            busy = datetime.fromisoformat(v["busy_until"]) if v.get("busy_until") else None
            restaurant.employees[k] = Employee(
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
            restaurant.tables[k] = Table(**v)

        for k, v in data["menu"].items():
            restaurant.menu[k] = Dish(**v)

        for k, v in data["ingredients"].items():
            restaurant.ingredients[k] = Ingredient(**v)

        events = []
        for e_data in data.get("scheduled_events", []):
            events.append(Event.from_dict(e_data))

        return restaurant, events