# Ideas del proyecto
nombre del proyecto: Dragón del sabor
Objetivo: Sistema de gestion de restaurantes (enfocado a un restaurante japones)
tecnologias: python, pytest, streamlit
buenas practicas: modularizacion, solid, escribir variables en ingles, buenas practicas de python
## Fase 1
Inicia el restaurante con unos empleados preestablecidos, unos ingredientes, unas mesas y un dinero por defecto, luego hay un menu por defecto, estas comidas requieren ingredientes y un chef que la haga, mientras un chef hace una comida no puede estar haciendo la comida de otra mesa, cada comida lleva un tiempo de preparacion, este tiempo se ve que el cocinero estara ocupado y por tanto no puede estar haciendo otra, ahora el calculo no es paso a paso, sino, cada comida del menu tiene un tiempo de hacerse, y unos recursos (ingredientes) lo que se hace es sumarse el tiempo de toda la comida que pidio la misma mesa, luego de ese tiempo el chef estara disponible, sin embargo capaz un segundo chef si puede estar disponible mientras, una vez se acabe un ingrediente de un plato, el plato no se puede preparar, luego los clientes pueden quitar ingredientes, lo que no baja el precio del plato, sin embargo si puede hacer que un plato se que no tenia ese ingrediente se habilite, sin embargo los platos tienen unos ingredientes base que no se pueden quitar
## Fase 2
la idea de lo anterior es que eso pase en una pestaña como principal. Ahora Crear una pestaña de menú, donde el usuario(el administrador del restaurante) puede añadir platos nuevos y eliminar otros, o editarlos, ya sea precio, ingredientes, imagen y así y crear un menú nuevo
## Fase 3
Una tercera pestaña que sea como para mostrar los empleados que trabajan en el restaurante, nombre, experiencia, cargo, foto, y arriba a la derecha o donde sea una cosita de ofertas de empleo donde cuando toques te salga las personas que quieren trabajar en el restaurante, puedes filtrar por cargo y experiencia, pero además por defecto el sistema te pone de primero al que más el sistema considera que necesita tu restaurante, por ejemplo si tienes 10 chef senior, y 1 dependiente, el lugar de ofertas de empleo a los primeros que te va a sacar será a los dependientes, aunque sea un dependiente novato te lo pondrá por encima de un chef senior ya que a tu restaurante no le hace falta mas chefs
## Fase 4
Una cuarta pestaña que sea como una tienda en la cual se puedan comprar los ingredientes de las comidas y así. En este punto habría que crear un sistema de alertas para que cuando el restaurante se esté quedando sin ingredientes para las comidas, le advierta al usuario para que vaya a comprar, sino se le bloqueará la comida especifica a los clientes como en la fase 1
# Fase 5
Una quinta pestaña que sea como el sistema de contabilidad del restaurante, la idea es que tú inicias con un dinero para el restaurante y tal pero a medida que avanza tu restaurante, contrata trabajadores, compra ingredientes etc, ese dinero sube (vendiendo platos) o baja, ahora el punto de si con el precio de tus platos el restaurante es rentable o no lo dice esta pestaña, así como graficas del dinero a lo largo del tiempo del restaurante. 













explicacion ia: 
mira tengo que hacer un proyecto de programacion, mi carrera es ciencias de la computacion y el proyecto que nos pidieron es el siguiente, 

# Planificador Inteligente de Eventos



El proyecto consiste en construir una aplicación de software completa para planificar **eventos** que consumen **recursos** de un inventario limitado. Dado que los eventos tienen una duración específica en el tiempo (un inicio y un fin), el reto principal del proyecto es garantizar que no existan conflictos ni colisiones en la asignación de recursos. Por lo tanto, manejar las nociones de operaciones con intervalos de tiempo será una habilidad central para el éxito. Te enfrentarás a uno de los problemas más comunes y cruciales en el mundo real: la gestión de la disponibilidad y la resolución de conflictos.



El objetivo principal es desarrollar un motor de planificación inteligente que garantice dos cosas en todo momento:



1. Que los recursos no se asignen a más de un evento a la vez.

2. Que se respeten un conjunto de reglas y **restricciones** personalizadas que tú mismo definirás.



Tu misión se divide en dos fases clave: una de diseño creativo y otra de implementación técnica.



## Diseño



Antes de escribir una sola línea de código, tu primera tarea es la de un arquitecto de software: elegirás un dominio del mundo real y modelarás sus reglas. ¿Gestionarás un hospital, una productora de cine, un laboratorio de investigación, un centro deportivo? La elección es tuya.



Dentro del dominio que elijas, deberás definir los siguientes componentes fundamentales:



### Eventos



Son las actividades principales que necesitan ser planificadas en el tiempo y que requieren recursos para poder llevarse a cabo.



- **Ejemplos:** "Cirugía de Corazón Abierto", "Rodaje de la Escena 5", "Experimento de Fusión Fría", "Partido Final del Torneo".



### Recursos



Es el inventario de todos los activos finitos, compartidos y reutilizables que tus eventos necesitan para ocurrir. Puedes modelar tus recursos como simples identificadores (nombres) o, si tu dominio lo requiere, añadirles atributos específicos (ej: capacidad, marca, modelo) para crear restricciones más interesantes.



- **Ejemplos:** "Quirófano 3", "Dr. Martínez (Cardiólogo)", "Cámara RED Epic-W", "Técnico de Sonido", "Microscopio Electrónico", "Pista Central".



### c. Restricciones entre Recursos



Esta es la parte más creativa y el verdadero núcleo de la lógica de tu proyecto. Debes modelar un conjunto de reglas que dicten cómo los recursos pueden (o no pueden) ser combinados. Estas restricciones le darán una personalidad única a tu aplicación.



Debes implementar al menos dos tipos de restricciones:



1. **Restricción de Co-requisito (Inclusión):** Un recurso siempre requiere de otro recurso complementario para ser utilizado en un evento.

    - _Ejemplo en una productora de cine:_ Una "Cámara RED" siempre debe ser asignada junto con un "Técnico de Cámara Certificado".

    - _Ejemplo en un hospital:_ Una "Cirugía Robótica" siempre requiere la asignación de la "Consola Da Vinci" y un "Cirujano Certificado en Da Vinci".

2. **Restricción de Exclusión Mutua:** Si un evento utiliza un recurso de un tipo, tiene prohibido utilizar otro recurso de otro tipo en el mismo evento.

    - _Ejemplo en un laboratorio:_ Un "Experimento Químico" no puede usar el "Mechero Bunsen" al mismo tiempo que el "Contenedor de Éter" por razones de seguridad.

    - _Ejemplo en un estudio de grabación:_ Una sesión en la "Sala de Grabación A" no puede usar el "Micrófono de Cinta (Ribbon)", que es extremadamente sensible, si también se ha reservado la "Batería Acústica".



_Nota sobre la implementación:_ Se espera que la lógica de validación de tus restricciones personalizadas forme parte del código de tu aplicación, aunque de forma opcional puede ser configurable por el usuario. Asegúrate de documentar y explicar muy bien estas reglas en tu archivo `README.md`.



## Implementación



Una vez diseñado tu dominio, el reto técnico es escribir el código que gestione el calendario de eventos, el estado del inventario de recursos y la validación de todas las reglas. Tu aplicación debe ser robusta y manejar adecuadamente los errores. Si un usuario introduce datos incorrectos (ej. una fecha mal formada) o una operación no se puede realizar, el programa no debe fallar, sino mostrar un mensaje de error claro y descriptivo.



### Operaciones y Lógica Requeridas



#### Planificar un Nuevo Evento



Esta será la operación central de tu programa. El usuario propondrá un evento, especificando los recursos que necesita y el intervalo de tiempo deseado. El sistema debe verificar **automáticamente** dos condiciones críticas antes de confirmar la planificación:



1. **Conflictos de Recursos:** Que ninguno de los recursos solicitados esté ya asignado a otro evento en ese mismo horario.

2. **Violación de Restricciones:** Que la combinación de recursos solicitada no viole ninguna de las reglas de co-requisito o exclusión que definiste en tu dominio.



#### Búsqueda Automática de Horarios ("Buscar Hueco")



Debes implementar una función inteligente que, dado un evento y los recursos que necesita, sea capaz de analizar el calendario y sugerir el **próximo intervalo de tiempo disponible** donde se pueda realizar sin conflictos ni violaciones de restricciones.



#### Interfaz de Usuario



La interacción con tu aplicación puede ser a través de una **interfaz de consola (CLI)** o una **interfaz gráfica (GUI) básica**. Independientemente de la opción, debe permitir al usuario realizar las siguientes acciones:



- **Listar** todos los eventos planificados.

- **Agregar** un nuevo evento, invocando toda la lógica de validación.

- **Eliminar** un evento existente, liberando sus recursos para que queden disponibles.

- **Ver Detalles** de un evento específico (qué recursos usa, a qué hora) o de un recurso (cuál es su agenda).



### Persistencia de Datos



Todo el estado de la aplicación (la definición de los recursos, la lista de eventos planificados, etc.) debe poder **guardarse y cargarse desde un único archivo** (ej. en formato JSON o un formato de texto propio). Esta funcionalidad es fundamental, ya que permite que tu aplicación pueda gestionar diferentes dominios y escenarios simplemente cambiando el archivo que se carga al inicio.



## 4. Requisitos Técnicos y Entregables



- **Tecnología:** Python. Se recomienda el uso de la librería `datetime` para la gestión del tiempo y `json` para la persistencia de datos.

