from abc import ABC, abstractmethod
from typing import List, Dict, Tuple
from src.models.restaurant import Dish, Ingredient

class Constraint(ABC):
    @abstractmethod
    def validate(self, dishes: List[Dish], ingredients: Dict[str, Ingredient]) -> Tuple[bool, str]:
        """Retorna (EsValido, Mensaje)"""
        pass

class CoRequirementConstraint(Constraint):
    """
    Regla de Co-requisito (Inclusión):
    Si se detecta un plato de cierta categoría, se exige que exista un ingrediente complementario en stock.
    """
    def __init__(self, name: str, trigger_category: str, required_ingredient_id: str, message: str):
        self.name = name
        self.trigger_category = trigger_category
        self.required_ingredient_id = required_ingredient_id
        self.message = message

    def validate(self, dishes: List[Dish], ingredients: Dict[str, Ingredient]) -> Tuple[bool, str]:
        for dish in dishes:
            if dish.category == self.trigger_category:
                ing = ingredients.get(self.required_ingredient_id)
                if not ing or ing.quantity <= 0:
                    return False, f"Regla violada ({self.name}): {self.message}"
        return True, ""

class MutualExclusionConstraint(Constraint):
    """
    Regla de Exclusión Mutua:
    No se permite que convivan ciertas categorías de platos en un mismo pedido.
    """
    def __init__(self, name: str, category_a: str, category_b: str, message: str):
        self.name = name
        self.category_a = category_a
        self.category_b = category_b
        self.message = message

    def validate(self, dishes: List[Dish], ingredients: Dict[str, Ingredient]) -> Tuple[bool, str]:
        categories = {dish.category for dish in dishes}
        if self.category_a in categories and self.category_b in categories:
            return False, f"Regla violada ({self.name}): {self.message}"
        return True, ""

class ConstraintValidator:
    def __init__(self):
        self.constraints: List[Constraint] = []
        self._init_default_rules()

    def _init_default_rules(self):
        # 1. Exclusión Mutua: Tradición italiana (No mezclar mariscos con quesos pesados)
        self.constraints.append(
            MutualExclusionConstraint(
                name="Tradición Italiana (Mar & Queso)",
                category_a="seafood",
                category_b="cheese_heavy",
                message="No se permite ordenar mariscos y platos con base láctea pesada (Gorgonzola/Cacio) en el mismo pedido por etiqueta culinaria."
            )
        )
        # 2. Co-requisito: Los platos con trufa requieren Aceite de Trufa en el stock
        self.constraints.append(
            CoRequirementConstraint(
                name="Soporte de Trufa",
                trigger_category="truffle_specialty",
                required_ingredient_id="truffle_oil",
                message="Los platos de especialidad con Trufa requieren que haya Aceite de Trufa en la despensa."
            )
        )

    def validate(self, dishes: List[Dish], ingredients: Dict[str, Ingredient]) -> Tuple[bool, str]:
        for constraint in self.constraints:
            valid, message = constraint.validate(dishes, ingredients)
            if not valid:
                return False, message
        return True, "Validación exitosa"