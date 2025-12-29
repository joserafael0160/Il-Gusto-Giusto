from typing import List, Tuple, Dict
from src.models.restaurant import Dish

class ConstraintValidator:
    """
    Gestiona las reglas de negocio personalizadas:
    1. Co-requisitos (Si pides A, necesitas B)
    2. Exclusión Mutua (No puedes pedir A y B juntos)
    """
    def __init__(self):
        self.co_requirements = []
        self.mutual_exclusions = []
        # Inicializamos reglas por defecto (esto podría venir de config)
        self._init_default_rules()

    def _init_default_rules(self):
        # Regla 1: Sushi requiere Chef especialista y Wasabi
        self.add_co_requirement(
            "Sushi Standard",
            lambda dish: dish.category == "sushi",
            "wasabi",
            "Los platos de Sushi requieren Wasabi fresco."
        )
        
        # Regla 2: Exclusión Sashimi vs Tempura (Ejemplo de tu idea)
        self.add_mutual_exclusion(
            "Choque Térmico",
            "sashimi",
            "tempura",
            "No se recomienda servir Sashimi (crudo) y Tempura (frito) simultáneamente por tiempos de servicio."
        )

    def add_co_requirement(self, name, trigger_condition, required_item_id, message):
        self.co_requirements.append({
            "name": name,
            "condition": trigger_condition,
            "required_item": required_item_id,
            "message": message
        })

    def add_mutual_exclusion(self, name, category_a, category_b, reason):
        self.mutual_exclusions.append({
            "name": name,
            "cat_a": category_a,
            "cat_b": category_b,
            "reason": reason
        })

    def validate(self, dishes: List[Dish], available_ingredients: Dict) -> Tuple[bool, str]:
        """
        Valida una lista de platos contra todas las reglas definidas.
        Retorna: (EsValido, MensajeError)
        """
        dish_categories = [d.category for d in dishes]
        
        # 1. Verificar Exclusión Mutua
        for rule in self.mutual_exclusions:
            if rule["cat_a"] in dish_categories and rule["cat_b"] in dish_categories:
                return False, f"Restricción '{rule['name']}': {rule['reason']}"

        # 2. Verificar Co-requisitos (Ingredientes especiales)
        for rule in self.co_requirements:
            for dish in dishes:
                if rule["condition"](dish):
                    req_item = rule["required_item"]
                    # Verificamos si existe el ingrediente en el inventario
                    if req_item not in available_ingredients or available_ingredients[req_item].quantity <= 0:
                        return False, f"Restricción '{rule['name']}': {rule['message']} (Falta {req_item})"
        
        return True, "Validación exitosa"