- **Entregables:**

    1. **Código Fuente:** Todos los archivos `.py` de tu proyecto, debidamente comentados y organizados.

    2. **Documento `README.md`:** Es una parte crucial del proyecto. Debe explicar claramente:

        - El dominio que elegiste y por qué.

        - Una descripción detallada de los eventos, recursos y, muy importante, **las restricciones que implementaste**, con ejemplos.

        - Instrucciones claras sobre cómo ejecutar el programa y usar sus funcionalidades.

    3. **Archivo de Datos de Ejemplo:** Un archivo de datos (`.json`, `.txt`, etc.) que demuestre el funcionamiento de tu aplicación en el dominio elegido.

    4. **Control de Versiones:** El proyecto debe ser desarrollado usando **Git** y entregado a través de un enlace a un repositorio (GitHub). Se esperan _commits_ frecuentes que muestren un progreso incremental.



## 5. Desafíos Opcionales para Sobresalir



Si completas todos los requisitos mínimos y quieres mejorar tu calificación, puedes implementar una o más de las siguientes funcionalidades avanzadas:

- **Recursos con Cantidad (Pools de Recursos):** En lugar de que cada recurso sea único (ej. "Cámara 1", "Cámara 2"), permite que existan recursos con una cantidad disponible (ej. "Cámara", `cantidad: 5`). La lógica de conflictos deberá comprobar si quedan unidades disponibles en lugar de un simple "ocupado/libre".

- **Planificación de Eventos Recurrentes:** Añade la opción de crear eventos que se repitan automáticamente cada día, semana o mes. El sistema deberá ser capaz de planificar todas las ocurrencias futuras, validando los conflictos y restricciones para cada una de ellas de forma individual.

- **Cualquiera otra funcionalidad interesante que se te ocurra**...



y este fue lo que se me ocurri'o que yo queria hacer

# Ideas del proyecto

nombre del proyecto: Dragón del sabor

Objetivo: Sistema de gestion de restaurantes (enfocado a un restaurante japones)

## Fase 1

Inicia el restaurante con unos empleados preestablecidos, unos ingredientes, unas mesas y un dinero por defecto, luego hay un menu por defecto, estas comidas requieren ingredientes y un chef que la haga, mientras un chef hace una comida no puede estar haciendo la comida de otra mesa, cada comida lleva un tiempo de preparacion, este tiempo se ve que el cocinero estara ocupado y por tanto no puede estar haciendo otra, ahora el calculo no es paso a paso, sino, cada comida del menu tiene un tiempo de hacerse, y unos recursos (ingredientes) lo que se hace es sumarse el tiempo de toda la comida que pidio la misma mesa, luego de ese tiempo el chef estara disponible, sin embargo capaz un segundo chef si puede estar disponible mientras, una vez se acabe un ingrediente de un plato, el plato no se puede preparar, luego los clientes pueden quitar ingredientes, lo que no baja el precio del plato, sin embargo si puede hacer que un plato se que no tenia ese ingrediente se habilite, sin embargo los platos tienen unos ingredientes base que no se pueden quitar

## Fase 2

la idea de lo anterior es que eso pase en una pestaña como principal. Ahora Crear una pestaña de menú, donde el usuario(el administrador del restaurante) puede añadir platos nuevos y eliminar otros, o editarlos, ya sea precio, ingredientes, imagen y así y crear un menú nuevo

## Fase 3

Una tercera pestaña que sea como para mostrar los empleados que trabajan en el restaurante, nombre, experiencia, cargo, foto, y arriba a la derecha o donde sea una cosita de ofertas de empleo donde cuando toques te salga las personas que quieren trabajar en el restaurante, puedes filtrar por cargo y experiencia, pero además por defecto el sistema te pone de primero al que más el sistema considera que necesita tu restaurante, por ejemplo si tienes 10 chef senior, y 1 dependiente, el lugar de ofertas de empleo a los primeros que te va a sacar será a los dependientes, aunque sea un dependiente novato te lo pondrá por encima de un chef senior ya que a tu restaurante no le hace falta mas chefs

## Fase 4

Una cuarta pestaña que sea como una tienda en la cual se puedan comprar los ingredientes de las comidas y así. En este punto habría que crear un sistema de alertas para que cuando el restaurante se esté quedando sin ingredientes para las comidas, le advierta al usuario para que vaya a comprar, sino se le bloqueará la comida especifica a los clientes como en la fase 1

# Fase 5

Una quinta pestaña que sea como el sistema de contabilidad del restaurante, la idea es que tú inicias con un dinero para el restaurante y tal pero a medida que avanza tu restaurante, contrata trabajadores, compra ingredientes etc, ese dinero sube (vendiendo platos) o baja, ahora el punto de si con el precio de tus platos el restaurante es rentable o no lo dice esta pestaña, así como graficas del dinero a lo largo del tiempo del restaurante. 



ahora mira el codigo que tengo hasta ahora
mi estructura 
dragon-del-sabor/
│
├── src/                          # Módulo principal de la aplicación
│   ├── __init__.py
│   ├── models/                  # Modelos de datos (clases)
│   │   ├── __init__.py
│   │   ├── events.py       # Restaurante, Mesa, etc.
│   │   ├── restaurant.py         # Empleado, Candidato
│   │
│   ├── core/                   # Lógica de negocio y simulaciones
│   │   ├── __init__.py
│   │   ├── scheduler.py        # Planificador de eventos (asignación de recursos)
│   │   ├── constraints.py      # Restricciones personalizadas (co-requisito, exclusión)
│   │
│   ├── persistence/            # Persistencia de datos
│   │   ├── __init__.py
│   │   ├── json_handler.py
│   │
│   ├── ui/                     # Interfaz de usuario (Streamlit)
│   │   ├── __init__.py
│   │   ├── components
│
├── data/                       # Datos persistentes
│   ├── default_config.json
│   ├── restaurant_state.json
│
├── assets/                     # Recursos estáticos
│   ├── images/
│   │   ├── dishes/             # Imágenes de platos
│   │   ├── employees/          # Fotos de empleados
│   │   └── icons/              # Íconos de la app
├── tests/                      # Pruebas
│   ├── __init__.py
│   │── test_scheduler.py
│
│── __init__.py
├── conftest.py
├── .gitignore
├── README.md                   # Documentación
├── main.py                     # Punto de entrada de Streamlit

main.py codigo 
"""
Main Streamlit application for Phase 1.
Simple UI that demonstrates all project requirements.
"""
import streamlit as st
import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent / "src"))

from src.models.restaurant import Restaurant, Order
from src.core.scheduler import EventScheduler
from src.persistence.json_handler import JSONHandler
from src.ui.components import (
    display_restaurant_status,
    order_form,
    display_scheduled_events,
    find_available_slot_form,
    display_resource_status
)

# Page configuration
st.set_page_config(
    page_title="Dragon's Flavor - Phase 1",
    page_icon="🐉",
    layout="wide"
)

# Initialize session state
if 'restaurant' not in st.session_state:
    # Try to load from saved state, otherwise create default
    data_file = Path("data") / "restaurant_state.json"
    
    if data_file.exists():
        st.session_state.restaurant = JSONHandler.load_restaurant(str(data_file))
    else:
        st.session_state.restaurant = JSONHandler.create_default_restaurant()
    
    st.session_state.scheduler = EventScheduler(st.session_state.restaurant)

def save_state():
    """Save current state to file."""
    data_file = Path("data") / "restaurant_state.json"
    data_file.parent.mkdir(exist_ok=True)
    JSONHandler.save_restaurant(st.session_state.restaurant, str(data_file))

