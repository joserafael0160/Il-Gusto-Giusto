import streamlit as st
from datetime import datetime
import uuid

def render_resource_status(restaurant, scheduler, save_callback):
    # --- 1. SINCRONIZACIÓN AUTOMÁTICA ---
    # Esto asegura que si un evento terminó, los recursos se vean libres de inmediato
    now = datetime.now()
    for event in scheduler.scheduled_events:
        if event.end_time < now:
            # Liberar mesa y chef internamente
            table = restaurant.tables.get(event.table_id)
            if table: table.is_occupied = False
            chef = restaurant.employees.get(event.assigned_chef_id)
            if chef: chef.is_available = True
            
    
    st.subheader("🍽️ Gestión de Sala en Tiempo Real")
    
    # Grid de Mesas
    cols = st.columns(4)
    for i, (table_id, table) in enumerate(restaurant.tables.items()):
        with cols[i % 4]:
            # Buscamos evento activo EXACTAMENTE ahora para esta mesa
            active_event = next((e for e in scheduler.scheduled_events 
                               if e.table_id == table_id and e.start_time <= now <= e.end_time), None)
            
            # Forzamos coherencia: si hay evento, está ocupada; si no, libre.
            is_occupied = active_event is not None
            status_color = "red" if is_occupied else "green"
            status_label = "OCUPADA" if is_occupied else "LIBRE"
            
            with st.container(border=True):
                st.markdown(f"### Mesa {table.number}")
                st.markdown(f":{status_color}[**{status_label}**] | Capacidad: {table.capacity}")
                
                if not is_occupied:
                    with st.popover("➕ Nuevo Pedido", use_container_width=True):
                        st.write("📝 **Tomar Comanda**")
                        selected_dishes = {}
                        for d_id, dish in restaurant.menu.items():
                            qty = st.number_input(f"{dish.name} (${dish.price})", 0, 10, key=f"t{table_id}_{d_id}")
                            if qty > 0: selected_dishes[d_id] = qty
                        
                        if st.button("Confirmar", key=f"btn_{table_id}", type="primary"):
                            if selected_dishes:
                                from src.models.restaurant import Order
                                new_order = Order(id=f"ORD-{uuid.uuid4().hex[:4].upper()}", 
                                                table_id=table_id, dishes=selected_dishes)
                                success, msg, _ = scheduler.schedule_order(new_order, datetime.now())
                                if success:
                                    save_callback()
                                    st.rerun()
                                else:
                                    st.error(msg)
                else:
                    with st.popover("🔍 Ver Detalles", use_container_width=True):
                        if active_event:
                            chef = restaurant.employees.get(active_event.assigned_chef_id)
                            st.write(f"**⏰ Fin:** {active_event.end_time.strftime('%H:%M')}")
                            st.write(f"**👨‍🍳 Chef:** {chef.name if chef else 'N/A'}")
                            st.divider()
                            if st.button("❌ Liberar Mesa", key=f"can_{active_event.id}", type="secondary"):
                                scheduler.cancel_event(active_event.id)
                                save_callback()
                                st.rerun()

    st.divider()
    
    # --- 2. SECCIÓN DE CHEFS  ---
    st.subheader("👨‍🍳 Staff de Cocina")
    chef_cols = st.columns(len(restaurant.employees))
    for i, chef in enumerate(restaurant.employees.values()):
        with chef_cols[i]:
            # Un chef está trabajando si tiene un evento asignado en este momento
            is_working = any(e for e in scheduler.scheduled_events 
                           if e.assigned_chef_id == chef.id and e.start_time <= now <= e.end_time)
            
            status_text = "En Cocina" if is_working else "Disponible"
            icon = "🔴" if is_working else "🟢"
            # Actualizamos el estado real del objeto para el scheduler
            chef.is_available = not is_working
            
            st.metric(label=chef.name, value=status_text, delta=icon, delta_color="normal")

def render_event_timeline(scheduler, save_callback):
    with st.expander("📅 Ver Cronograma Completo"):
        if not scheduler.scheduled_events:
            st.info("No hay eventos programados.")
        else:
            for event in scheduler.scheduled_events:
                st.write(f"**Mesa {event.table_id}** | {event.start_time.strftime('%H:%M')} a {event.end_time.strftime('%H:%M')}")
