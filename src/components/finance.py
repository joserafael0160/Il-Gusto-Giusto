import streamlit as st
from src.models.restaurant import Restaurant

def render_finances(restaurant: Restaurant):
    st.subheader("📊 Análisis Contable y Rentabilidad")

    # Indicador de balance actual
    st.metric(label="Capital Disponible Neto", value=f"${restaurant.balance:.2f}")

    if restaurant.history:
        st.write("### Evolución del Balance Financiero")
        chart_data = []
        for idx, entry in enumerate(restaurant.history):
            chart_data.append({
                "Transacción": idx + 1,
                "Capital ($)": entry["balance_after"]
            })
        st.line_chart(data=chart_data, x="Transacción", y="Capital ($)")

        st.write("### Registro General de Transacciones (Ledger)")
        for entry in reversed(restaurant.history):
            color = "green" if entry["amount"] >= 0 else "red"
            sign = "+" if entry["amount"] >= 0 else ""
            st.write(f"[{entry['timestamp'][:19]}] **{entry['description']}**: :{color}[{sign}${entry['amount']:.2f}] (Saldo: ${entry['balance_after']:.2f})")

    st.divider()
    st.write("### Asesoría de Rentabilidad de Platos")

    for dish_id, dish in restaurant.menu.items():
        recipe_cost = 0.0
        for ing_id, qty in dish.ingredients.items():
            ing = restaurant.ingredients.get(ing_id)
            unit_cost = ing.price_per_unit if ing else 0.0
            recipe_cost += unit_cost * qty

        profit = dish.price - recipe_cost
        margin = (profit / dish.price) * 100 if dish.price > 0 else 0.0

        with st.container(border=True):
            st.write(f"#### {dish.name}")
            st.write(f"Precio venta: ${dish.price:.2f} | Costo preparación: ${recipe_cost:.2f}")
            if profit > 0:
                st.write(f"Margen Neto: :green[${profit:.2f} ({margin:.1f}%)]")
                if margin < 40:
                    st.info("💡 *Consejo:* Revisa el costo de insumos o eleva ligeramente el precio de venta para mejorar el rendimiento de este plato.")
                else:
                    st.success("💡 *Consejo:* ¡Altamente rentable! Destaca este plato en tu publicidad.")
            else:
                st.write(f"Margen Neto: :red[${profit:.2f} ({margin:.1f}%)]")
                st.error("🚨 *Alerta de Pérdida:* Este plato está perdiendo dinero por cada porción elaborada. Ajusta costos de inmediato.")