from dataclasses import dataclass, field
from typing import List, Dict, Optional
from datetime import datetime
from enum import Enum

class EmployeeRole(str, Enum):
    CHEF = "chef"
    WAITER = "waiter"
    MANAGER = "manager"

@dataclass
class Ingredient:
    id: str
    name: str
    quantity: float
    unit: str
    min_quantity: float = 0.0
    price_per_unit: float = 0.0

@dataclass
class Dish:
    id: str
    name: str
    price: float
    prep_time: int  # en minutos
    ingredients: Dict[str, float]  # {id_ingrediente: cantidad}
    base_ingredients: List[str]
    category: str
    requires_specialty: Optional[str] = None

@dataclass
class Employee:
    id: str
    name: str
    role: EmployeeRole
    specialties: List[str] = field(default_factory=list)
    is_available: bool = True
    busy_until: Optional[datetime] = None

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
    dishes: Dict[str, int]  # {id_plato: cantidad}
    modifications: List[str] = field(default_factory=list) # "Sin cebolla", etc.
    total_price: float = 0.0
    status: str = "pending"

    def calculate_total_price(self, menu: Dict[str, Dish]) -> float:
        total = 0.0
        for dish_id, qty in self.dishes.items():
            if dish_id in menu:
                total += menu[dish_id].price * qty
        return total

@dataclass
class Restaurant:
    name: str
    balance: float
    menu: Dict[str, Dish] = field(default_factory=dict)
    ingredients: Dict[str, Ingredient] = field(default_factory=dict)
    employees: Dict[str, Employee] = field(default_factory=dict)
    tables: Dict[str, Table] = field(default_factory=dict)
    active_orders: List[Order] = field(default_factory=list)
    history: List[Order] = field(default_factory=list)

    def add_order(self, order: Order):
        self.active_orders.append(order)
        self.history.append(order)