def main():
    """Main application."""
    st.title("🐉 Dragon's Flavor - Phase 1")
    st.caption("Intelligent Restaurant Event Scheduler - Project for CC Course")
    
    # Sidebar navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.radio(
        "Go to",
        ["🏠 Dashboard", "📅 Schedule Order", "🔍 Find Slot", "📊 Resources", "⚙️ Settings"]
    )
    
    # Save state button in sidebar
    if st.sidebar.button("💾 Save State"):
        save_state()
        st.sidebar.success("State saved successfully!")
    
    # Dashboard page
    if page == "🏠 Dashboard":
        st.header("Restaurant Dashboard")
        
        # Display restaurant status
        display_restaurant_status(st.session_state.restaurant)
        
        st.divider()
        
        # Show scheduled events
        display_scheduled_events(st.session_state.scheduler)
        
        # Quick stats
        st.divider()
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📈 Quick Stats")
            st.write(f"- **Total Orders:** {len(st.session_state.restaurant.history)}")
            st.write(f"- **Active Orders:** {len(st.session_state.restaurant.active_orders)}")
            st.write(f"- **Available Chefs:** {sum(1 for e in st.session_state.restaurant.employees.values() if e.role == 'chef' and e.is_available)}")
        
        with col2:
            st.subheader("🎯 Project Features")
            st.write("✅ Resource conflict detection")
            st.write("✅ Constraint validation")
            st.write("✅ Automatic gap finding")
            st.write("✅ Event listing & cancellation")
            st.write("✅ JSON persistence")
    
    # Schedule Order page
    elif page == "📅 Schedule Order":
        st.header("Schedule New Order")
        
        # Display form
        order_data = order_form(
            st.session_state.restaurant,
            st.session_state.restaurant.menu,
            st.session_state.restaurant.tables
        )
        
        if order_data:
            # Create order object
            import uuid
            from datetime import datetime
            
            order = Order(
                id=f"order_{uuid.uuid4().hex[:8]}",
                table_id=order_data["table_id"],
                dishes=order_data["dishes"],
                modifications=order_data["modifications"]
            )
            
            # Calculate total price
            order.total_price = order.calculate_total_price(st.session_state.restaurant.menu)
            
            # Try to schedule
            success, message, event = st.session_state.scheduler.schedule_order(
                order,
                order_data["requested_time"]
            )
            
            if success:
                st.success("✅ " + message)
                st.session_state.restaurant.add_order(order)
                
                # Show event details
                st.json({
                    "event_id": event.id,
                    "order_id": order.id,
                    "table": event.table_id,
                    "chef": event.assigned_chef_id,
                    "start_time": event.start_time.strftime("%Y-%m-%d %H:%M"),
                    "end_time": event.end_time.strftime("%Y-%m-%d %H:%M"),
                    "total_price": f"${order.total_price:.2f}"
                })
                
                # Save state
                save_state()
                st.rerun()
            else:
                st.error("❌ " + message)
                
                # Offer to find next available slot
                if st.button("🔍 Find next available slot for this order"):
                    slot = st.session_state.scheduler.find_next_available_slot(order)
                    if slot:
                        st.info(f"Next available slot: **{slot.strftime('%Y-%m-%d %H:%M')}**")
                    else:
                        st.warning("No available slots found in the next 8 hours.")
    
    # Find Slot page
    elif page == "🔍 Find Slot":
        st.header("Find Available Time Slot")
        st.write("Use this tool to find when an order could be scheduled.")
        
        find_available_slot_form(
            st.session_state.scheduler,
            st.session_state.restaurant,
            st.session_state.restaurant.menu
        )
    
    # Resources page
    elif page == "📊 Resources":
        st.header("Resource Management")
        
        display_resource_status(st.session_state.restaurant)
        
        st.divider()
        
        # Show current constraints
        st.subheader("🔗 Active Constraints")
        
        st.write("#### Co-Requirements (Inclusion)")
        st.write("1. **Sushi dishes** require fresh wasabi and a sushi-specialized chef")
        st.write("2. **Tempura dishes** require sesame oil and a tempura-specialized chef")
        
        st.write("#### Mutual Exclusions")
        st.write("- **Sashimi and Tempura** cannot be ordered together (different temperature requirements)")
        
        st.divider()
        
        # Show menu
        st.subheader("🍣 Current Menu")
        
        for dish in st.session_state.restaurant.menu.values():
            with st.expander(f"{dish.name} - ${dish.price}"):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write(f"**Category:** {dish.category}")
                    st.write(f"**Prep time:** {dish.prep_time} min")
                    if dish.requires_specialty:
                        st.write(f"**Requires:** {dish.requires_specialty} chef")
                
                with col2:
                    st.write("**Ingredients:**")
                    for ing, amount in dish.ingredients.items():
                        st.write(f"- {ing}: {amount}")
                    
                    if dish.base_ingredients:
                        st.write("**Base ingredients (cannot be removed):**")
                        for base in dish.base_ingredients:
                            st.write(f"- {base}")
    
    # Settings page
    elif page == "⚙️ Settings":
        st.header("Settings")
        
        st.subheader("Restaurant Information")
        st.write(f"**Name:** {st.session_state.restaurant.name}")
        st.write(f"**Balance:** ${st.session_state.restaurant.balance:.2f}")
        
        st.divider()
        
        st.subheader("Data Management")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🔄 Reset to Default", type="secondary"):
                st.session_state.restaurant = JSONHandler.create_default_restaurant()
                st.session_state.scheduler = EventScheduler(st.session_state.restaurant)
                save_state()
                st.success("Restaurant reset to default!")
                st.rerun()
        
        with col2:
            if st.button("🗑️ Clear All Orders", type="secondary"):
                # Clear all orders and events
                st.session_state.restaurant.orders.clear()
                st.session_state.restaurant.active_orders.clear()
                st.session_state.restaurant.history.clear()
                st.session_state.scheduler.scheduled_events.clear()
                
                # Reset all chefs
                for emp in st.session_state.restaurant.employees.values():
                    if emp.role == "chef":
                        emp.is_available = True
                        emp.busy_until = None
                        emp.current_order_id = None
                
                # Reset all tables
                for table in st.session_state.restaurant.tables.values():
                    table.is_occupied = False
                    table.current_order_id = None
                
                save_state()
                st.success("All orders cleared!")
                st.rerun()
        
        st.divider()
        
        st.subheader("About This Project")
        st.write("""
        **Dragon's Flavor - Phase 1**  
        Intelligent Event Scheduler for Japanese Restaurant
        
        **Project Requirements Met:**
        1. ✅ Resource conflict detection (chefs, tables)
        2. ✅ Constraint validation (co-requirements & mutual exclusions)
        3. ✅ Automatic gap finding
        4. ✅ Event listing & management
        5. ✅ JSON persistence
        6. ✅ Error handling
        7. ✅ Simple UI with Streamlit
        
        **Domain:** Japanese Restaurant  
        **Resources:** Chefs, Ingredients, Tables  
        **Events:** Customer Orders
        """)

if __name__ == "__main__":
    main()
    conftest.py

conftest.py codigo
# conftest.py en la raíz del proyecto
import sys
from pathlib import Path

# Añade src al path de Python para todos los tests
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

test_scheduler.py codigo
"""
Unit tests for the scheduler - FIXED VERSION.
"""
import sys
import os
from pathlib import Path
import pytest
from datetime import datetime, timedelta

# Añade src al path de Python
current_dir = Path(__file__).parent
src_dir = current_dir.parent / "src"
sys.path.insert(0, str(src_dir))

# Importa DESPUÉS de añadir src al path
from models.restaurant import Restaurant, Order, Dish, Employee, Ingredient, Table, EmployeeRole, OrderStatus
from core.scheduler import EventScheduler
from core.constraints import ConstraintValidator

@pytest.fixture
def sample_restaurant():
    """Create a sample restaurant for testing."""
    restaurant = Restaurant(name="Test Restaurant", balance=10000.0)
    
    # Add a chef
    chef = Employee(
        id="chef_001",
        name="Test Chef",
        role=EmployeeRole.CHEF,
        experience="senior",
        salary=2500.0,
        specialties=["sushi"],
        is_available=True
    )
    restaurant.employees[chef.id] = chef
    
    # Add ingredients - use simple IDs that match dish requirements
    ingredients_data = [
        ("sushi_rice", "kg", 10.0, 2.0, 2.5),
        ("fresh_salmon", "kg", 5.0, 1.0, 18.0),
        ("wasabi", "kg", 2.0, 0.5, 30.0)
    ]
    
    for name, unit, qty, min_qty, price in ingredients_data:
        ingredient = Ingredient(
            id=name,  # Use name as ID to match dish requirements
            name=name,
            unit=unit,
            quantity=qty,
            min_quantity=min_qty,
            price_per_unit=price
        )
        restaurant.ingredients[ingredient.id] = ingredient
    
    # Add a dish - make sure ingredient names match
    dish = Dish(
        id="dish_001",
        name="Sushi Test",
        price=20.0,
        prep_time=15,
        ingredients={"sushi_rice": 0.1, "fresh_salmon": 0.05},
        base_ingredients=["sushi_rice", "fresh_salmon"],
        category="sushi",
        requires_specialty="sushi"
    )
    restaurant.menu[dish.id] = dish
    
    # Add a table
    table = Table(id="table_001", number=1, capacity=4)
    restaurant.tables[table.id] = table
    
    return restaurant

@pytest.fixture
def scheduler(sample_restaurant):
    """Create a scheduler with sample restaurant."""
    return EventScheduler(sample_restaurant)

def test_schedule_valid_order(scheduler, sample_restaurant):
    """Test scheduling a valid order."""
    order = Order(
        id="order_001",
        table_id="table_001",
        dishes={"dish_001": 1}
    )
    
    requested_time = datetime.now() + timedelta(hours=1)
    success, message, event = scheduler.schedule_order(order, requested_time)
    
    print(f"Test result: success={success}, message='{message}'")  # DEBUG
    assert success is True, f"Expected success but got: {message}"
    assert "successfully" in message.lower() or "scheduled" in message.lower()
    assert event is not None
    assert event.order_id == order.id
    assert len(scheduler.scheduled_events) == 1

def test_schedule_order_no_chef_available(scheduler, sample_restaurant):
    """Test scheduling when no chef is available."""
    # Make chef busy
    chef = sample_restaurant.employees["chef_001"]
    chef.is_available = False
    chef.busy_until = datetime.now() + timedelta(hours=2)
    
    order = Order(
        id="order_001",
        table_id="table_001",
        dishes={"dish_001": 1}
    )
    
    requested_time = datetime.now() + timedelta(minutes=30)
    success, message, event = scheduler.schedule_order(order, requested_time)
    
    print(f"Test result: success={success}, message='{message}'")  # DEBUG
    assert success is False
    # Could be "basic validation" or "no available chef"
    assert "chef" in message.lower() or "basic" in message.lower() or "available" in message.lower()
    assert event is None

def test_schedule_order_insufficient_ingredients(scheduler, sample_restaurant):
    """Test scheduling with insufficient ingredients."""
    # Reduce ingredient quantity
    sample_restaurant.ingredients["fresh_salmon"].quantity = 0.001
    
    order = Order(
        id="order_001",
        table_id="table_001",
        dishes={"dish_001": 2}  # Order 2 to require more ingredients
    )
    
    requested_time = datetime.now() + timedelta(hours=1)
    success, message, event = scheduler.schedule_order(order, requested_time)
    
    assert success is False
    assert "basic validation" in message.lower() or "ingredient" in message.lower() or "insufficient" in message.lower()
    assert event is None

