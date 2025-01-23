from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict, Optional

@dataclass
class Resource:
    id: str
    name: str
    type: str  # employee, equipment, table
    attributes: Dict = field(default_factory=dict)

@dataclass
class Ingredient:
    id: str
    name: str
    current_stock: float
    unit: str
    min_stock: float
    cost_per_unit: float

@dataclass
class Event:
    id: str
    name: str
    start_time: datetime
    end_time: datetime
    resource_ids: List[str]
    ingredients_needed: Dict[str, float]  # {ing_id: quantity}

@dataclass
class Constraint:
    type: str  # co_requisite, exclusion
    target_id: str
    related_ids: List[str]
    message: str