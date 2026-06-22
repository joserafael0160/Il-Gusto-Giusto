import os
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any

class EmployeeRole(Enum):
    CHEF = "chef"
    WAITER = "waiter"

class ExperienceLevel(Enum):
    JUNIOR = "junior"
    SENIOR = "senior"

@dataclass
class Employee:
    id: str
    name: str
    role: EmployeeRole
    experience: ExperienceLevel
    specialties: List[str]
    daily_wage: float
    is_available: bool = True
    busy_until: Optional[datetime] = None

@dataclass
class Ingredient:
    id: str
    name: str
    quantity: float
    unit: str
    min_quantity: float
    price_per_unit: float

@dataclass
class Dish:
    id: str
    name: str
    price: float
    prep_time: int  # en minutos
    ingredients: Dict[str, float]  # ing_id -> cantidad requerida
    base_ingredients: List[str]    # ingredientes indispensables (no se pueden quitar)
    category: str                  # ej: "pizza", "seafood", "truffle_specialty"
    requires_specialty: Optional[str] = None

@dataclass
class Table:
    id: str
    number: int
    capacity: int
    is_occupied: bool = False

@dataclass
class Order:
    id: str
    table_id: str
    dishes: Dict[str, int]  # dish_id -> cantidad
    # Almacena ingredientes opcionales omitidos: dish_id -> [lista de ing_id omitidos]
    customized_removals: Dict[str, List[str]] = field(default_factory=dict)

class Restaurant:
    def __init__(self, name: str, balance: float):
        self.name = name
        self.balance = balance
        self.employees: Dict[str, Employee] = {}
        self.tables: Dict[str, Table] = {}
        self.menu: Dict[str, Dish] = {}
        self.ingredients: Dict[str, Ingredient] = {}
        self.history: List[Dict[str, Any]] = []  # Historial transaccional
        self.active_orders: List[Order] = []

        self.add_transaction(balance, "Capital Inicial de Apertura")

    def add_transaction(self, amount: float, description: str):
        self.balance += amount
        self.history.append({
            "timestamp": datetime.now().isoformat(),
            "amount": amount,
            "description": description,
            "balance_after": self.balance
        })