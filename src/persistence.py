import json
from .models import Resource, Ingredient, Constraint

def load_from_json(path: str):
    """Carga el estado del restaurante desde un archivo JSON."""
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    res_dict = {}
    ing_dict = {}
    cons_list = []

    # Cargar Recursos (Empleados, Equipos, Mesas)
    # Usamos .get() por si alguna lista no existe en el JSON
    for cat in ['employees', 'equipment', 'tables']:
        for item in data['resources'].get(cat, []):
            res_dict[item['id']] = Resource(item['id'], item['name'], cat, item)

    # Cargar Ingredientes
    for item in data['resources'].get('ingredients', []):
        ing_dict[item['id']] = Ingredient(
            item['id'], item['name'], item['current_stock'], 
            item['unit'], item['min_stock'], item['cost_per_unit']
        )

    # Cargar Restricciones
    for item in data.get('constraints', []):
        target = item.get('event_type') or item.get('target_id') or item.get('resource1')
        related = item.get('required_resources') or [item.get('resource2')]
        msg = item.get('description') or item.get('reason') or "Restricción de operación"
        cons_list.append(Constraint(item['type'], target, related, msg))

    return res_dict, ing_dict, cons_list

def save_to_json(path: str, engine):
    """Guarda el estado actual del motor en el archivo JSON."""
    # Esta función servirá para que tus cambios no se pierdan al cerrar
    data = {
        "resources": {
            "employees": [r.attributes for r in engine.resources.values() if r.type == 'employees'],
            "equipment": [r.attributes for r in engine.resources.values() if r.type == 'equipment'],
            "tables": [r.attributes for r in engine.resources.values() if r.type == 'tables'],
            "ingredients": [
                {
                    "id": i.id, "name": i.name, "current_stock": i.current_stock,
                    "unit": i.unit, "min_stock": i.min_stock, "cost_per_unit": i.cost_per_unit
                } for i in engine.ingredients.values()
            ]
        },
        "constraints": [
            {
                "type": c.type, "target_id": c.target_id, 
                "related_ids": c.related_ids, "message": c.message
            } for c in engine.constraints
        ],
        "events": [
            {
                "id": e.id, "name": e.name, 
                "start": e.start_time.isoformat(), 
                "end": e.end_time.isoformat(),
                "resources": e.resource_ids,
                "ingredients": e.ingredients_needed
            } for e in engine.events
        ]
    }
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)