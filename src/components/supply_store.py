# src/components/supply_store.py
import streamlit as st
from src.models.restaurant import Restaurant
from src.services.restaurant_service import RestaurantService

STOCK_BADGES = {
    "empty": "<span style='background-color: rgba(231, 111, 81, 0.15); color: #e76f51; padding: 3px 8px; border-radius: 4px; font-size: 0.75rem; font-weight: bold; border: 1px solid rgba(231, 111, 81, 0.25);'>🔴 AGOTADO</span>",
    "low": "<span style='background-color: rgba(233, 196, 106, 0.15); color: #e9c46a; padding: 3px 8px; border-radius: 4px; font-size: 0.75rem; font-weight: bold; border: 1px solid rgba(233, 196, 106, 0.25);'>⚠️ STOCK CRÍTICO</span>",
    "stable": "<span style='background-color: rgba(42, 157, 143, 0.15); color: #2a9d8f; padding: 3px 8px; border-radius: 4px; font-size: 0.75rem; font-weight: bold; border: 1px solid rgba(42, 157, 143, 0.25);'>🟢 SUFICIENTE</span>"
}

def render_store_and_stock(restaurant: Restaurant, save_callback) -> None:
    st.subheader("🛒 Despensa de Suministros e Inventario")

    # Mostrar alerta de compra anterior si existe
    if "purchase_alert" in st.session_state and st.session_state.purchase_alert:
        alert = st.session_state.purchase_alert
        if alert["type"] == "success":
            st.success(alert["msg"])
        elif alert["type"] == "error":
            st.error(alert["msg"])
        del st.session_state.purchase_alert

    # Contador para reiniciar cantidades tras compra exitosa
    if "purchase_counter" not in st.session_state:
        st.session_state.purchase_counter = 0

    low_stock_items = [ing for ing in restaurant.ingredients.values() if ing.quantity <= ing.min_quantity]
    
    if low_stock_items:
        alert_msg = "⚠️ **Alerta de Insumos Críticos:** Las siguientes materias primas están por debajo del mínimo recomendado:\n\n"
        for ing in low_stock_items:
            alert_msg += f"- **{ing.name}**: `{ing.quantity:.2f} {ing.unit}` (Mínimo: `{ing.min_quantity:.2f}`)\n"
        st.warning(alert_msg)
    else:
        st.success("✅ Todos los suministros se encuentran estables en la despensa.")

    if "store_active_tab" not in st.session_state:
        st.session_state.store_active_tab = "store"

    col_tab1, col_tab2 = st.columns(2)
    with col_tab1:
        is_pantry = st.session_state.store_active_tab == "pantry"
        if st.button("📦 Existencias en Almacén", key="btn_subtab_pantry", width='stretch', type="primary" if is_pantry else "secondary"):
            st.session_state.store_active_tab = "pantry"
            st.rerun()

    with col_tab2:
        is_store = st.session_state.store_active_tab == "store"
        if st.button("🛍️ Comprar Suministros (Mayorista)", key="btn_subtab_store", width='stretch', type="primary" if is_store else "secondary"):
            st.session_state.store_active_tab = "store"
            st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)

    if st.session_state.store_active_tab == "pantry":
        st.markdown("### Inventario de Materias Primas")
        st.markdown("<p style='color: gray;'>Visualización de existencias ordenadas por prioridad de urgencia.</p>", unsafe_allow_html=True)

        critical_items = [ing for ing in restaurant.ingredients.values() if ing.quantity <= ing.min_quantity]
        healthy_items = [ing for ing in restaurant.ingredients.values() if ing.quantity > ing.min_quantity]

        if critical_items:
            st.markdown("#### 🚨 Reabastecimiento Requerido")
            for ing in critical_items:
                with st.container(border=True):
                    col_name, col_progress, col_badge = st.columns([3, 4, 2])
                    with col_name:
                        st.markdown(f"**{ing.name}**")
                        st.caption(f"Actual: `{ing.quantity:.2f} {ing.unit}` / Mínimo: `{ing.min_quantity:.2f} {ing.unit}`")
                    with col_progress:
                        percentage = min(1.0, max(0.0, ing.quantity / max(1.0, ing.min_quantity * 3.0)))
                        st.markdown("<div style='margin-top: 5px;'></div>", unsafe_allow_html=True)
                        st.progress(percentage)
                    with col_badge:
                        badge_html = STOCK_BADGES["empty"] if ing.quantity <= 0 else STOCK_BADGES["low"]
                        st.markdown(f"<div style='margin-top: 10px; text-align: right;'>{badge_html}</div>", unsafe_allow_html=True)

        if healthy_items:
            st.markdown("#### ✅ Niveles Estables")
            for ing in healthy_items:
                with st.container(border=True):
                    col_name, col_progress, col_badge = st.columns([3, 4, 2])
                    with col_name:
                        st.markdown(f"**{ing.name}**")
                        st.caption(f"Actual: `{ing.quantity:.2f} {ing.unit}` / Mínimo: `{ing.min_quantity:.2f} {ing.unit}`")
                    with col_progress:
                        percentage = min(1.0, max(0.0, ing.quantity / max(1.0, ing.min_quantity * 3.0)))
                        st.markdown("<div style='margin-top: 5px;'></div>", unsafe_allow_html=True)
                        st.progress(percentage)
                    with col_badge:
                        st.markdown(f"<div style='margin-top: 10px; text-align: right;'>{STOCK_BADGES['stable']}</div>", unsafe_allow_html=True)

    else:
        col_balance1, col_balance2 = st.columns([2, 1])
        with col_balance1:
            st.markdown("### Pedido Mayorista por Lotes")
            st.markdown("<p style='color: gray;'>Ajusta las cantidades que deseas de cada ingrediente y procesa la compra.</p>", unsafe_allow_html=True)
        with col_balance2:
            st.metric(label="💰 Capital Disponible", value=f"${restaurant.balance:,.2f}")
            
        st.divider()

        # --- Pedido interactivo (sin formulario) ---
        order_quantities = {}
        for ing_id, ing in restaurant.ingredients.items():
            with st.container(border=True):
                col_name, col_qty, col_subtotal = st.columns([3, 2, 2])
                with col_name:
                    st.markdown(f"#### {ing.name}")
                    st.caption(f"Costo mayorista: **${ing.price_per_unit:.2f}** / `{ing.unit}`")
                    st.caption(f"Inventario actual: `{ing.quantity:.2f} {ing.unit}`")
                with col_qty:
                    qty = st.number_input(
                        f"Cantidad a pedir ({ing.unit}):", 
                        min_value=0.0, 
                        max_value=100.0, 
                        step=1.0, 
                        key=f"bulk_qty_{ing_id}_{st.session_state.purchase_counter}"
                    )
                    order_quantities[ing_id] = qty
                with col_subtotal:
                    subtotal = qty * ing.price_per_unit
                    st.markdown(f"<p style='text-align: right; margin-top: 25px; font-size: 1.05rem;'>Subtotal: <b>${subtotal:.2f}</b></p>", unsafe_allow_html=True)

        # Total y resumen (ahora sí se actualizan en tiempo real)
        total_invoice_cost = sum(order_quantities[ing_id] * ing.price_per_unit for ing_id, ing in restaurant.ingredients.items())

        if total_invoice_cost > 0:
            st.markdown("---")
            with st.container(border=True):
                st.markdown("### 📋 Resumen del Pedido Consolidado")
                for ing_id, qty in order_quantities.items():
                    if qty > 0:
                        ing = restaurant.ingredients[ing_id]
                        cost = qty * ing.price_per_unit
                        st.markdown(f"- **{ing.name}**: `{qty} {ing.unit}` &nbsp;&bull;&nbsp; **${cost:.2f}**")
                
                st.divider()
                col_res1, col_res2 = st.columns([2, 1])
                with col_res1:
                    st.markdown(f"## Total de Compra: `${total_invoice_cost:,.2f}`")
                with col_res2:
                    st.markdown("<div style='margin-top: 5px;'></div>", unsafe_allow_html=True)
                    if restaurant.balance < total_invoice_cost:
                        st.error("Capital Insuficiente")
                    else:
                        if st.button("Procesar Pedido Completo", key="process_purchase_btn", type="primary", width='stretch'):
                            success, message = RestaurantService.purchase_ingredients(restaurant, order_quantities)
                            if success:
                                st.session_state.purchase_alert = {"type": "success", "msg": message}
                                st.session_state.purchase_counter += 1  # Reinicia inputs
                                save_callback()
                                st.rerun()
                            else:
                                st.session_state.purchase_alert = {"type": "error", "msg": message}
                                st.rerun()
        else:
            st.info("Selecciona las cantidades de los ingredientes que deseas comprar.")