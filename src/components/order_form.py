import streamlit as st
from datetime import datetime
from src.models.restaurant import Order
import uuid

def render_order_creation(restaurant, scheduler, save_callback):
    """Formulario modular para crear nuevas órdenes."""
    st.subheader("📝 Tomar Pedido")
    
    with st.form("new_order_form"):
        # Selección de mesa
        available_tables = [t for t in restaurant.tables.values() if not t.is_occupied]
        table_choice = st.selectbox(
            "Seleccionar Mesa", 
            available_tables, 
            format_func=lambda t: f"Mesa {t.number} (Cap: {t.capacity})"
        )
        
        # Selección de platos múltiples
        st.write("---")
        st.write("**Selección del Menú**")
        selected_dishes = {}
        for dish_id, dish in restaurant.menu.items():
            qty = st.number_input(f"{dish.name} (${dish.price})", min_value=0, max_value=10, key=f"form_{dish_id}")
            if qty > 0:
                selected_dishes[dish_id] = qty
        
        submit = st.form_submit_button("Planificar y Confirmar")
        
        if submit:
            if not table_choice or not selected_dishes:
                st.error("Debes seleccionar una mesa y al menos un plato.")
                return

            new_order = Order(
                id=f"ORD-{uuid.uuid4().hex[:4].upper()}",
                table_id=table_choice.id,
                dishes=selected_dishes
            )
            new_order.total_price = new_order.calculate_total_price(restaurant.menu)
            
            success, msg, event = scheduler.schedule_order(new_order, datetime.now())
            
            if success:
                restaurant.add_order(new_order)
                st.success(f"¡Orden confirmada! {msg}")
                save_callback() # Guardamos los cambios
                st.rerun()
            else:
                st.error(f"Error de planificación: {msg}")