def test_find_next_available_slot(scheduler, sample_restaurant):
    """Test finding next available slot."""
    order = Order(
        id="order_001",
        table_id="table_001",
        dishes={"dish_001": 1}
    )
    
    # Schedule first order
    first_time = datetime.now() + timedelta(minutes=30)
    success, message, _ = scheduler.schedule_order(order, first_time)
    print(f"First order result: {success}, {message}")  # DEBUG
    assert success is True, f"Should be able to schedule first order: {message}"
    
    # Create second order for same table
    order2 = Order(
        id="order_002",
        table_id="table_001",  # Same table
        dishes={"dish_001": 1}
    )
    
    # Find next slot - should be after first order completes
    next_slot = scheduler.find_next_available_slot(order2)
    
    assert next_slot is not None, "Should find a next slot"
    # Should be at least prep time after first order starts
    assert next_slot >= first_time + timedelta(minutes=15)

def test_list_all_events(scheduler, sample_restaurant):
    """Test listing all events."""
    order = Order(
        id="order_001",
        table_id="table_001",
        dishes={"dish_001": 1}
    )
    
    requested_time = datetime.now() + timedelta(hours=1)
    success, message, _ = scheduler.schedule_order(order, requested_time)
    print(f"Schedule result: {success}, {message}")  # DEBUG
    assert success is True, f"Should schedule successfully: {message}"
    
    events = scheduler.list_all_events()
    
    assert len(events) == 1
    assert events[0]["order_id"] == order.id
    assert events[0]["table"] == order.table_id

def test_cancel_event(scheduler, sample_restaurant):
    """Test canceling an event."""
    order = Order(
        id="order_001",
        table_id="table_001",
        dishes={"dish_001": 1}
    )
    
    requested_time = datetime.now() + timedelta(hours=1)
    success, message, event = scheduler.schedule_order(order, requested_time)
    
    print(f"Schedule result: {success}, {message}")  # DEBUG
    assert success is True, f"Should schedule successfully: {message}"
    
    # Cancel the event
    cancel_success = scheduler.cancel_event(event.id)
    
    assert cancel_success is True
    assert len(scheduler.scheduled_events) == 0
    
    # Verify resources were freed
    chef = sample_restaurant.employees["chef_001"]
    assert chef.is_available is True
    assert chef.busy_until is None
    
    table = sample_restaurant.tables["table_001"]
    assert table.is_occupied is False

def test_constraint_validator():
    """Test constraint validation."""
    validator = ConstraintValidator()
    
    # Add a co-requirement
    validator.add_co_requirement(
        name="test_requirement",
        trigger_condition=lambda dish: dish.category == "sushi",
        required_items=["wasabi"],
        message="Sushi requires wasabi"
    )
    
    # Add a mutual exclusion
    validator.add_mutual_exclusion(
        name="test_exclusion",
        item_a="sashimi",
        item_b="tempura",
        reason="Cannot be together"
    )
    
    # Test with sushi dish without wasabi
    sushi_dish = Dish(
        id="dish_001",
        name="Sushi",
        price=20.0,
        prep_time=15,
        ingredients={"rice": 0.1, "salmon": 0.05},
        base_ingredients=["rice"],
        category="sushi"
    )
    
    valid, message = validator.validate([sushi_dish])
    assert valid is False
    assert "wasabi" in message
    
    # Test with mutual exclusion violation
    sashimi_dish = Dish(
        id="dish_002",
        name="Sashimi",
        price=25.0,
        prep_time=10,
        ingredients={"salmon": 0.1},
        base_ingredients=["salmon"],
        category="sashimi"
    )
    
    tempura_dish = Dish(
        id="dish_003",
        name="Tempura",
        price=18.0,
        prep_time=20,
        ingredients={"batter": 0.2},
        base_ingredients=["batter"],
        category="tempura"
    )
    
    valid, message = validator.validate([sashimi_dish, tempura_dish])
    assert valid is False
    assert "cannot" in message.lower()
default_config.json
{
  "restaurant": {
    "name": "Dragon's Flavor",
    "initial_balance": 10000.0
  },
  "employees": [
    {
      "id": "emp_001",
      "name": "Kenji Tanaka",
      "role": "chef",
      "experience": "senior",
      "salary": 2500.0,
      "specialties": ["sushi", "sashimi"],
      "is_available": true
    },
    {
      "id": "emp_002",
      "name": "Aiko Yamamoto",
      "role": "chef",
      "experience": "intermediate",
      "salary": 1800.0,
      "specialties": ["tempura", "teriyaki"],
      "is_available": true
    }
  ],
  "ingredients": [
    {
      "id": "ing_001",
      "name": "sushi_rice",
      "unit": "kg",
      "quantity": 50.0,
      "min_quantity": 10.0,
      "price_per_unit": 2.5
    },
    {
      "id": "ing_002",
      "name": "fresh_salmon",
      "unit": "kg",
      "quantity": 20.0,
      "min_quantity": 5.0,
      "price_per_unit": 18.0
    }
  ],
  "menu": [
    {
      "id": "dish_001",
      "name": "Sushi Deluxe",
      "price": 24.99,
      "prep_time": 25,
      "ingredients": {
        "sushi_rice": 0.15,
        "fresh_salmon": 0.08,
        "wasabi": 0.01
      },
      "base_ingredients": ["sushi_rice", "fresh_salmon"],
      "category": "sushi",
      "requires_specialty": "sushi"
    },
    {
      "id": "dish_002",
      "name": "Tempura Special",
      "price": 18.99,
      "prep_time": 20,
      "ingredients": {
        "tempura_batter": 0.2,
        "sesame_oil": 0.05
      },
      "base_ingredients": ["tempura_batter"],
      "category": "tempura",
      "requires_specialty": "tempura"
    }
  ],
  "tables": [
    {"id": "table_01", "number": 1, "capacity": 4, "is_occupied": false},
    {"id": "table_02", "number": 2, "capacity": 4, "is_occupied": false}
  ],
  "constraints": {
    "co_requirements": [
      {
        "name": "sushi_requires_fresh_wasabi",
        "condition": "dish.category == 'sushi'",
        "requirements": [
          {"type": "ingredient", "name": "fresh_wasabi", "quantity": 1},
          {"type": "chef_specialty", "value": "sushi"}
        ]
      }
    ],
    "mutual_exclusions": [
      {
        "name": "no_raw_with_cooked",
        "forbidden_combinations": [["sashimi", "tempura"]]
      }
    ]
  }
}

restaurant_state.json
{
  "name": "Dragon's Flavor",
  "balance": 10000.0,
  "employees": {
    "chef_001": {
      "id": "chef_001",
      "name": "Kenji Tanaka",
      "role": "chef",
      "experience": "senior",
      "salary": 2500.0,
      "specialties": [
        "sushi",
        "sashimi"
      ],
      "is_available": true,
      "busy_until": null,
      "current_order_id": null
    },
    "chef_002": {
      "id": "chef_002",
      "name": "Aiko Yamamoto",
      "role": "chef",
      "experience": "intermediate",
      "salary": 1800.0,
      "specialties": [
        "tempura",
        "teriyaki"
      ],
      "is_available": true,
      "busy_until": null,
      "current_order_id": null
    }
  },
  "ingredients": {
    "ing_001": {
      "id": "ing_001",
      "name": "sushi_rice",
      "unit": "kg",
      "quantity": 50.0,
      "min_quantity": 10.0,
      "price_per_unit": 2.5
    },
    "ing_002": {
      "id": "ing_002",
      "name": "fresh_salmon",
      "unit": "kg",
      "quantity": 20.0,
      "min_quantity": 5.0,
      "price_per_unit": 18.0
    },
    "ing_003": {
      "id": "ing_003",
      "name": "wasabi",
      "unit": "kg",
      "quantity": 5.0,
      "min_quantity": 1.0,
      "price_per_unit": 30.0
    },
    "ing_004": {
      "id": "ing_004",
      "name": "tempura_batter",
      "unit": "kg",
      "quantity": 10.0,
      "min_quantity": 3.0,
      "price_per_unit": 5.0
    },
    "ing_005": {
      "id": "ing_005",
      "name": "sesame_oil",
      "unit": "liter",
      "quantity": 8.0,
      "min_quantity": 2.0,
      "price_per_unit": 12.0
    }
  },
  "menu": {
    "dish_001": {
      "id": "dish_001",
      "name": "Sushi Deluxe",
      "price": 24.99,
      "prep_time": 25,
      "ingredients": {
        "sushi_rice": 0.15,
        "fresh_salmon": 0.08,
        "wasabi": 0.01
      },
      "base_ingredients": [
        "sushi_rice",
        "fresh_salmon"
      ],
      "category": "sushi",
      "requires_specialty": "sushi",
      "is_active": true
    },
    "dish_002": {
      "id": "dish_002",
      "name": "Tempura Special",
      "price": 18.99,
      "prep_time": 20,
      "ingredients": {
        "tempura_batter": 0.2,
        "sesame_oil": 0.05
      },
      "base_ingredients": [
        "tempura_batter"
      ],
      "category": "tempura",
      "requires_specialty": "tempura",
      "is_active": true
    },
    "dish_003": {
      "id": "dish_003",
      "name": "Sashimi Plate",
      "price": 22.99,
      "prep_time": 15,
      "ingredients": {
        "fresh_salmon": 0.12,
        "wasabi": 0.01
      },
      "base_ingredients": [
        "fresh_salmon"
      ],
      "category": "sashimi",
      "requires_specialty": "sushi",
      "is_active": true
    }
  },
  "tables": {
    "table_001": {
      "id": "table_001",
      "number": 1,
      "capacity": 4,
      "is_occupied": false,
      "current_order_id": null
    },
    "table_002": {
      "id": "table_002",
      "number": 2,
      "capacity": 4,
      "is_occupied": false,
      "current_order_id": null
    },
    "table_003": {
      "id": "table_003",
      "number": 3,
      "capacity": 4,
      "is_occupied": false,
      "current_order_id": null
    },
    "table_004": {
      "id": "table_004",
      "number": 4,
      "capacity": 6,
      "is_occupied": false,
      "current_order_id": null
    },
    "table_005": {
      "id": "table_005",
      "number": 5,
      "capacity": 6,
      "is_occupied": false,
      "current_order_id": null
    }
  },
  "orders": {},
  "active_orders": [],
  "history": []
}
constraints.py codigo 
"""
Constraint validation system - handles co-requirements and mutual exclusions.
"""
from typing import List, Dict, Any, Callable, Tuple
from models.restaurant import Dish

