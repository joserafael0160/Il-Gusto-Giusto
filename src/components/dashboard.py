import streamlit as st
from datetime import datetime
import uuid

def render_resource_status(restaurant, scheduler, save_callback):
    st.subheader("🍽️ Gestión de Sala en Tiempo Real")
    
    # Grid de Mesas (4 columnas para que se vean grandes pero organizadas)
    cols = st.columns(4)
    
    for i, (table_id, table) in enumerate(restaurant.tables.items()):
        with cols[i % 4]:
            # Buscamos si hay un evento activo para esta mesa
            active_event = next((e for e in scheduler.scheduled_events if e.table_id == table_id), None)
            
            # Definimos el estilo visual
            status_color = "red" if table.is_occupied else "green"
            status_label = "OCUPADA" if table.is_occupied else "LIBRE"
            
            # --- TARJETA DE MESA ---
            with st.container(border=True):
                st.markdown(f"### Mesa {table.number}")
                st.markdown(f":{status_color}[**{status_label}**] | Capacidad: {table.capacity}")
                
                # Usamos popover para la interactividad al "tocar/clicar"
                if not table.is_occupied:
                    with st.popover("➕ Nuevo Pedido", use_container_width=True):
                        st.write("📝 **Tomar Comanda**")
                        selected_dishes = {}
                        for d_id, dish in restaurant.menu.items():
                            qty = st.number_input(f"{dish.name} (${dish.price})", 0, 10, key=f"t{table_id}_{d_id}")
                            if qty > 0: selected_dishes[d_id] = qty
                        
                        if st.button("Confirmar Pedido", key=f"btn_{table_id}", type="primary"):
                            if selected_dishes:
                                # Importamos Order aquí para evitar circulares
                                from src.models.restaurant import Order
                                new_order = Order(id=f"ORD-{uuid.uuid4().hex[:4].upper()}", table_id=table_id, dishes=selected_dishes)
                                success, msg, _ = scheduler.schedule_order(new_order, datetime.now())
                                if success:
                                    save_callback()
                                    st.success("¡Buen provecho!")
                                    st.rerun()
                                else:
                                    st.error(msg)
                else:
                    # MESA OCUPADA: Mostrar detalles y opción de cancelar
                    with st.popover("🔍 Ver Detalles", use_container_width=True):
                        if active_event:
                            chef_name = restaurant.employees.get(active_event.assigned_chef_id).name
                            st.write(f"**⏰ Horario:** {active_event.start_time.strftime('%H:%M')} - {active_event.end_time.strftime('%H:%M')}")
                            st.write(f"**👨‍🍳 Chef:** {chef_name}")
                            st.write(f"**🆔 Orden:** {active_event.order_id}")
                            
                            st.divider()
                            if st.button("❌ Cancelar Pedido", key=f"can_{active_event.id}", type="secondary"):
                                scheduler.cancel_event(active_event.id)
                                save_callback()
                                st.rerun()

    st.divider()
    # Sección de Chefs más compacta
    st.subheader("👨‍🍳 Staff de Cocina")
    chef_cols = st.columns(len(restaurant.employees))
    for i, chef in enumerate(restaurant.employees.values()):
        with chef_cols[i]:
            icon = "🟢" if chef.is_available else "🔴"
            st.metric(label=chef.name, value="Disponible" if chef.is_available else "En Cocina", delta=icon, delta_color="normal")

# Mantenemos las otras funciones pero las simplificamos porque ya hay mucha info arriba
def render_event_timeline(scheduler, save_callback):
    with st.expander("📅 Ver Cronograma Completo"):
        for event in scheduler.scheduled_events:
            st.write(f"**Mesa {event.table_id}** | {event.start_time.strftime('%H:%M')} -> {event.end_time.strftime('%H:%M')} | Chef: {event.assigned_chef_id}")

def render_resource_agenda(events, restaurant):
    # (Se mantiene igual a tu versión anterior o puedes integrarla en el popover de arriba)
    pass