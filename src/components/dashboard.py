# src/components/dashboard.py
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import uuid
from src.models.restaurant import Restaurant, Order, EmployeeRole
from src.core.scheduler import EventScheduler

def _render_table_card(table_id: str, table, restaurant: Restaurant, scheduler: EventScheduler, save_callback) -> None:
    now = datetime.now()

    # Buscar evento actualmente activo o futuro para la mesa
    active_event = next((e for e in scheduler.scheduled_events
                         if e.table_id == table_id and e.start_time <= now <= e.end_time), None)
    is_occupied = active_event is not None or table.is_occupied

    event_to_display = active_event
    if not event_to_display and is_occupied:
        future_events = [e for e in scheduler.scheduled_events
                         if e.table_id == table_id and e.start_time > now]
        if future_events:
            event_to_display = min(future_events, key=lambda e: e.start_time)

    # 🎨 Diseño de Badges estilizados de estado
    if is_occupied:
        status_badge = (
            "<span style='background-color: rgba(231, 111, 81, 0.15); color: #e76f51; "
            "padding: 4px 10px; border-radius: 20px; font-size: 0.8rem; font-weight: bold; "
            "border: 1px solid rgba(231, 111, 81, 0.3);'>🔴 OCUPADA</span>"
        )
    else:
        status_badge = (
            "<span style='background-color: rgba(42, 157, 143, 0.15); color: #2a9d8f; "
            "padding: 4px 10px; border-radius: 20px; font-size: 0.8rem; font-weight: bold; "
            "border: 1px solid rgba(42, 157, 143, 0.3);'>🟢 DISPONIBLE</span>"
        )

    with st.container(border=True):
        # Encabezado de la mesa con capacidad alineada a la derecha
        c_head1, c_head2 = st.columns([1, 1])
        with c_head1:
            st.markdown(f"### 🪑 Mesa {table.number}")
        with c_head2:
            st.markdown(f"<p style='text-align: right; color: #888888; margin-top: 8px; font-size: 0.9rem;'>👥 Cap: <b>{table.capacity} pax</b></p>", unsafe_allow_html=True)

        # Renderizado del badge de estado
        st.markdown(f"<div style='margin-bottom: 20px;'>{status_badge}</div>", unsafe_allow_html=True)

        if not is_occupied:
            with st.popover("➕ Tomar Comanda", use_container_width=True):
                _render_order_popover(table, restaurant, scheduler, save_callback)
        else:
            with st.popover("🔍 Detalles de Servicio", use_container_width=True):
                if event_to_display:
                    chef = restaurant.employees.get(event_to_display.assigned_chef_id)
                    is_future = event_to_display.start_time > now
                    
                    if is_future:
                        st.caption("⏳ **Pedido Programado (Próximo)**")
                    else:
                        st.caption("🔥 **En Preparación (Activo)**")
                        
                    st.write(f"**Comanda:** `{event_to_display.order_id}`")
                    st.write(f"**Inicio:** {event_to_display.start_time.strftime('%H:%M:%S')}")
                    st.write(f"**Listo a las:** {event_to_display.end_time.strftime('%H:%M:%S')}")
                    st.write(f"**Chef asignado:** {chef.name if chef else 'N/A'}")
                    st.divider()
                    
                if st.button("❌ Liberar Mesa", key=f"can_t{table_id}", type="secondary", use_container_width=True):
                    if event_to_display:
                        scheduler.cancel_event(event_to_display.id)
                    else:
                        table.is_occupied = False
                    save_callback()
                    st.rerun()