class ConstraintValidator:
    """Validates constraints between resources."""
    
    def __init__(self):
        self.co_requirements: List[Dict] = []
        self.mutual_exclusions: List[Dict] = []
    
    def add_co_requirement(self, name: str, trigger_condition: Callable[[Dish], bool],
                          required_items: List[str], message: str) -> None:
        """Add a co-requirement constraint."""
        self.co_requirements.append({
            "name": name,
            "trigger": trigger_condition,
            "required_items": required_items,
            "message": message
        })
    
    def add_mutual_exclusion(self, name: str, item_a: str, item_b: str, reason: str) -> None:
        """Add a mutual exclusion constraint."""
        self.mutual_exclusions.append({
            "name": name,
            "items": [item_a, item_b],
            "reason": reason
        })
    
    def validate(self, dishes: List[Dish]) -> Tuple[bool, str]:
        """
        Validate all constraints for a list of dishes.
        Returns: (is_valid, error_message)
        """
        # Check co-requirements
        for constraint in self.co_requirements:
            # Check if any dish triggers this constraint
            triggered_dishes = [
                dish for dish in dishes 
                if constraint["trigger"](dish)
            ]
            
            if triggered_dishes:
                # All required items must be present in some dish
                for required_item in constraint["required_items"]:
                    if not any(required_item in dish.ingredients for dish in dishes):
                        return False, constraint["message"]
        
        # Check mutual exclusions
        dish_categories = [dish.category for dish in dishes]
        dish_names = [dish.name.lower() for dish in dishes]
        
        for constraint in self.mutual_exclusions:
            item_a, item_b = constraint["items"]
            
            # Check if both items are present
            has_item_a = any(item_a in cat.lower() for cat in dish_categories) or \
                        any(item_a in name for name in dish_names)
            has_item_b = any(item_b in cat.lower() for cat in dish_categories) or \
                        any(item_b in name for name in dish_names)
            
            if has_item_a and has_item_b:
                return False, constraint["reason"]
        
        return True, "All constraints satisfied"
    
    def validate_order(self, dishes: List[Dish], modifications: Dict[str, List[str]] = None) -> Tuple[bool, str]:
        """
        Alternative validation that considers modifications.
        """
        # Create modified dish views
        modified_dishes = []
        for dish in dishes:
            # Create a copy of dish with modifications applied
            if modifications and dish.id in modifications:
                # Filter out modified ingredients
                modified_ingredients = {
                    k: v for k, v in dish.ingredients.items() 
                    if k not in modifications[dish.id]
                }
                # Create a temporary dish object
                temp_dish = Dish(
                    id=dish.id,
                    name=dish.name,
                    price=dish.price,
                    prep_time=dish.prep_time,
                    ingredients=modified_ingredients,
                    base_ingredients=dish.base_ingredients,
                    category=dish.category,
                    requires_specialty=dish.requires_specialty,
                    is_active=dish.is_active
                )
                modified_dishes.append(temp_dish)
            else:
                modified_dishes.append(dish)
        
        return self.validate(modified_dishes)

        scheduler.py

        """
Intelligent Event Scheduler - Main component for project requirements.
Handles: Resource conflicts, constraint validation, gap finding.
"""
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Set
import uuid

from models.restaurant import Restaurant, Order, OrderStatus, Employee, Dish
from models.events import EventRequest, ScheduledEvent
from core.constraints import ConstraintValidator

class EventScheduler:
    """Main scheduler class - fulfills project requirements."""
    
    def __init__(self, restaurant: Restaurant):
        self.restaurant = restaurant
        self.constraint_validator = ConstraintValidator()
        self.scheduled_events: List[ScheduledEvent] = []
        
        # Load default constraints for Japanese restaurant
        self._load_default_constraints()
    
    def _load_default_constraints(self):
        """Load default constraints for our domain."""
        # 1. Co-requirement: Sushi dishes require fresh wasabi
        self.constraint_validator.add_co_requirement(
            name="sushi_requires_fresh_wasabi",
            trigger_condition=lambda dish: dish.category == "sushi",
            required_items=["fresh_wasabi"],
            message="Sushi dishes require fresh wasabi"
        )
        
        # 2. Co-requirement: Tempura requires sesame oil
        self.constraint_validator.add_co_requirement(
            name="tempura_requires_sesame_oil",
            trigger_condition=lambda dish: dish.category == "tempura",
            required_items=["sesame_oil"],
            message="Tempura requires sesame oil"
        )
        
        # 3. Mutual exclusion: Raw and cooked dishes shouldn't be together
        self.constraint_validator.add_mutual_exclusion(
            name="no_raw_with_cooked",
            item_a="sashimi",
            item_b="tempura",
            reason="Raw fish and cooked tempura have different temperature requirements"
        )
    
    def schedule_order(self, order: Order, requested_time: datetime) -> Tuple[bool, str, Optional[ScheduledEvent]]:
        """
        Main scheduling method - validates and schedules an order.
        Returns: (success, message, scheduled_event)
        """
        # Validate basic requirements
        if not self._validate_basic_requirements(order):
            return False, "Basic validation failed", None
        
        # Check resource conflicts
        conflict_check = self._check_resource_conflicts(order, requested_time)
        if not conflict_check[0]:
            return False, f"Resource conflict: {conflict_check[1]}", None
        
        # Validate constraints
        constraint_check = self._validate_constraints(order)
        if not constraint_check[0]:
            return False, f"Constraint violation: {constraint_check[1]}", None
        
        # Find available chef
        chef = self._find_available_chef(order, requested_time)
        if not chef:
            return False, "No available chef for the requested time", None
        
        # Calculate event duration
        duration = order.calculate_prep_time(self.restaurant.menu)
        end_time = requested_time + timedelta(minutes=duration)
        
        # Create scheduled event
        event = ScheduledEvent(
            id=str(uuid.uuid4()),
            order_id=order.id,
            table_id=order.table_id,
            start_time=requested_time,
            end_time=end_time,
            assigned_chef_id=chef.id,
            required_resources=self._get_required_resources(order)
        )
        
        # Reserve resources
        self._reserve_resources(order, chef, requested_time, end_time)
        
        # Update order
        order.status = OrderStatus.IN_PREPARATION
        order.assigned_chef_id = chef.id
        order.start_time = requested_time
        order.estimated_end_time = end_time
        
        # Add to scheduled events
        self.scheduled_events.append(event)
        
        return True, "Order scheduled successfully", event
    
    def _validate_basic_requirements(self, order: Order) -> bool:
        """Validate basic requirements like table availability and ingredients."""
        # Check table exists and is free
        table = self.restaurant.tables.get(order.table_id)
        if not table or table.is_occupied:
            return False
        
        # Check all dishes exist and are active
        for dish_id in order.dishes.keys():
            dish = self.restaurant.menu.get(dish_id)
            if not dish or not dish.is_active:
                return False
        
        # Check ingredient availability
        for dish_id, quantity in order.dishes.items():
            dish = self.restaurant.menu[dish_id]
            modifications = order.modifications.get(dish_id, [])
            
            for ingredient_name, amount_needed in dish.get_required_ingredients(modifications).items():
                ingredient = self.restaurant.ingredients.get(ingredient_name)
                if not ingredient or not ingredient.has_enough(amount_needed * quantity):
                    return False
        
        return True
    
    def _check_resource_conflicts(self, order: Order, requested_time: datetime) -> Tuple[bool, str]:
        """
        Check for resource conflicts (project requirement #1).
        Ensures no resource is double-booked.
        """
        duration = order.calculate_prep_time(self.restaurant.menu)
        end_time = requested_time + timedelta(minutes=duration)
        
        # Check chef availability
        chefs_busy = self._get_busy_chefs_in_interval(requested_time, end_time)
        available_chefs = [
            chef for chef in self.restaurant.employees.values() 
            if chef.role == "chef" and chef.id not in chefs_busy
        ]
        
        if not available_chefs:
            return False, "No chefs available in requested time slot"
        
        # Check if table is occupied during this time
        # (Simplified - in reality would check table reservations)
        table = self.restaurant.tables[order.table_id]
        if table.is_occupied:
            # Check if table will be free by requested_time
            current_order = self.restaurant.orders.get(table.current_order_id)
            if current_order and current_order.estimated_end_time:
                if current_order.estimated_end_time > requested_time:
                    return False, f"Table {table.number} occupied until {current_order.estimated_end_time}"
        
        return True, "No resource conflicts"
    
    def _get_busy_chefs_in_interval(self, start: datetime, end: datetime) -> Set[str]:
        """Get chefs busy during a time interval."""
        busy_chefs = set()
        
        for event in self.scheduled_events:
            # Check if time intervals overlap
            if not (event.end_time <= start or event.start_time >= end):
                busy_chefs.add(event.assigned_chef_id)
        
        return busy_chefs
    
    def _validate_constraints(self, order: Order) -> Tuple[bool, str]:
        """Validate all constraints for the order."""
        # Get all dishes in order
        dish_objects = []
        for dish_id in order.dishes.keys():
            dish = self.restaurant.menu.get(dish_id)
            if dish:
                dish_objects.append(dish)
        
        # Validate with constraint validator
        return self.constraint_validator.validate(dish_objects)
    
    def _find_available_chef(self, order: Order, start_time: datetime) -> Optional[Employee]:
        """Find an available chef considering specialties."""
        required_specialties = set()
        
        # Check if any dish requires specific specialty
        for dish_id in order.dishes.keys():
            dish = self.restaurant.menu.get(dish_id)
            if dish and dish.requires_specialty:
                required_specialties.add(dish.requires_specialty)
        
        # Find available chefs
        for employee in self.restaurant.employees.values():
            if employee.role != "chef":  # Comparar con string
                continue
            
            # Check availability
            if not employee.is_free_at(start_time):
                continue
            
            # Check specialties if required
            if required_specialties:
                if not any(spec in employee.specialties for spec in required_specialties):
                    continue
            
            return employee
        
        return None
    
    def _get_required_resources(self, order: Order) -> List[str]:
        """Get list of required resources for the order."""
        resources = []
        
        # Add table
        resources.append(f"table_{order.table_id}")
        
        # Add chef (will be assigned later)
        resources.append("chef")
        
        # Add ingredients
        for dish_id, quantity in order.dishes.items():
            dish = self.restaurant.menu[dish_id]
            modifications = order.modifications.get(dish_id, [])
            
            for ingredient_name in dish.get_required_ingredients(modifications).keys():
                resources.append(f"ingredient_{ingredient_name}")
        
        return resources
    
    def _reserve_resources(self, order: Order, chef: Employee, 
                          start_time: datetime, end_time: datetime) -> None:
        """Reserve all resources for the order."""
        # Reserve table
        table = self.restaurant.tables[order.table_id]
        table.is_occupied = True
        table.current_order_id = order.id
        
        # Reserve chef
        chef.is_available = False
        chef.busy_until = end_time
        chef.current_order_id = order.id
        
        # Reserve ingredients
        for dish_id, quantity in order.dishes.items():
            dish = self.restaurant.menu[dish_id]
            modifications = order.modifications.get(dish_id, [])
            
            for ingredient_name, amount_needed in dish.get_required_ingredients(modifications).items():
                ingredient = self.restaurant.ingredients[ingredient_name]
                ingredient.quantity -= amount_needed * quantity
    
    def find_next_available_slot(self, order: Order, 
                                start_from: datetime = None,
                                search_hours: int = 8) -> Optional[datetime]:
        """
        Find next available time slot for an order (project requirement).
        Returns: Next available datetime or None if no slot found.
        """
        if start_from is None:
            start_from = datetime.now()
        
        duration = order.calculate_prep_time(self.restaurant.menu)
        
        # Check every 15 minutes in the next search_hours
        current_time = start_from
        end_search = start_from + timedelta(hours=search_hours)
        
        while current_time < end_search:
            # Check if this time slot works
            success, message, _ = self.schedule_order(order, current_time)
            
            if success:
                # Clean up - we're just checking, not actually scheduling
                self._undo_test_scheduling(order, current_time)
                return current_time
            
            # Try next 15-minute interval
            current_time += timedelta(minutes=15)
        
        return None
    
    def _undo_test_scheduling(self, order: Order, test_time: datetime) -> None:
        """Clean up after test scheduling."""
        # Remove any test events
        self.scheduled_events = [
            e for e in self.scheduled_events 
            if not (e.order_id == order.id and e.start_time == test_time)
        ]
    
    def list_all_events(self) -> List[Dict]:
        """List all scheduled events (project requirement)."""
        events = []
        for event in self.scheduled_events:
            events.append({
                "id": event.id,
                "order_id": event.order_id,
                "table": event.table_id,
                "chef": event.assigned_chef_id,
                "start_time": event.start_time.strftime("%Y-%m-%d %H:%M"),
                "end_time": event.end_time.strftime("%Y-%m-%d %H:%M"),
                "status": event.status
            })
        return events
    
    def cancel_event(self, event_id: str) -> bool:
        """Cancel a scheduled event and free resources."""
        event = next((e for e in self.scheduled_events if e.id == event_id), None)
        if not event:
            return False
        
        # Free table
        table = self.restaurant.tables.get(event.table_id)
        if table:
            table.is_occupied = False
            table.current_order_id = None
        
        # Free chef
        chef = self.restaurant.employees.get(event.assigned_chef_id)
        if chef:
            chef.is_available = True
            chef.busy_until = None
            chef.current_order_id = None
        
        # Update order status
        order = self.restaurant.orders.get(event.order_id)
        if order:
            order.status = OrderStatus.CANCELLED
        
        # Remove event
        self.scheduled_events.remove(event)
        
        return True


