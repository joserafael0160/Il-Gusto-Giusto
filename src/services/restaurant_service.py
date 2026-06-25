# src/services/restaurant_service.py
import uuid
from typing import Dict, Tuple, List
from src.models.restaurant import Restaurant, Employee, EmployeeRole, ExperienceLevel, Dish, Ingredient

def calculate_role_deficit(restaurant: Restaurant, role: EmployeeRole) -> int:
    """Computes the difference between target headcount and current staffing."""
    current_count = len([e for e in restaurant.employees.values() if e.role == role])
    num_tables = len(restaurant.tables)

    if role == EmployeeRole.WAITER:
        target = max(1, num_tables // 2)
    else:  # CHEF
        target = max(1, num_tables // 3)

    return target - current_count

class RestaurantService:
    @staticmethod
    def hire_employee(restaurant: Restaurant, applicant: Dict) -> Tuple[bool, str]:
        """Transitions a job candidate to the active employee payroll, charging onboarding costs."""
        if restaurant.balance < applicant["daily_wage"]:
            return False, "Saldo insuficiente en el balance para costear la inducción diaria de este candidato."
        
        role_enum = applicant["role"] if isinstance(applicant["role"], EmployeeRole) else EmployeeRole(applicant["role"])
        exp_enum = applicant["experience"] if isinstance(applicant["experience"], ExperienceLevel) else ExperienceLevel(applicant["experience"])
        
        emp_id = f"emp_{uuid.uuid4().hex[:6]}"
        new_emp = Employee(
            id=emp_id,
            name=applicant["name"],
            role=role_enum,
            experience=exp_enum,
            specialties=applicant["specialties"],
            daily_wage=applicant["daily_wage"]
        )
        
        restaurant.employees[emp_id] = new_emp
        restaurant.add_transaction(-new_emp.daily_wage, f"Contratación de {new_emp.name}")
        restaurant.applicants = [a for a in restaurant.applicants if a["name"] != applicant["name"]]
        return True, f"¡{new_emp.name} se ha unido formalmente a tu equipo!"

    @staticmethod
    def fire_employee(restaurant: Restaurant, employee_id: str) -> Tuple[bool, str]:
        """Removes an active employee from the restaurant payroll."""
        employee = restaurant.employees.get(employee_id)
        if not employee:
            return False, "Empleado no encontrado."
        
        del restaurant.employees[employee_id]
        return True, f"{employee.name} ha sido retirado de la nómina activa."

    @staticmethod
    def purchase_ingredients(restaurant: Restaurant, purchases: Dict[str, float]) -> Tuple[bool, str]:
        """Executes transaction for supplier purchases and loads ingredients to pantry."""
        total_cost = 0.0
        ingredients_summary = []
        
        for ing_id, qty in purchases.items():
            if qty <= 0:
                continue
            ing = restaurant.ingredients.get(ing_id)
            if not ing:
                return False, f"Ingrediente {ing_id} no existe."
            total_cost += qty * ing.price_per_unit
            ingredients_summary.append(f"{qty} {ing.unit} de {ing.name}")
            
        if total_cost <= 0:
            return False, "Ningún ingrediente seleccionado."
            
        if restaurant.balance < total_cost:
            return False, "No cuentas con suficiente capital disponible en caja para realizar esta compra."
            
        for ing_id, qty in purchases.items():
            if qty > 0:
                restaurant.ingredients[ing_id].quantity += qty
                
        summary_text = "Compra de suministros: " + ", ".join(ingredients_summary)
        restaurant.add_transaction(-total_cost, summary_text)
        return True, f"Compra completada por un total de ${total_cost:.2f}."

    @staticmethod
    def publish_dish(restaurant: Restaurant, dish_data: Dict) -> Tuple[bool, str]:
        """Adds a newly created recipe to the operational menu."""
        if not dish_data.get("name"):
            return False, "El nombre de la receta es obligatorio."
        if not dish_data.get("ingredients"):
            return False, "La receta debe contener al menos un ingrediente."
        
        dish_id = f"dish_{uuid.uuid4().hex[:6]}"
        new_dish = Dish(
            id=dish_id,
            name=dish_data["name"],
            price=dish_data["price"],
            prep_time=dish_data["prep_time"],
            ingredients=dish_data["ingredients"],
            base_ingredients=dish_data.get("base_ingredients", []),
            category=dish_data["category"],
            requires_specialty=dish_data.get("requires_specialty")
        )
        restaurant.menu[dish_id] = new_dish
        return True, f"¡'{new_dish.name}' ha sido publicado exitosamente!"

    @staticmethod
    def update_dish(restaurant: Restaurant, dish_id: str, dish_data: Dict) -> Tuple[bool, str]:
        """Saves edited metrics and recipe adjustments for a specific menu item."""
        dish = restaurant.menu.get(dish_id)
        if not dish:
            return False, "Plato no encontrado."
        if not dish_data.get("name"):
            return False, "El nombre del plato no puede estar vacío."
        if not dish_data.get("ingredients"):
            return False, "Debes seleccionar al menos un ingrediente activo."
            
        dish.name = dish_data["name"]
        dish.price = dish_data["price"]
        dish.prep_time = dish_data["prep_time"]
        dish.category = dish_data["category"]
        dish.requires_specialty = dish_data.get("requires_specialty")
        dish.ingredients = dish_data["ingredients"]
        dish.base_ingredients = dish_data.get("base_ingredients", [])
        return True, f"Plato '{dish.name}' actualizado correctamente."

    @staticmethod
    def delete_dish(restaurant: Restaurant, dish_id: str) -> Tuple[bool, str]:
        """Permanently deletes a recipe from the active menu card."""
        dish = restaurant.menu.get(dish_id)
        if not dish:
            return False, "Plato no encontrado."
        del restaurant.menu[dish_id]
        return True, f"'{dish.name}' ha sido eliminado exitosamente."