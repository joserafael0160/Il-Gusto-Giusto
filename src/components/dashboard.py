import streamlit as st
from datetime import datetime

def render_resource_status(restaurant):
    st.subheader("📊 Estado de Operaciones")
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("#### 🪑 Mesas")
        t_cols = st.columns(2)
        for i, table in enumerate(restaurant.tables.values()):
            with t_cols[i % 2]:
                status = "🔴 Ocupada" if table.is_occupied else "🟢 Libre"
                st.info(f"**Mesa {table.number}**\n\nStatus: {status}")

    with col2:
        st.write("#### 👨‍🍳 Staff de Cocina")
        for employee in restaurant.employees.values():
            if employee.is_available:
                st.success(f"**{employee.name}** - Disponible")
            else:
                st.warning(f"**{employee.name}** - Ocupado")

def render_event_timeline(scheduler, save_callback):
    """Muestra eventos y permite eliminarlos"""
    st.subheader("📅 Cronograma de Pedidos")
    events = scheduler.scheduled_events
    
    if not events:
        st.info("No hay pedidos en curso.")
    else:
        for event in events:
            # Creamos un contenedor para cada evento con un botón de eliminar
            with st.expander(f"Orden {event.order_id} - Mesa {event.table_id}"):
                col_text, col_btn = st.columns([4, 1])
                with col_text:
                    st.write(f"**Chef:** {event.assigned_chef_id}")
                    st.write(f"**Horario:** {event.start_time.strftime('%H:%M')} a {event.end_time.strftime('%H:%M')}")
                with col_btn:
                    if st.button("❌ Eliminar", key=f"del_{event.id}"):
                        success, msg = scheduler.cancel_event(event.id)
                        if success:
                            save_callback()
                            st.rerun()

def render_resource_agenda(events, restaurant):
    """Requerimiento: Ver detalles/agenda de un recurso específico"""
    st.subheader("📑 Agenda por Recurso")
    
    resource_type = st.radio("Filtrar agenda por:", ["Chefs", "Mesas"], horizontal=True)
    
    if resource_type == "Chefs":
        chef_id = st.selectbox("Seleccionar Chef", options=list(restaurant.employees.keys()), 
                               format_func=lambda x: restaurant.employees[x].name)
        chef_events = [e for e in events if e.assigned_chef_id == chef_id]
        if not chef_events:
            st.caption("Este chef no tiene eventos programados.")
        for e in chef_events:
            st.write(f"• **{e.start_time.strftime('%H:%M')} - {e.end_time.strftime('%H:%M')}**: Orden {e.order_id}")
            
    else:
        table_id = st.selectbox("Seleccionar Mesa", options=list(restaurant.tables.keys()), 
                                format_func=lambda x: f"Mesa {restaurant.tables[x].number}")
        table_events = [e for e in events if e.table_id == table_id]
        if not table_events:
            st.caption("Esta mesa no tiene reservas.")
        for e in table_events:
            st.write(f"• **{e.start_time.strftime('%H:%M')} - {e.end_time.strftime('%H:%M')}**: Ocupada (Orden {e.order_id})")