events.py
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict, Any, Optional
from enum import Enum

class ConstraintType(Enum):
    CO_REQUIREMENT = "co_requirement"
    MUTUAL_EXCLUSION = "mutual_exclusion"

@dataclass
class Constraint:
    type: ConstraintType
    name: str
    description: str
    conditions: Dict[str, Any]
    
    @classmethod
    def create_co_requirement(cls, name: str, required_items: List[str], 
                            trigger_condition: Dict[str, Any]) -> 'Constraint':
        """Create a co-requirement constraint."""
        return cls(
            type=ConstraintType.CO_REQUIREMENT,
            name=name,
            description=f"Requires {', '.join(required_items)}",
            conditions={
                "required_items": required_items,
                "trigger": trigger_condition
            }
        )
    
    @classmethod
    def create_mutual_exclusion(cls, name: str, item_a: str, item_b: str, 
                               reason: str) -> 'Constraint':
        """Create a mutual exclusion constraint."""
        return cls(
            type=ConstraintType.MUTUAL_EXCLUSION,
            name=name,
            description=f"{item_a} and {item_b} cannot be used together",
            conditions={
                "items": [item_a, item_b],
                "reason": reason
            }
        )

@dataclass
class EventRequest:
    """Request to schedule an event (order)."""
    table_id: str
    dish_requests: List[Dict[str, Any]]  # Each: {"dish_id": "id", "quantity": 1, "modifications": []}
    requested_time: datetime
    duration: int  # Estimated duration in minutes
    
    def get_dish_ids(self) -> List[str]:
        """Get all dish IDs in the request."""
        return [req["dish_id"] for req in self.dish_requests]
    
    def get_total_quantity(self, dish_id: str) -> int:
        """Get total quantity of a specific dish."""
        total = 0
        for req in self.dish_requests:
            if req["dish_id"] == dish_id:
                total += req.get("quantity", 1)
        return total

@dataclass
class ScheduledEvent:
    """A successfully scheduled event."""
    id: str
    order_id: str
    table_id: str
    start_time: datetime
    end_time: datetime
    assigned_chef_id: str
    required_resources: List[str]
    status: str = "scheduled"

restaurant.py
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Set
from enum import Enum

class OrderStatus(Enum):
    PENDING = "pending"
    IN_PREPARATION = "in_preparation"
    READY = "ready"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class EmployeeRole(Enum):
    CHEF = "chef"
    WAITER = "waiter"
    MANAGER = "manager"

@dataclass
class Employee:
    id: str
    name: str
    role: EmployeeRole
    experience: str  # novice, intermediate, senior
    salary: float
    specialties: List[str] = field(default_factory=list)
    is_available: bool = True
    busy_until: Optional[datetime] = None
    current_order_id: Optional[str] = None
    
    def is_free_at(self, time: datetime) -> bool:
        """Check if employee is free at given time."""
        if self.busy_until is None:
            return True
        return time > self.busy_until

@dataclass
class Ingredient:
    id: str
    name: str
    unit: str  # kg, liters, units
    quantity: float
    min_quantity: float
    price_per_unit: float
    
    def has_enough(self, amount: float) -> bool:
        """Check if there's enough of this ingredient."""
        return self.quantity >= amount

@dataclass
class Dish:
    id: str
    name: str
    price: float
    prep_time: int  # minutes
    ingredients: Dict[str, float]  # ingredient_name: amount_needed
    base_ingredients: List[str]  # Cannot be removed
    category: str = ""
    requires_specialty: Optional[str] = None
    is_active: bool = True
    
    def get_required_ingredients(self, modifications: List[str] = None) -> Dict[str, float]:
        """Get ingredients needed, excluding modifications."""
        if modifications is None:
            modifications = []
        return {k: v for k, v in self.ingredients.items() if k not in modifications}

@dataclass
class Table:
    id: str
    number: int
    capacity: int
    is_occupied: bool = False
    current_order_id: Optional[str] = None

@dataclass
class Order:
    id: str
    table_id: str
    dishes: Dict[str, int]  # dish_id: quantity
    status: OrderStatus = OrderStatus.PENDING
    assigned_chef_id: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    start_time: Optional[datetime] = None
    estimated_end_time: Optional[datetime] = None
    modifications: Dict[str, List[str]] = field(default_factory=dict)  # dish_id: [removed_ingredients]
    total_price: float = 0.0
    
    def calculate_total_price(self, menu: Dict[str, 'Dish']) -> float:
        """Calculate total price based on menu prices."""
        total = 0.0
        for dish_id, quantity in self.dishes.items():
            if dish_id in menu:
                total += menu[dish_id].price * quantity
        return total
    
    def calculate_prep_time(self, menu: Dict[str, 'Dish']) -> int:
        """Calculate total preparation time in minutes."""
        total_time = 0
        for dish_id, quantity in self.dishes.items():
            if dish_id in menu:
                total_time += menu[dish_id].prep_time * quantity
        return total_time

