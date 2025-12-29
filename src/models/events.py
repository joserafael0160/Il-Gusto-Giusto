from dataclasses import dataclass, field
from datetime import datetime
from typing import List

@dataclass
class Event:
    id: str
    order_id: str
    table_id: str
    assigned_chef_id: str
    start_time: datetime
    end_time: datetime
    resource_ids: List[str] = field(default_factory=list) # Lista de IDs bloqueados

    def to_dict(self):
        return {
            "id": self.id,
            "order_id": self.order_id,
            "table_id": self.table_id,
            "assigned_chef_id": self.assigned_chef_id,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat(),
            "resource_ids": [self.table_id, self.assigned_chef_id]
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            id=data["id"],
            order_id=data["order_id"],
            table_id=data["table_id"],
            assigned_chef_id=data["assigned_chef_id"],
            start_time=datetime.fromisoformat(data["start_time"]),
            end_time=datetime.fromisoformat(data["end_time"]),
            resource_ids=data.get("resource_ids", [])
        )