def _render_order_popover(table, restaurant: Restaurant, scheduler: EventScheduler, save_callback) -> None:
    st.markdown("### 📝 Nueva Comanda")
    
    # 1. Buscador/Selector inteligente de platos (Corregido con clave única)
    dish_options = {dish.name: d_id for d_id, dish in restaurant.menu.items()}
    selected_dish_names = st.multiselect(
        "Selecciona los platos a ordenar:",
        options=list(dish_options.keys()),
        placeholder="Buscar platillos en el menú...",
        key=f"multiselect_dishes_{table.id}"
    )
    
    selected_dishes = {}
    customized_removals = {}

    if selected_dish_names:
        st.divider()
        for name in selected_dish_names:
            d_id = dish_options[name]
            dish = restaurant.menu[d_id]
            
            # Controles en columnas compactas por plato
            c1, c2 = st.columns([3, 2])
            with c1:
                st.markdown(f"**{dish.name}**  \n`Precio: ${dish.price:.2f}` | `Prep: {dish.prep_time} min`")
            with c2:
                qty = st.number_input(
                    "Cantidad:", min_value=1, max_value=10, value=1,
                    key=f"qty_t{table.id}_{d_id}"
                )
                selected_dishes[d_id] = qty

            # Personalización opcional de ingredientes
            optionals = [ing_id for ing_id in dish.ingredients.keys() if ing_id not in dish.base_ingredients]
            if optionals:
                with st.expander(f"Personalizar {dish.name} (Quitar ingredientes)"):
                    removed_list = []
                    for ing_id in optionals:
                        ing_obj = restaurant.ingredients.get(ing_id)
                        name_disp = ing_obj.name if ing_obj else ing_id
                        keep = st.checkbox(
                            f"Lleva {name_disp}", value=True,
                            key=f"chk_t{table.id}_{d_id}_{ing_id}"
                        )
                        if not keep:
                            removed_list.append(ing_id)
                    if removed_list:
                        customized_removals[d_id] = removed_list
        st.divider()
    else:
        st.info("Selecciona platos en el campo superior para armar la comanda.")

    if selected_dishes:
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Enviar a Cocina", key=f"btn_t{table.id}", type="primary", use_container_width=True):
                new_order = Order(
                    id=f"ORD-{uuid.uuid4().hex[:4].upper()}",
                    table_id=table.id,
                    dishes=selected_dishes,
                    customized_removals=customized_removals
                )
                success, msg, _ = scheduler.schedule_order(new_order, datetime.now())
                if success:
                    st.success("¡Pedido enviado a cocina!")
                    save_callback()
                    st.rerun()
                else:
                    st.error(msg)

        with col2:
            if st.button("⏱️ Buscar próximo hueco", key=f"find_slot_t{table.id}", use_container_width=True):
                new_order = Order(
                    id=f"ORD-{uuid.uuid4().hex[:4].upper()}",
                    table_id=table.id,
                    dishes=selected_dishes,
                    customized_removals=customized_removals
                )
                slot = scheduler.find_next_available_slot(new_order)
                if slot:
                    max_prep = max(restaurant.menu[d_id].prep_time for d_id in selected_dishes if restaurant.menu.get(d_id))
                    end_slot = slot + timedelta(minutes=max_prep)

                    st.session_state[f"pending_order_{table.id}"] = {
                        "order": new_order,
                        "slot": slot,
                        "end": end_slot
                    }
                    st.info(
                        f"**⏱️ Intervalo Sugerido:**  \n"
                        f"**Inicio:** {slot.strftime('%H:%M:%S')}  \n"
                        f"**Fin:** {end_slot.strftime('%H:%M:%S')}"
                    )
                else:
                    st.error("No hay disponibilidad en las próximas 24 horas.")

    # Flujo de confirmación para reservas agendadas fuera de hora
    pending_key = f"pending_order_{table.id}"
    if pending_key in st.session_state and st.session_state[pending_key]:
        pending = st.session_state[pending_key]
        order, slot, end_slot = pending["order"], pending["slot"], pending["end"]

        st.write("---")
        st.write(f"**¿Agendar pedido de {slot.strftime('%H:%M:%S')} a {end_slot.strftime('%H:%M:%S')}?**")
        if st.button("✅ Confirmar Agendamiento", key=f"confirm_slot_{table.id}", type="primary", use_container_width=True):
            success, msg, event = scheduler.schedule_order(order, slot)
            if success:
                st.success("¡Pedido reservado y agendado!")
                del st.session_state[pending_key]
                save_callback()
                st.rerun()
            else:
                st.error(msg)

