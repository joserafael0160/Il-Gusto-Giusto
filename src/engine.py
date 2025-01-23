from datetime import datetime, timedelta
from typing import List, Dict  
from .models import Event, Resource, Ingredient, Constraint

class PlanningEngine:
    def __init__(self):
        self.events: List[Event] = []
        self.resources: Dict[str, Resource] = {}
        self.ingredients: Dict[str, Ingredient] = {}
        self.constraints: List[Constraint] = []

    def check_overlap(self, start1, end1, start2, end2):
        return max(start1, start2) < min(end1, end2)

    def validate_event(self, new_event: Event):
        # 1. Validación de Conflictos de Tiempo y Recursos
        for existing in self.events:
            if self.check_overlap(new_event.start_time, new_event.end_time, existing.start_time, existing.end_time):
                common = set(new_event.resource_ids) & set(existing.resource_ids)
                if common:
                    raise ValueError(f"Recursos ocupados en este horario: {common}")

        # 2. Validación de Stock
        for ing_id, qty in new_event.ingredients_needed.items():
            if self.ingredients[ing_id].current_stock < qty:
                raise ValueError(f"Stock insuficiente de: {self.ingredients[ing_id].name}")

        # 3. Validación de Restricciones (Co-requisito y Exclusión)
        for c in self.constraints:
            if c.type == "co_requisite":
                if c.target_id in new_event.resource_ids:
                    if not all(rid in new_event.resource_ids for rid in c.related_ids):
                        raise ValueError(f"Falta requisito: {c.message}")
            
            if c.type == "exclusion":
                if c.target_id in new_event.resource_ids:
                    for rid in c.related_ids:
                        if rid in new_event.resource_ids:
                            raise ValueError(f"Conflicto de exclusión: {c.message}")

    def add_event(self, event: Event):
        self.validate_event(event)
        # Descontar inventario inmediatamente (Reserva lógica)
        for ing_id, qty in event.ingredients_needed.items():
            self.ingredients[ing_id].current_stock -= qty
        self.events.append(event)

    def find_next_slot(self, duration_mins: int, resource_ids: List[str], start_from: datetime):
        """Algoritmo 'Buscar Hueco' básico"""
        potential_start = start_from
        while potential_start < start_from + timedelta(days=1):
            potential_end = potential_start + timedelta(minutes=duration_mins)
            try:
                # Simulamos un evento para validar
                test_event = Event("test", "Test", potential_start, potential_end, resource_ids, {})
                self.validate_event(test_event)
                return potential_start
            except ValueError:
                potential_start += timedelta(minutes=15) # Saltos de 15 min
        return None