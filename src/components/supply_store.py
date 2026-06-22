import streamlit as st
from src.models.restaurant import Restaurant

def render_store_and_stock(restaurant: Restaurant, save_callback):
    st.subheader("🛒 Despensa de Ingredientes y Proveedor")

    # Sistema de Alertas
    has_alert = False
    for ing in restaurant.ingredients.values():
        if ing.quantity <= ing.min_quantity:
            st.warning(f"⚠️ **Alerta de Stock Crítico:** {ing.name} cuenta únicamente con {ing.quantity:.2f} {ing.unit} (Mínimo requerido: {ing.min_quantity:.2f}). ¡Es hora de reponer!")
            has_alert = True
    if not has_alert:
        st.success("✅ Los niveles de existencias se encuentran estables.")

    tab1, tab2 = st.tabs(["Nivel de Despensa", "Comprar Suministros"])

    with tab1:
        st.write("### Inventario de Materias Primas")
        for ing_id, ing in restaurant.ingredients.items():
            with st.container():
                c1, c2, c3 = st.columns([3, 2, 2])
                with c1:
                    st.write(f"**{ing.name}**")
                with c2:
                    st.write(f"{ing.quantity:.2f} / {ing.min_quantity:.2f} {ing.unit}")
                with c3:
                    if ing.quantity <= 0:
                        st.error("AGOTADO")
                    elif ing.quantity <= ing.min_quantity:
                        st.warning("COMPRAR URGENTE")
                    else:
                        st.success("STABLE")

    with tab2:
        st.write("### Tienda del Proveedor Mayorista Italiano")
        for ing_id, ing in restaurant.ingredients.items():
            with st.container(border=True):
                col_name, col_act, col_buy = st.columns([3, 2, 2])
                with col_name:
                    st.write(f"**{ing.name}**")
                    st.caption(f"Precio por unidad: ${ing.price_per_unit:.2f} / {ing.unit}")
                with col_act:
                    qty_to_buy = st.number_input(f"Cantidad ({ing.unit})", min_value=0.0, max_value=50.0, step=1.0, key=f"store_{ing_id}")
                with col_buy:
                    cost = qty_to_buy * ing.price_per_unit
                    st.write(f"Subtotal: ${cost:.2f}")
                    if st.button("Comprar", key=f"btn_store_{ing_id}"):
                        if qty_to_buy <= 0:
                            st.warning("Indica una cantidad superior a cero.")
                        elif restaurant.balance < cost:
                            st.error("No cuentas con saldo suficiente.")
                        else:
                            restaurant.ingredients[ing_id].quantity += qty_to_buy
                            restaurant.add_transaction(-cost, f"Compra de {qty_to_buy} {ing.unit} de {ing.name}")
                            save_callback()
                            st.success(f"Adquisición completada.")
                            st.rerun()