def _render_chef_status(restaurant: Restaurant, scheduler: EventScheduler) -> None:
    now = datetime.now()
    chefs = [e for e in restaurant.employees.values() if e.role == EmployeeRole.CHEF]
    if chefs:
        chef_cols = st.columns(len(chefs))
        for idx, chef in enumerate(chefs):
            with chef_cols[idx]:
                is_working = any(e for e in scheduler.scheduled_events
                                 if e.assigned_chef_id == chef.id and e.start_time <= now <= e.end_time)
                
                chef.is_available = not is_working
                
                # 🎨 Badges estilizados de estado de los Chefs
                if is_working:
                    chef_badge = (
                        "<span style='background-color: rgba(231, 111, 81, 0.15); color: #e76f51; "
                        "padding: 3px 8px; border-radius: 4px; font-size: 0.75rem; font-weight: bold; "
                        "border: 1px solid rgba(231, 111, 81, 0.25);'>🔥 EN COCINA</span>"
                    )
                else:
                    chef_badge = (
                        "<span style='background-color: rgba(42, 157, 143, 0.15); color: #2a9d8f; "
                        "padding: 3px 8px; border-radius: 4px; font-size: 0.75rem; font-weight: bold; "
                        "border: 1px solid rgba(42, 157, 143, 0.25);'>🟢 DISPONIBLE</span>"
                    )
                
                # Fichas individuales estructuradas
                with st.container(border=True):
                    st.markdown(f"👨‍🍳 **{chef.name}**")
                    st.markdown(f"<span style='color: #888888; font-size: 0.85rem;'>{chef.experience.value.upper()}</span>", unsafe_allow_html=True)
                    st.markdown(f"<div style='margin-top: 8px; margin-bottom: 8px;'>{chef_badge}</div>", unsafe_allow_html=True)
                    if chef.specialties:
                        st.markdown(f"<p style='color: #a0a0a5; font-size: 0.8rem; margin: 0;'><b>Especialidad:</b> {', '.join(chef.specialties)}</p>", unsafe_allow_html=True)

def render_resource_status(restaurant: Restaurant, scheduler: EventScheduler, save_callback) -> None:
    now = datetime.now()
    
    # Liberación automática de recursos expirados
    for event in list(scheduler.scheduled_events):
        if event.end_time < now:
            table = restaurant.tables.get(event.table_id)
            if table:
                table.is_occupied = False
            chef = restaurant.employees.get(event.assigned_chef_id)
            if chef:
                chef.is_available = True
                chef.busy_until = None

    st.subheader("🍽️ Gestión de Sala en Tiempo Real")
    cols = st.columns(3)
    for i, (table_id, table) in enumerate(restaurant.tables.items()):
        with cols[i % 3]:
            _render_table_card(table_id, table, restaurant, scheduler, save_callback)

    st.divider()
    st.subheader("👨‍🍳 Staff en Cocina")
    _render_chef_status(restaurant, scheduler)

def render_event_timeline(scheduler: EventScheduler, save_callback) -> None:
    st.subheader("📅 Cronograma y Reserva de Turnos")
    
    if not scheduler.scheduled_events:
        st.info("No hay actividades o comandas agendadas en la planificación actual.")
    else:
        events_data = []
        now = datetime.now()
        
        # Mapear los eventos a un DataFrame para un despliegue profesional
        for event in scheduler.scheduled_events:
            chef = scheduler.restaurant.employees.get(event.assigned_chef_id)
            table = scheduler.restaurant.tables.get(event.table_id)
            
            is_active = event.start_time <= now <= event.end_time
            state_label = "🔥 En Preparación" if is_active else ("⏳ Esperando Turno" if event.start_time > now else "✅ Finalizado")
            
            events_data.append({
                "Comanda": event.order_id,
                "Mesa": f"Mesa {table.number if table else event.table_id}",
                "Chef": chef.name if chef else "N/A",
                "Hora Inicio": event.start_time.strftime("%H:%M:%S"),
                "Hora Fin": event.end_time.strftime("%H:%M:%S"),
                "Estado": state_label
            })
            
        df = pd.DataFrame(events_data)
        
        # Renderizar la tabla de datos estructurada e interactiva nativa de Streamlit
        st.dataframe(
            df, 
            use_container_width=True, 
            hide_index=True,
            column_config={
                "Comanda": st.column_config.TextColumn("ID Comanda"),
                "Estado": st.column_config.TextColumn("Estado del Proceso", help="Estado en tiempo real según el reloj del sistema")
            }
        )