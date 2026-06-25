# src/components/supply_store.py
import streamlit as st
from src.models.restaurant import Restaurant

# Diseño de badges para el estado del inventario
STOCK_BADGES = {
    "empty": "<span style='background-color: rgba(231, 111, 81, 0.15); color: #e76f51; padding: 3px 8px; border-radius: 4px; font-size: 0.75rem; font-weight: bold; border: 1px solid rgba(231, 111, 81, 0.25);'>🔴 AGOTADO</span>",
    "low": "<span style='background-color: rgba(233, 196, 106, 0.15); color: #e9c46a; padding: 3px 8px; border-radius: 4px; font-size: 0.75rem; font-weight: bold; border: 1px solid rgba(233, 196, 106, 0.25);'>⚠️ STOCK CRÍTICO</span>",
    "stable": "<span style='background-color: rgba(42, 157, 143, 0.15); color: #2a9d8f; padding: 3px 8px; border-radius: 4px; font-size: 0.75rem; font-weight: bold; border: 1px solid rgba(42, 157, 143, 0.25);'>🟢 SUFICIENTE</span>"
}

def process_bulk_purchase_callback(restaurant: Restaurant, save_callback) -> None:
    """Callback function that executes BEFORE the page is drawn.
    
    Modifies inventory state safely and resets input widgets.
    """
    order_quantities = {}
    total_cost = 0.0
    ingredients_summary = []
    
    for ing_id, ing in restaurant.ingredients.items():
        qty = st.session_state.get(f"bulk_qty_{ing_id}", 0.0)
        if qty > 0:
            order_quantities[ing_id] = qty
            total_cost += qty * ing.price_per_unit
            ingredients_summary.append(f"{qty} {ing.unit} de {ing.name}")
            
    if total_cost <= 0:
        return
        
    if restaurant.balance < total_cost:
        st.session_state.purchase_error = "No cuentas con suficiente capital disponible en caja para realizar esta compra."
        return
        
    # Aplicar la compra física
    for ing_id, qty in order_quantities.items():
        restaurant.ingredients[ing_id].quantity += qty
        
    # Registrar transacción
    summary_text = "Compra de suministros: " + ", ".join(ingredients_summary)
    restaurant.add_transaction(-total_cost, summary_text)
    
    # Resetear los inputs
    for ing_id in restaurant.ingredients.keys():
        st.session_state[f"bulk_qty_{ing_id}"] = 0.0
        
    st.session_state.purchase_success = (
        f"🎉 **¡Pedido Procesado Exitosamente!** Se han incorporado las materias primas a "
        f"la despensa. Coste total facturado: **${total_cost:,.2f}**."
    )
    
    save_callback()


