import streamlit as st
import sys
from pathlib import Path
from datetime import datetime
import os

ROOT_DIR = Path(__file__).parent
if str(ROOT_DIR / "src") not in sys.path:
    sys.path.append(str(ROOT_DIR / "src"))

from src.core.scheduler import EventScheduler
from src.persistence.json_handler import JSONHandler
from src.components.dashboard import render_resource_status, render_event_timeline
from src.components.menu_admin import render_menu_manager
from src.components.staff_admin import render_staff_manager
from src.components.supply_store import render_store_and_stock
from src.components.finance import render_finances

def init_state():
    if 'restaurant' not in st.session_state:
        state_path = "data/restaurant_state.json"
        seed_path = "data/default_config.json"
        
        # Crear directorio data si no existe
        os.makedirs("data", exist_ok=True)

        if os.path.exists(state_path):
            rest, events = JSONHandler.load_restaurant(state_path)
        elif os.path.exists(seed_path):
            rest, events = JSONHandler.load_restaurant(seed_path)
        else:
            st.error("No se encontraron configuraciones base en el directorio data/.")
            return

        # Sincronización cronológica inicial al arrancar el programa
        now = datetime.now()
        active_events = []
        for event in events:
            if event.start_time <= now <= event.end_time:
                table = rest.tables.get(event.table_id)
                if table:
                    table.is_occupied = True
                active_events.append(event)
            elif event.end_time > now:
                active_events.append(event)
            else:
                table = rest.tables.get(event.table_id)
                if table:
                    table.is_occupied = False
                chef = rest.employees.get(event.assigned_chef_id)
                if chef:
                    chef.is_available = True
                    chef.busy_until = None

        st.session_state.restaurant = rest
        st.session_state.scheduler = EventScheduler(rest)
        st.session_state.scheduler.scheduled_events = active_events

def save_all():
    JSONHandler.save_restaurant(
        st.session_state.restaurant,
        st.session_state.scheduler.scheduled_events,
        "data/restaurant_state.json"
    )

def main():
    st.set_page_config(page_title="Il Gusto Giusto", page_icon="🍕", layout="wide")
    init_state()

    st.title("🍕 Il Gusto Giusto")
    st.caption("Planificador de Eventos y Motor de Disponibilidad")

    # Panel lateral de navegación
    menu = st.sidebar.radio(
        "Navegación del Sistema",
        [
            "Servicio (Dashboard)",
            "Gestión del Menú",
            "Contrataciones (Staff)",
            "Compras y Suministros",
            "Libro de Contabilidad"
        ]
    )

    if menu == "Servicio (Dashboard)":
        render_resource_status(st.session_state.restaurant, st.session_state.scheduler, save_all)
        st.divider()
        render_event_timeline(st.session_state.scheduler, save_all)
    elif menu == "Gestión del Menú":
        render_menu_manager(st.session_state.restaurant, save_all)
    elif menu == "Contrataciones (Staff)":
        render_staff_manager(st.session_state.restaurant, save_all)
    elif menu == "Compras y Suministros":
        render_store_and_stock(st.session_state.restaurant, save_all)
    elif menu == "Libro de Contabilidad":
        render_finances(st.session_state.restaurant)

if __name__ == "__main__":
    main()