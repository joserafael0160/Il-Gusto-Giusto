import streamlit as st
from datetime import datetime
import uuid
from src.models.restaurant import Order, Restaurant
from src.core.scheduler import EventScheduler

def render_resource_status(restaurant: Restaurant, scheduler: EventScheduler, save_callback):
    now = datetime.now()

    # Sincronización en tiempo real al renderizar
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
            active_event = next((e for e in scheduler.scheduled_events
                               if e.table_id == table_id and e.start_time <= now <= e.end_time), None)

            is_occupied = active_event is not None or table.is_occupied
            status_color = "red" if is_occupied else "green"
            status_label = "OCUPADA" if is_occupied else "DISPONIBLE"

            with st.container(border=True):
                st.markdown(f"### Mesa {table.number}")
                st.markdown(f":{status_color}[**{status_label}**] | Capacidad: {table.capacity}")

                if not is_occupied:
                    with st.popover("➕ Tomar Comanda", use_container_width=True):
                        st.write("📝 **Nuevo Pedido**")
                        selected_dishes = {}
                        customized_removals = {}

                        for d_id, dish in restaurant.menu.items():
                            qty = st.number_input(f"{dish.name} (${dish.price:.2f})", min_value=0, max_value=10, key=f"t{table_id}_{d_id}")
                            if qty > 0:
                                selected_dishes[d_id] = qty

                                # Opcionales
                                optionals = [ing_id for ing_id in dish.ingredients.keys() if ing_id not in dish.base_ingredients]
                                if optionals:
                                    st.caption(f"Ingredientes opcionales para {dish.name}:")
                                    removed_list = []
                                    for ing_id in optionals:
                                        ing_obj = restaurant.ingredients.get(ing_id)
                                        name_disp = ing_obj.name if ing_obj else ing_id
                                        keep = st.checkbox(f"Lleva {name_disp}", value=True, key=f"chk_t{table_id}_{d_id}_{ing_id}")
                                        if not keep:
                                            removed_list.append(ing_id)
                                    if removed_list:
                                        customized_removals[d_id] = removed_list

                        if st.button("Enviar a Cocina", key=f"btn_t{table_id}", type="primary"):
                            if selected_dishes:
                                new_order = Order(
                                    id=f"ORD-{uuid.uuid4().hex[:4].upper()}",
                                    table_id=table_id,
                                    dishes=selected_dishes,
                                    customized_removals=customized_removals
                                )
                                success, msg, _ = scheduler.schedule_order(new_order, datetime.now())
                                if success:
                                    st.success("¡Pedido despachado!")
                                    save_callback()
                                    st.rerun()
                                else:
                                    st.error(msg)
                            else:
                                st.warning("Debes seleccionar al menos un plato.")
                else:
                    with st.popover("🔍 Detalles del Pedido", use_container_width=True):
                        if active_event:
                            chef = restaurant.employees.get(active_event.assigned_chef_id)
                            st.write(f"**Referencia:** `{active_event.order_id}`")
                            st.write(f"**Listo a las:** {active_event.end_time.strftime('%H:%M:%S')}")
                            st.write(f"**Cocinando:** {chef.name if chef else 'N/A'}")
                            st.divider()
                        if st.button("❌ Terminar Servicio / Cancelar", key=f"can_t{table_id}", type="secondary"):
                            if active_event:
                                scheduler.cancel_event(active_event.id)
                            else:
                                table.is_occupied = False
                            save_callback()
                            st.rerun()

    st.divider()
    st.subheader("👨‍🍳 Staff en Cocina")
    chefs = [e for e in restaurant.employees.values() if e.role.value == "chef"]
    if chefs:
        chef_cols = st.columns(len(chefs))
        for idx, chef in enumerate(chefs):
            with chef_cols[idx]:
                is_working = any(e for e in scheduler.scheduled_events
                               if e.assigned_chef_id == chef.id and e.start_time <= now <= e.end_time)
                status_text = "En los Fogones" if is_working else "Disponible"
                icon = "🔴" if is_working else "🟢"
                chef.is_available = not is_working

                st.metric(label=f"{chef.name} ({chef.experience.value.capitalize()})", value=status_text, delta=icon, delta_color="normal")
                if chef.specialties:
                    st.caption(f"Especialidad: {', '.join(chef.specialties)}")

def render_event_timeline(scheduler: EventScheduler, save_callback):
    with st.expander("📅 Cronograma de Cocina"):
        if not scheduler.scheduled_events:
            st.info("No hay actividades registradas en la cocina.")
        else:
            for event in scheduler.scheduled_events:
                st.write(
                    f"**Mesa:** {event.table_id} | "
                    f"**Chef:** {event.assigned_chef_id} | "
                    f"**Intervalo:** {event.start_time.strftime('%H:%M:%S')} - {event.end_time.strftime('%H:%M:%S')}"
                )