def render_store_and_stock(restaurant: Restaurant, save_callback) -> None:
    st.subheader("🛒 Despensa de Suministros e Inventario")

    # 🧾 MOSTRAR NOTIFICACIONES PERSISTENTES
    if "purchase_success" in st.session_state and st.session_state.purchase_success:
        st.success(st.session_state.purchase_success)
        del st.session_state.purchase_success

    if "purchase_error" in st.session_state and st.session_state.purchase_error:
        st.error(st.session_state.purchase_error)
        del st.session_state.purchase_error

    # 🚨 Alerta Inteligente Consolidada de Stock Crítico
    low_stock_items = [ing for ing in restaurant.ingredients.values() if ing.quantity <= ing.min_quantity]
    
    if low_stock_items:
        alert_msg = "⚠️ **Alerta de Insumos Críticos:** Las siguientes materias primas están por debajo del mínimo recomendado:\n\n"
        for ing in low_stock_items:
            alert_msg += f"- **{ing.name}**: `{ing.quantity:.2f} {ing.unit}` (Mínimo: `{ing.min_quantity:.2f}`)\n"
        st.warning(alert_msg)
    else:
        st.success("✅ Todos los suministros se encuentran estables en la despensa.")

    # ─── SISTEMA DE PESTAÑAS CONTROLADO POR ESTADO DE SESIÓN (Rock-Solid Routing) ───
    if "store_active_tab" not in st.session_state:
        st.session_state.store_active_tab = "tienda"  # Abrir por defecto en la tienda

    # Renderizar barra de pestañas como botones segmentados
    c_tab1, c_tab2 = st.columns(2)
    with c_tab1:
        is_despensa = st.session_state.store_active_tab == "despensa"
        if st.button("📦 Existencias en Almacén", key="btn_subtab_despensa", use_container_width=True, type="primary" if is_despensa else "secondary"):
            st.session_state.store_active_tab = "despensa"
            st.rerun()

    with c_tab2:
        is_tienda = st.session_state.store_active_tab == "tienda"
        if st.button("🛍️ Comprar Suministros (Mayorista)", key="btn_subtab_tienda", use_container_width=True, type="primary" if is_tienda else "secondary"):
            st.session_state.store_active_tab = "tienda"
            st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)

    # ─── VISTA 1: INVENTARIO DE MATERIAS PRIMAS ───
    if st.session_state.store_active_tab == "despensa":
        st.markdown("### Inventario de Materias Primas")
        st.markdown("<p style='color: gray;'>Visualización de existencias ordenadas por prioridad de urgencia.</p>", unsafe_allow_html=True)

        critical_items = [ing for ing in restaurant.ingredients.values() if ing.quantity <= ing.min_quantity]
        healthy_items = [ing for ing in restaurant.ingredients.values() if ing.quantity > ing.min_quantity]

        if critical_items:
            st.markdown("#### 🚨 Reabastecimiento Requerido")
            for ing in critical_items:
                with st.container(border=True):
                    c_name, c_progress, c_badge = st.columns([3, 4, 2])
                    with c_name:
                        st.markdown(f"**{ing.name}**")
                        st.caption(f"Actual: `{ing.quantity:.2f} {ing.unit}` / Mínimo: `{ing.min_quantity:.2f} {ing.unit}`")
                    with c_progress:
                        percentage = min(1.0, max(0.0, ing.quantity / max(1.0, ing.min_quantity * 3.0)))
                        st.markdown("<div style='margin-top: 5px;'></div>", unsafe_allow_html=True)
                        st.progress(percentage)
                    with c_badge:
                        badge_html = STOCK_BADGES["empty"] if ing.quantity <= 0 else STOCK_BADGES["low"]
                        st.markdown(f"<div style='margin-top: 10px; text-align: right;'>{badge_html}</div>", unsafe_allow_html=True)
            st.write("")

        if healthy_items:
            st.markdown("#### ✅ Niveles Estables")
            for ing in healthy_items:
                with st.container(border=True):
                    c_name, c_progress, c_badge = st.columns([3, 4, 2])
                    with c_name:
                        st.markdown(f"**{ing.name}**")
                        st.caption(f"Actual: `{ing.quantity:.2f} {ing.unit}` / Mínimo: `{ing.min_quantity:.2f} {ing.unit}`")
                    with c_progress:
                        percentage = min(1.0, max(0.0, ing.quantity / max(1.0, ing.min_quantity * 3.0)))
                        st.markdown("<div style='margin-top: 5px;'></div>", unsafe_allow_html=True)
                        st.progress(percentage)
                    with c_badge:
                        st.markdown(f"<div style='margin-top: 10px; text-align: right;'>{STOCK_BADGES['stable']}</div>", unsafe_allow_html=True)

    # ─── VISTA 2: COMPRAR SUMINISTROS ───
    else:
        c_bal1, c_bal2 = st.columns([2, 1])
        with c_bal1:
            st.markdown("### Pedido Mayorista por Lotes")
            st.markdown("<p style='color: gray;'>Ajusta las cantidades que deseas de cada ingrediente y presiona procesar pedido.</p>", unsafe_allow_html=True)
        with c_bal2:
            st.metric(label="💰 Capital Disponible", value=f"${restaurant.balance:,.2f}")
            
        st.divider()

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
                        key=f"bulk_qty_{ing_id}"
                    )
                    order_quantities[ing_id] = qty
                    
                with col_subtotal:
                    subtotal = qty * ing.price_per_unit
                    st.markdown(f"<p style='text-align: right; margin-top: 25px; font-size: 1.05rem;'>Subtotal: <b>${subtotal:.2f}</b></p>", unsafe_allow_html=True)

        st.divider()

        total_invoice_cost = sum(order_quantities[ing_id] * ing.price_per_unit for ing_id, ing in restaurant.ingredients.items())

        if total_invoice_cost > 0:
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
                        st.button(
                            "🧾 Procesar Pedido Completo", 
                            type="primary", 
                            use_container_width=True,
                            on_click=process_bulk_purchase_callback,
                            args=(restaurant, save_callback)
                        )
        else:
            st.info("Incrementa la cantidad de los ingredientes que deseas comprar para generar una factura consolidada.")