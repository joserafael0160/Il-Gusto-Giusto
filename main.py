import streamlit as st
import sys
from pathlib import Path
from datetime import datetime
import os
# En main.py o json_handler.py
if not os.path.exists("data"):
    os.makedirs("data")
# Rutas
ROOT_DIR = Path(__file__).parent
sys.path.append(str(ROOT_DIR / "src"))

from src.core.scheduler import EventScheduler
from src.persistence.json_handler import JSONHandler
from src.components.dashboard import render_resource_agenda, render_resource_status, render_event_timeline
from src.components.order_form import render_order_creation

def save_all():
    JSONHandler.save_restaurant(
        st.session_state.restaurant,
        st.session_state.scheduler.scheduled_events,
        "data/restaurant_state.json"
    )

def init_state():
    if 'restaurant' not in st.session_state:
        rest, events = JSONHandler.load_restaurant("data/restaurant_state.json")
        if not rest:
            # Si no existe el JSON, el JSONHandler debería crear uno por defecto
            # o cargar uno desde un archivo semilla.
            st.error("No se pudo cargar el estado inicial.")
            return
            
        st.session_state.restaurant = rest
        st.session_state.scheduler = EventScheduler(rest)
        st.session_state.scheduler.scheduled_events = events
        
        # Sincronización de tiempo real al arrancar
        now = datetime.now()
        for event in events:
            if event.end_time < now:
                table = rest.tables.get(event.table_id)
                if table: table.is_occupied = False
                chef = rest.employees.get(event.assigned_chef_id)
                if chef: 
                    chef.is_available = True
                    chef.busy_until = None
        st.session_state.scheduler.scheduled_events = [e for e in events if e.end_time > now]

def main():
    st.set_page_config(page_title="El Dragón del Sabor", page_icon="🐉", layout="wide")
    init_state()
    
    st.title("🐉 El Dragón del Sabor")
    
    # Sidebar para navegación
    menu = st.sidebar.radio("Navegación", ["Dashboard", "Pedidos", "Inventario"])
    
    if menu == "Dashboard":
        # 1. Estado general (Visual)
        render_resource_status(st.session_state.restaurant)
        
        st.divider()
        
        # 2. Línea de tiempo y Eliminación (Operacional)
        render_event_timeline(st.session_state.scheduler, save_all)
        
        st.divider()
        
        # 3. La Agenda detallada (Requerimiento de consulta)
        render_resource_agenda(
            st.session_state.scheduler.scheduled_events, 
            st.session_state.restaurant
        )
        
    elif menu == "Pedidos":
        render_order_creation(st.session_state.restaurant, st.session_state.scheduler, save_all)
        
    elif menu == "Inventario":
        st.write("### 🍱 Gestión de Stock")
        st.table(st.session_state.restaurant.ingredients)

if __name__ == "__main__":
    main()