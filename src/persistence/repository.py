# src/persistence/repository.py
from typing import Tuple, List, Protocol
from src.models.restaurant import Restaurant
from src.models.events import Event

class StateRepository(Protocol):
    """Abstract interface defining required storage capabilities."""
    def save(self, restaurant: Restaurant, events: List[Event], filepath: str) -> None:
        """Saves current restaurant and events data to storage."""
        ...

    def load(self, filepath: str) -> Tuple[Restaurant, List[Event]]:
        """Loads restaurant and events data from storage."""
        ...