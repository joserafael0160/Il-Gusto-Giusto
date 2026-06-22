import streamlit as st
import sys
from pathlib import Path
from datetime import datetime
import os

if not os.path.exists("data"):
    os.makedirs("data")

# Rutas
ROOT_DIR = Path(__file__).parent
sys.path.append(str(ROOT_DIR / "src"))

from src.core.scheduler import EventScheduler
from src.persistence.json_handler import JSONHandler
from src.components.dashboard import render_resource_status, render_event_timeline


def init_state():
    if 'restaurant' not in st.session_state:
        rest, events = JSONHandler.load_restaurant("data/restaurant_state.json")
        
        # --- LÓGICA DE AUTO-LIMPIEZA AL ARRANCAR ---
        now = datetime.now()
        
        # 1. Por defecto, ponemos todas las mesas como libres
        for table in rest.tables.values():
            table.is_occupied = False
            
        # 2. Solo marcamos como ocupadas las que tienen eventos ACTIVOS ahora mismo
        active_events = []
        for event in events:
            if event.start_time <= now <= event.end_time:
                table = rest.tables.get(event.table_id)
                if table: table.is_occupied = True
                active_events.append(event)
            elif event.end_time > now:
                # Mantener eventos futuros en la lista, pero no ocupan la mesa todavía
                active_events.append(event)
        
        st.session_state.restaurant = rest
        st.session_state.scheduler = EventScheduler(rest)
        st.session_state.scheduler.scheduled_events = active_events
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
    




    # Sidebar optimizada
    menu = st.sidebar.radio("Navegación", ["Dashboard", "Inventario"])
    
    if menu == "Dashboard":
        # Todo ocurre aquí ahora: Ver, Pedir y Cancelar
        render_resource_status(st.session_state.restaurant, st.session_state.scheduler, save_all)
        
        st.divider()
        render_event_timeline(st.session_state.scheduler, save_all)
        
    elif menu == "Inventario":
        st.subheader("🍱 Gestión de Stock")
        # Podemos mejorar esto luego con una UI similar a las mesas para los ingredientes
        st.table(st.session_state.restaurant.ingredients)
if __name__ == "__main__":
    main()



