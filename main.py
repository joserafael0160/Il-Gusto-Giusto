# main.py
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
from src.ui.styles import apply_custom_theme, render_italian_header

def init_state() -> None:
    """Initializes standard startup states or pulls prior database runs."""
    if 'restaurant' not in st.session_state:
        state_path = "data/restaurant_state.json"
        seed_path = "data/default_config.json"
        
        os.makedirs("data", exist_ok=True)

        if os.path.exists(state_path):
            restaurant, events = JSONHandler.load(state_path)
        elif os.path.exists(seed_path):
            restaurant, events = JSONHandler.load(seed_path)
        else:
            st.error("No se encontraron configuraciones base en el directorio data/.")
            return

        if restaurant and not restaurant.history:
            restaurant.add_transaction(restaurant.balance, "Capital Inicial de Apertura")

        now = datetime.now()
        active_events = []
        if restaurant:
            for event in events:
                if event.start_time <= now <= event.end_time:
                    table = restaurant.tables.get(event.table_id)
                    if table:
                        table.is_occupied = True
                    active_events.append(event)
                elif event.end_time > now:
                    active_events.append(event)
                else:
                    table = restaurant.tables.get(event.table_id)
                    if table:
                        table.is_occupied = False
                    chef = restaurant.employees.get(event.assigned_chef_id)
                    if chef:
                        chef.is_available = True
                        chef.busy_until = None

            # Limpiar eventos huérfanos
            active_events = [e for e in active_events if restaurant.employees.get(e.assigned_chef_id)]

            st.session_state.restaurant = restaurant
            st.session_state.scheduler = EventScheduler(restaurant)
            st.session_state.scheduler.scheduled_events = active_events

def save_all() -> None:
    """Persists current visual state back to disk."""
    JSONHandler.save(
        st.session_state.restaurant,
        st.session_state.scheduler.scheduled_events,
        "data/restaurant_state.json"
    )

def main() -> None:
    st.set_page_config(page_title="Il Gusto Giusto", page_icon="🍕", layout="wide")
    apply_custom_theme()
    init_state()

    render_italian_header("Il Gusto Giusto", "Sistema de Gestión de Restaurante Italiano")
    
    if "selected_menu" not in st.session_state:
        st.session_state.selected_menu = "Servicio (Dashboard)"

    st.sidebar.markdown(
        """
        <div style='text-align: center; margin-bottom: 15px; margin-top: 10px;'>
            <span style='font-size: 3.5rem;'>🍕</span>
            <h4 style='margin-top: 5px; font-family: "Georgia", serif;'>Il Gusto Giusto</h4>
            <p style='color: #888888; font-size: 0.8rem; margin: 0;'>Gestión Profesional</p>
        </div>
        <hr style='border-color: rgba(255,255,255,0.08); margin-bottom: 20px;' />
        """,
        unsafe_allow_html=True
    )

    menu_items = [
        {"key": "Servicio (Dashboard)", "label": "Servicio (Dashboard)", "icon": "📊"},
        {"key": "Gestión del Menú", "label": "Gestión del Menú", "icon": "📋"},
        {"key": "Contrataciones (Staff)", "label": "Contrataciones (Staff)", "icon": "👥"},
        {"key": "Compras y Suministros", "label": "Compras y Suministros", "icon": "🛒"},
        {"key": "Libro de Contabilidad", "label": "Libro de Contabilidad", "icon": "💰"},
        {"key": "Configuración", "label": "Configuración", "icon": "⚙️"}
    ]

    for item in menu_items:
        is_active = st.session_state.selected_menu == item["key"]
        btn_type = "primary" if is_active else "secondary"
        
        if st.sidebar.button(
            f"{item['icon']} &nbsp;&nbsp; {item['label']}",
            key=f"nav_btn_{item['key']}",
            width='stretch',
            type=btn_type
        ):
            st.session_state.selected_menu = item["key"]
            st.rerun()

    st.sidebar.markdown("<br><hr style='border-color: rgba(255,255,255,0.08);' />", unsafe_allow_html=True)
    current_view = st.session_state.selected_menu

    if "restaurant" in st.session_state:
        if current_view == "Servicio (Dashboard)":
            render_resource_status(st.session_state.restaurant, st.session_state.scheduler, save_all)
            st.divider()
            render_event_timeline(st.session_state.scheduler, save_all)
        elif current_view == "Gestión del Menú":
            render_menu_manager(st.session_state.restaurant, save_all)
        elif current_view == "Contrataciones (Staff)":
            render_staff_manager(st.session_state.restaurant, save_all, st.session_state.scheduler)
        elif current_view == "Compras y Suministros":
            render_store_and_stock(st.session_state.restaurant, save_all)
        elif current_view == "Libro de Contabilidad":
            render_finances(st.session_state.restaurant)
        elif current_view == "Configuración":
            from src.components.settings import render_settings
            render_settings()

if __name__ == "__main__":
    main()