@dataclass
class Restaurant:
    name: str
    balance: float
    employees: Dict[str, Employee] = field(default_factory=dict)
    ingredients: Dict[str, Ingredient] = field(default_factory=dict)
    menu: Dict[str, Dish] = field(default_factory=dict)
    tables: Dict[str, Table] = field(default_factory=dict)
    orders: Dict[str, Order] = field(default_factory=dict)
    active_orders: List[str] = field(default_factory=list)
    history: List[Order] = field(default_factory=list)
    
    def add_order(self, order: Order) -> None:
        """Add order to restaurant."""
        self.orders[order.id] = order
        self.active_orders.append(order.id)
        
    def complete_order(self, order_id: str) -> None:
        """Move order from active to history."""
        if order_id in self.orders:
            order = self.orders[order_id]
            order.status = OrderStatus.COMPLETED
            self.history.append(order)
            self.active_orders.remove(order_id)
            
            # Free the table
            for table in self.tables.values():
                if table.current_order_id == order_id:
                    table.is_occupied = False
                    table.current_order_id = None


json_handler.py
"""
JSON persistence handler - saves/loads restaurant state.
"""
import json
from datetime import datetime
from typing import Any, Dict, List
from pathlib import Path

from models.restaurant import Restaurant, Employee, Ingredient, Dish, Table, Order, OrderStatus

class DateTimeEncoder(json.JSONEncoder):
    """Custom JSON encoder for datetime objects."""
    
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)

class JSONHandler:
    """Handles JSON serialization/deserialization."""
    
    @staticmethod
    def save_restaurant(restaurant: Restaurant, filepath: str) -> bool:
        """Save restaurant state to JSON file."""
        try:
            data = {
                "name": restaurant.name,
                "balance": restaurant.balance,
                "employees": JSONHandler._serialize_employees(restaurant.employees),
                "ingredients": JSONHandler._serialize_ingredients(restaurant.ingredients),
                "menu": JSONHandler._serialize_dishes(restaurant.menu),
                "tables": JSONHandler._serialize_tables(restaurant.tables),
                "orders": JSONHandler._serialize_orders(restaurant.orders),
                "active_orders": restaurant.active_orders,
                "history": JSONHandler._serialize_orders_list(restaurant.history)
            }
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, cls=DateTimeEncoder, indent=2)
            return True
        except Exception as e:
            print(f"Error saving restaurant: {e}")
            return False
    
    @staticmethod
    def load_restaurant(filepath: str) -> Restaurant:
        """Load restaurant state from JSON file."""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Create restaurant instance
            restaurant = Restaurant(
                name=data["name"],
                balance=data["balance"]
            )
            
            # Load components
            restaurant.employees = JSONHandler._deserialize_employees(data["employees"])
            restaurant.ingredients = JSONHandler._deserialize_ingredients(data["ingredients"])
            restaurant.menu = JSONHandler._deserialize_dishes(data["menu"])
            restaurant.tables = JSONHandler._deserialize_tables(data["tables"])
            restaurant.orders = JSONHandler._deserialize_orders(data["orders"])
            restaurant.active_orders = data["active_orders"]
            restaurant.history = JSONHandler._deserialize_orders_list(data["history"])
            
            return restaurant
        except Exception as e:
            print(f"Error loading restaurant: {e}")
            # Return default restaurant
            return JSONHandler.create_default_restaurant()
    
    @staticmethod
    def create_default_restaurant() -> Restaurant:
        """Create a default restaurant for testing."""
        restaurant = Restaurant(
            name="Dragon's Flavor",
            balance=10000.0
        )
        
        # Add default employees
        chef1 = Employee(
            id="chef_001",
            name="Kenji Tanaka",
            role="chef",
            experience="senior",
            salary=2500.0,
            specialties=["sushi", "sashimi"]
        )
        
        chef2 = Employee(
            id="chef_002",
            name="Aiko Yamamoto",
            role="chef",
            experience="intermediate",
            salary=1800.0,
            specialties=["tempura", "teriyaki"]
        )
        
        restaurant.employees = {
            chef1.id: chef1,
            chef2.id: chef2
        }
        
        # Add default ingredients
        ingredients_data = [
            ("sushi_rice", "kg", 50.0, 10.0, 2.5),
            ("fresh_salmon", "kg", 20.0, 5.0, 18.0),
            ("wasabi", "kg", 5.0, 1.0, 30.0),
            ("tempura_batter", "kg", 10.0, 3.0, 5.0),
            ("sesame_oil", "liter", 8.0, 2.0, 12.0)
        ]
        
        for i, (name, unit, qty, min_qty, price) in enumerate(ingredients_data, 1):
            ingredient = Ingredient(
                id=f"ing_{i:03d}",
                name=name,
                unit=unit,
                quantity=qty,
                min_quantity=min_qty,
                price_per_unit=price
            )
            restaurant.ingredients[ingredient.id] = ingredient
        
        # Add default dishes
        dishes_data = [
            ("Sushi Deluxe", 24.99, 25, 
             {"sushi_rice": 0.15, "fresh_salmon": 0.08, "wasabi": 0.01},
             ["sushi_rice", "fresh_salmon"], "sushi", "sushi"),
            
            ("Tempura Special", 18.99, 20,
             {"tempura_batter": 0.2, "sesame_oil": 0.05},
             ["tempura_batter"], "tempura", "tempura"),
            
            ("Sashimi Plate", 22.99, 15,
             {"fresh_salmon": 0.12, "wasabi": 0.01},
             ["fresh_salmon"], "sashimi", "sushi")
        ]
        
        for i, (name, price, prep_time, ing, base, category, specialty) in enumerate(dishes_data, 1):
            dish = Dish(
                id=f"dish_{i:03d}",
                name=name,
                price=price,
                prep_time=prep_time,
                ingredients=ing,
                base_ingredients=base,
                category=category,
                requires_specialty=specialty
            )
            restaurant.menu[dish.id] = dish
        
        # Add default tables
        for i in range(1, 6):
            table = Table(
                id=f"table_{i:03d}",
                number=i,
                capacity=4 if i <= 3 else 6
            )
            restaurant.tables[table.id] = table
        
        return restaurant
    
    # Serialization helper methods
    @staticmethod
    def _serialize_employees(employees: Dict[str, Employee]) -> Dict:
        return {
            emp_id: {
                "id": emp.id,
                "name": emp.name,
                "role": emp.role,
                "experience": emp.experience,
                "salary": emp.salary,
                "specialties": emp.specialties,
                "is_available": emp.is_available,
                "busy_until": emp.busy_until.isoformat() if emp.busy_until else None,
                "current_order_id": emp.current_order_id
            }
            for emp_id, emp in employees.items()
        }
    
    @staticmethod
    def _deserialize_employees(data: Dict) -> Dict[str, Employee]:
        employees = {}
        for emp_data in data.values():
            emp = Employee(
                id=emp_data["id"],
                name=emp_data["name"],
                role=emp_data["role"],
                experience=emp_data["experience"],
                salary=emp_data["salary"],
                specialties=emp_data["specialties"],
                is_available=emp_data["is_available"],
                busy_until=datetime.fromisoformat(emp_data["busy_until"]) if emp_data["busy_until"] else None,
                current_order_id=emp_data["current_order_id"]
            )
            employees[emp.id] = emp
        return employees
    
    @staticmethod
    def _serialize_ingredients(ingredients: Dict[str, Ingredient]) -> Dict:
        return {
            ing_id: {
                "id": ing.id,
                "name": ing.name,
                "unit": ing.unit,
                "quantity": ing.quantity,
                "min_quantity": ing.min_quantity,
                "price_per_unit": ing.price_per_unit
            }
            for ing_id, ing in ingredients.items()
        }
    
    @staticmethod
    def _deserialize_ingredients(data: Dict) -> Dict[str, Ingredient]:
        ingredients = {}
        for ing_data in data.values():
            ing = Ingredient(
                id=ing_data["id"],
                name=ing_data["name"],
                unit=ing_data["unit"],
                quantity=ing_data["quantity"],
                min_quantity=ing_data["min_quantity"],
                price_per_unit=ing_data["price_per_unit"]
            )
            ingredients[ing.id] = ing
        return ingredients
    
    @staticmethod
    def _serialize_dishes(dishes: Dict[str, Dish]) -> Dict:
        return {
            dish_id: {
                "id": dish.id,
                "name": dish.name,
                "price": dish.price,
                "prep_time": dish.prep_time,
                "ingredients": dish.ingredients,
                "base_ingredients": dish.base_ingredients,
                "category": dish.category,
                "requires_specialty": dish.requires_specialty,
                "is_active": dish.is_active
            }
            for dish_id, dish in dishes.items()
        }
    
    @staticmethod
    def _deserialize_dishes(data: Dict) -> Dict[str, Dish]:
        dishes = {}
        for dish_data in data.values():
            dish = Dish(
                id=dish_data["id"],
                name=dish_data["name"],
                price=dish_data["price"],
                prep_time=dish_data["prep_time"],
                ingredients=dish_data["ingredients"],
                base_ingredients=dish_data["base_ingredients"],
                category=dish_data["category"],
                requires_specialty=dish_data["requires_specialty"],
                is_active=dish_data["is_active"]
            )
            dishes[dish.id] = dish
        return dishes
    
    @staticmethod
    def _serialize_tables(tables: Dict[str, Table]) -> Dict:
        return {
            table_id: {
                "id": table.id,
                "number": table.number,
                "capacity": table.capacity,
                "is_occupied": table.is_occupied,
                "current_order_id": table.current_order_id
            }
            for table_id, table in tables.items()
        }
    
    @staticmethod
    def _deserialize_tables(data: Dict) -> Dict[str, Table]:
        tables = {}
        for table_data in data.values():
            table = Table(
                id=table_data["id"],
                number=table_data["number"],
                capacity=table_data["capacity"],
                is_occupied=table_data["is_occupied"],
                current_order_id=table_data["current_order_id"]
            )
            tables[table.id] = table
        return tables
    
    @staticmethod
    def _serialize_orders(orders: Dict[str, Order]) -> Dict:
        serialized = {}
        for order_id, order in orders.items():
            serialized[order_id] = {
                "id": order.id,
                "table_id": order.table_id,
                "dishes": order.dishes,
                "status": order.status.value,
                "assigned_chef_id": order.assigned_chef_id,
                "created_at": order.created_at.isoformat(),
                "start_time": order.start_time.isoformat() if order.start_time else None,
                "estimated_end_time": order.estimated_end_time.isoformat() if order.estimated_end_time else None,
                "modifications": order.modifications,
                "total_price": order.total_price
            }
        return serialized
    
    @staticmethod
    def _deserialize_orders(data: Dict) -> Dict[str, Order]:
        orders = {}
        for order_data in data.values():
            order = Order(
                id=order_data["id"],
                table_id=order_data["table_id"],
                dishes=order_data["dishes"],
                status=OrderStatus(order_data["status"]),
                assigned_chef_id=order_data["assigned_chef_id"],
                created_at=datetime.fromisoformat(order_data["created_at"]),
                start_time=datetime.fromisoformat(order_data["start_time"]) if order_data["start_time"] else None,
                estimated_end_time=datetime.fromisoformat(order_data["estimated_end_time"]) if order_data["estimated_end_time"] else None,
                modifications=order_data["modifications"],
                total_price=order_data["total_price"]
            )
            orders[order.id] = order
        return orders
    
    @staticmethod
    def _serialize_orders_list(orders_list: List[Order]) -> List:
        return [
            {
                "id": order.id,
                "table_id": order.table_id,
                "dishes": order.dishes,
                "status": order.status.value,
                "assigned_chef_id": order.assigned_chef_id,
                "created_at": order.created_at.isoformat(),
                "start_time": order.start_time.isoformat() if order.start_time else None,
                "estimated_end_time": order.estimated_end_time.isoformat() if order.estimated_end_time else None,
                "modifications": order.modifications,
                "total_price": order.total_price
            }
            for order in orders_list
        ]
    
    @staticmethod
    def _deserialize_orders_list(data: List) -> List[Order]:
        orders = []
        for order_data in data:
            order = Order(
                id=order_data["id"],
                table_id=order_data["table_id"],
                dishes=order_data["dishes"],
                status=OrderStatus(order_data["status"]),
                assigned_chef_id=order_data["assigned_chef_id"],
                created_at=datetime.fromisoformat(order_data["created_at"]),
                start_time=datetime.fromisoformat(order_data["start_time"]) if order_data["start_time"] else None,
                estimated_end_time=datetime.fromisoformat(order_data["estimated_end_time"]) if order_data["estimated_end_time"] else None,
                modifications=order_data["modifications"],
                total_price=order_data["total_price"]
            )
            orders.append(order)
        return orders
