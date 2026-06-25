from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Any

@dataclass
class Event:
    id: str
    order_id: str
    table_id: str
    assigned_chef_id: str
    start_time: datetime
    end_time: datetime
    dishes: Dict[str, int] = field(default_factory=dict)                # dish_id -> cantidad pedida
    customized_removals: Dict[str, List[str]] = field(default_factory=dict)  # dish_id -> [ing_id omitidos]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "order_id": self.order_id,
            "table_id": self.table_id,
            "assigned_chef_id": self.assigned_chef_id,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat(),
            "dishes": self.dishes,
            "customized_removals": self.customized_removals
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Event":
        return cls(
            id=data["id"],
            order_id=data["order_id"],
            table_id=data["table_id"],
            assigned_chef_id=data["assigned_chef_id"],
            start_time=datetime.fromisoformat(data["start_time"]),
            end_time=datetime.fromisoformat(data["end_time"]),
            dishes=data.get("dishes", {}),
            customized_removals=data.get("customized_removals", {})
        )