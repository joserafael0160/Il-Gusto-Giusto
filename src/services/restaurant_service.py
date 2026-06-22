from src.models.restaurant import Restaurant, EmployeeRole

def calculate_role_deficit(restaurant: Restaurant, role: EmployeeRole) -> int:
    """
    Evalúa la cantidad actual del rol comparada con un modelo balanceado del restaurante:
    Deseable: 1 Camarero por cada 2 mesas, 1 Chef por cada 3 mesas.
    Retorna el déficit (positivo si faltan empleados).
    """
    current_count = len([e for e in restaurant.employees.values() if e.role == role])
    num_tables = len(restaurant.tables)

    if role == EmployeeRole.WAITER:
        target = max(1, num_tables // 2)
    else:  # CHEF
        target = max(1, num_tables // 3)

    return target - current_count