components.py

"""
UI components for Streamlit interface.
"""
import streamlit as st
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from models.restaurant import Restaurant, Order
from core.scheduler import EventScheduler
from persistence.json_handler import JSONHandler
def display_restaurant_status(restaurant):
    """Display current restaurant status."""
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("💰 Balance", f"${restaurant.balance:,.2f}")
    
    with col2:
        available_tables = sum(1 for t in restaurant.tables.values() if not t.is_occupied)
        total_tables = len(restaurant.tables)
        st.metric("🍽️ Tables", f"{available_tables}/{total_tables} available")
    
    with col3:
        available_chefs = sum(1 for e in restaurant.employees.values() 
                            if e.role == "chef" and e.is_available)
        total_chefs = sum(1 for e in restaurant.employees.values() if e.role == "chef")
        st.metric("👨‍🍳 Chefs", f"{available_chefs}/{total_chefs} available")
    
    with col4:
        active_orders = len(restaurant.active_orders)
        st.metric("📝 Active Orders", active_orders)

def order_form(restaurant, menu, tables):
    """Form for creating a new order."""
    st.subheader("📋 Create New Order")
    
    # Table selection
    available_tables = [t for t in tables.values() if not t.is_occupied]
    table_options = {f"Table {t.number} ({t.capacity} people)": t.id for t in available_tables}
    
    if not table_options:
        st.warning("No tables available!")
        return None
    
    selected_table_label = st.selectbox("Select Table", list(table_options.keys()))
    table_id = table_options[selected_table_label]
    
    # Dish selection
    st.write("### Select Dishes")
    
    order_items = {}
    modifications = {}
    
    for dish in menu.values():
        if not dish.is_active:
            continue
            
        col1, col2, col3 = st.columns([3, 1, 3])
        
        with col1:
            st.write(f"**{dish.name}** - ${dish.price}")
            st.caption(f"Prep time: {dish.prep_time} min")
        
        with col2:
            quantity = st.number_input(
                "Qty",
                min_value=0,
                max_value=10,
                value=0,
                key=f"qty_{dish.id}"
            )
            
            if quantity > 0:
                order_items[dish.id] = quantity
        
        with col3:
            if quantity > 0 and dish.ingredients:
                # Show modification options (remove ingredients)
                removable = [ing for ing in dish.ingredients.keys() 
                           if ing not in dish.base_ingredients]
                
                if removable:
                    removed = st.multiselect(
                        "Remove ingredients",
                        removable,
                        key=f"mod_{dish.id}"
                    )
                    if removed:
                        modifications[dish.id] = removed
    
    # Request time
    st.write("### Schedule Time")
    col1, col2 = st.columns(2)
    
    with col1:
        request_date = st.date_input("Date", value=datetime.now().date())
    
    with col2:
        default_time = (datetime.now() + timedelta(hours=1)).time()
        request_time = st.time_input("Time", value=default_time)
    
    requested_datetime = datetime.combine(request_date, request_time)
    
    if st.button("📅 Schedule Order", type="primary"):
        if not order_items:
            st.error("Please select at least one dish!")
            return None
        
        return {
            "table_id": table_id,
            "dishes": order_items,
            "modifications": modifications,
            "requested_time": requested_datetime
        }
    
    return None

def display_scheduled_events(scheduler):
    """Display all scheduled events."""
    st.subheader("📅 Scheduled Events")
    
    events = scheduler.list_all_events()
    
    if not events:
        st.info("No events scheduled yet.")
        return
    
    for event in events:
        with st.expander(f"🕐 {event['start_time']} - Table {event['table']}"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.write(f"**Event ID:** {event['id']}")
                st.write(f"**Chef:** {event['chef']}")
                st.write(f"**Status:** {event['status']}")
            
            with col2:
                st.write(f"**Start:** {event['start_time']}")
                st.write(f"**End:** {event['end_time']}")
            
            if st.button("❌ Cancel", key=f"cancel_{event['id']}"):
                if scheduler.cancel_event(event['id']):
                    st.success(f"Event {event['id']} cancelled!")
                    st.rerun()
                else:
                    st.error("Failed to cancel event.")

def find_available_slot_form(scheduler, restaurant, menu):
    """Form to find next available slot."""
    st.subheader("🔍 Find Available Time Slot")
    
    # Create a test order
    st.write("### Create Test Order")
    
    test_items = {}
    test_modifications = {}
    
    for dish in menu.values():
        if not dish.is_active:
            continue
            
        quantity = st.number_input(
            f"{dish.name}",
            min_value=0,
            max_value=5,
            value=0,
            key=f"test_qty_{dish.id}"
        )
        
        if quantity > 0:
            test_items[dish.id] = quantity
            
            # Modifications for this dish
            removable = [ing for ing in dish.ingredients.keys() 
                       if ing not in dish.base_ingredients]
            
            if removable:
                removed = st.multiselect(
                    f"Remove from {dish.name}",
                    removable,
                    key=f"test_mod_{dish.id}"
                )
                if removed:
                    test_modifications[dish.id] = removed
    
    if st.button("Find Next Available Slot", type="secondary"):
        if not test_items:
            st.error("Please select at least one dish!")
            return
        
        # Create a temporary order for testing
        from ..models.restaurant import Order
        import uuid
        
        test_order = Order(
            id=f"test_{uuid.uuid4().hex[:8]}",
            table_id="table_001",  # Will be reassigned
            dishes=test_items,
            modifications=test_modifications
        )
        
        # Find available slot
        slot = scheduler.find_next_available_slot(test_order)
        
        if slot:
            st.success(f"✅ Next available slot: **{slot.strftime('%Y-%m-%d %H:%M')}**")
            st.info(f"That's in {(slot - datetime.now()).total_seconds() / 60:.0f} minutes")
        else:
            st.error("❌ No available slots found in the next 8 hours.")

def display_resource_status(restaurant):
    """Display current resource status."""
    st.subheader("📊 Resource Status")
    
    # Chefs status
    st.write("### 👨‍🍳 Chefs")
    chefs = [e for e in restaurant.employees.values() if e.role == "chef"]
    
    for chef in chefs:
        status = "🟢 Available" if chef.is_available else "🔴 Busy"
        busy_info = f" until {chef.busy_until.strftime('%H:%M')}" if chef.busy_until else ""
        st.write(f"- **{chef.name}** ({chef.experience}) - {status}{busy_info}")
    
    # Ingredients status
    st.write("### 🥗 Ingredients")
    
    low_ingredients = []
    for ingredient in restaurant.ingredients.values():
        if ingredient.quantity <= ingredient.min_quantity:
            low_ingredients.append(ingredient)
    
    if low_ingredients:
        st.warning("⚠️ Low inventory:")
        for ing in low_ingredients:
            st.write(f"- {ing.name}: {ing.quantity} {ing.unit} (min: {ing.min_quantity})")
    else:
        st.success("All ingredients are sufficiently stocked.")