import streamlit as st
from datetime import datetime, timedelta
import uuid
from src.models.restaurant import Restaurant, Order, EmployeeRole
from src.core.scheduler import EventScheduler

def _render_table_card(table_id, table, restaurant, scheduler, save_callback):
    now = datetime.now()

    # Buscar evento actualmente en ejecución
    active_event = next((e for e in scheduler.scheduled_events
                         if e.table_id == table_id and e.start_time <= now <= e.end_time), None)
    is_occupied = active_event is not None or table.is_occupied

    # Determinar el evento a mostrar (activo o el próximo futuro si la mesa está ocupada)
    event_to_display = active_event
    if not event_to_display and is_occupied:
        future_events = [e for e in scheduler.scheduled_events
                         if e.table_id == table_id and e.start_time > now]
        if future_events:
            event_to_display = min(future_events, key=lambda e: e.start_time)

    status_color = "red" if is_occupied else "green"
    status_label = "OCUPADA" if is_occupied else "DISPONIBLE"

    with st.container(border=True):
        st.markdown(f"### Mesa {table.number}")
        st.markdown(f":{status_color}[**{status_label}**] | Capacidad: {table.capacity}")

        if not is_occupied:
            with st.popover("➕ Tomar Comanda", use_container_width=True):
                _render_order_popover(table, restaurant, scheduler, save_callback)
        else:
            with st.popover("🔍 Detalles del Pedido", use_container_width=True):
                if event_to_display:
                    chef = restaurant.employees.get(event_to_display.assigned_chef_id)
                    es_futuro = event_to_display.start_time > now
                    if es_futuro:
                        st.caption("⏳ **Pedido programado**")
                    else:
                        st.caption("🔥 **En preparación**")
                    st.write(f"**Comanda:** {event_to_display.order_id}")
                    st.write(f"**Inicio:** {event_to_display.start_time.strftime('%H:%M:%S')}")
                    st.write(f"**Listo a las:** {event_to_display.end_time.strftime('%H:%M:%S')}")
                    st.write(f"**Chef a cargo:** {chef.name if chef else 'N/A'}")
                    st.divider()
                if st.button("❌ Cancelar / Terminar", key=f"can_t{table_id}", type="secondary"):
                    if event_to_display:
                        scheduler.cancel_event(event_to_display.id)
                    else:
                        table.is_occupied = False
                    save_callback()
                    st.rerun()

def _render_order_popover(table, restaurant, scheduler, save_callback):
    st.write("📝 **Nuevo Pedido**")
    selected_dishes = {}
    customized_removals = {}

    for d_id, dish in restaurant.menu.items():
        qty = st.number_input(
            f"{dish.name} (${dish.price:.2f})", min_value=0, max_value=10,
            key=f"t{table.id}_{d_id}"
        )
        if qty > 0:
            selected_dishes[d_id] = qty
            optionals = [ing_id for ing_id in dish.ingredients.keys()
                         if ing_id not in dish.base_ingredients]
            if optionals:
                st.caption(f"Ingredientes opcionales para {dish.name}:")
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

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Enviar a Cocina", key=f"btn_t{table.id}", type="primary"):
            if selected_dishes:
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
            else:
                st.warning("Selecciona al menos un plato.")

    with col2:
        if st.button("🔎 Buscar y agendar en próximo hueco", key=f"find_slot_t{table.id}"):
            if selected_dishes:
                new_order = Order(
                    id=f"ORD-{uuid.uuid4().hex[:4].upper()}",
                    table_id=table.id,
                    dishes=selected_dishes,
                    customized_removals=customized_removals
                )
                slot = scheduler.find_next_available_slot(new_order)
                if slot:
                    # Calcular la duración total (plato más lento)
                    max_prep = 0
                    for d_id in selected_dishes:
                        dish = restaurant.menu.get(d_id)
                        if dish and dish.prep_time > max_prep:
                            max_prep = dish.prep_time
                    end_slot = slot + timedelta(minutes=max_prep)

                    # Guardar en session_state para el paso de confirmación
                    st.session_state[f"pending_order_{table.id}"] = {
                        "order": new_order,
                        "slot": slot,
                        "end": end_slot
                    }
                    st.info(
                        f"⏱️ Hueco disponible:\n\n"
                        f"**Inicio:** {slot.strftime('%H:%M:%S')}\n\n"
                        f"**Fin:** {end_slot.strftime('%H:%M:%S')}"
                    )
                else:
                    st.error("No hay disponibilidad en las próximas 24 horas.")
            else:
                st.warning("Elige platos primero.")

    # ─── Paso de confirmación ───
    pending_key = f"pending_order_{table.id}"
    if pending_key in st.session_state and st.session_state[pending_key]:
        pending = st.session_state[pending_key]
        order, slot, end_slot = pending["order"], pending["slot"], pending["end"]

        st.write("---")
        st.write(f"**¿Agendar este pedido de {slot.strftime('%H:%M:%S')} a {end_slot.strftime('%H:%M:%S')}?**")
        if st.button("✅ Confirmar agendamiento", key=f"confirm_slot_{table.id}", type="primary"):
            success, msg, event = scheduler.schedule_order(order, slot)
            if success:
                chef = restaurant.employees.get(event.assigned_chef_id)
                st.success(
                    f"✅ **Pedido agendado**\n\n"
                    f"**Chef:** {chef.name if chef else 'N/A'}\n\n"
                    f"**Inicio:** {event.start_time.strftime('%H:%M:%S')}\n\n"
                    f"**Fin:** {event.end_time.strftime('%H:%M:%S')}"
                )
                del st.session_state[pending_key]
                save_callback()
                st.rerun()
            else:
                st.error(msg)

def _render_chef_status(restaurant, scheduler):
    now = datetime.now()
    chefs = [e for e in restaurant.employees.values() if e.role == EmployeeRole.CHEF]
    if chefs:
        chef_cols = st.columns(len(chefs))
        for idx, chef in enumerate(chefs):
            with chef_cols[idx]:
                is_working = any(e for e in scheduler.scheduled_events
                                 if e.assigned_chef_id == chef.id and e.start_time <= now <= e.end_time)
                status_text = "En los fogones" if is_working else "Disponible"
                icon = "🔴" if is_working else "🟢"
                chef.is_available = not is_working
                st.metric(label=f"{chef.name} ({chef.experience.value.capitalize()})",
                          value=status_text, delta=icon, delta_color="normal")
                if chef.specialties:
                    st.caption(f"Especialidad: {', '.join(chef.specialties)}")

def render_resource_status(restaurant: Restaurant, scheduler: EventScheduler, save_callback):
    now = datetime.now()
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

def render_event_timeline(scheduler: EventScheduler, save_callback):
    with st.expander("📅 Cronograma de Cocina"):
        if not scheduler.scheduled_events:
            st.info("No hay actividades registradas.")
        else:
            for event in scheduler.scheduled_events:
                st.write(
                    f"**Mesa:** {event.table_id} | "
                    f"**Chef:** {event.assigned_chef_id} | "
                    f"**Intervalo:** {event.start_time.strftime('%H:%M:%S')} - {event.end_time.strftime('%H:%M:%S')}"
                )