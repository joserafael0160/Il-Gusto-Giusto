import streamlit as st
import pandas as pd
from src.models.restaurant import Restaurant

def render_finances(restaurant: Restaurant):
    st.subheader("📊 Análisis Contable y Rentabilidad")

    # ─── Balance actual ───
    st.metric(label="Capital Disponible Neto", value=f"${restaurant.balance:,.2f}")

    # ─── Evolución del balance ───
    if restaurant.history:
        st.write("### Evolución del Balance")
        df = pd.DataFrame(restaurant.history)
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        df.set_index("timestamp", inplace=True)
        df = df.sort_index()

        # Gráfico de línea con el balance a lo largo del tiempo
        st.line_chart(df["balance_after"])

        # ─── Ledger de transacciones ───
        st.write("### Registro de Transacciones")
        ledger_df = df.reset_index()[["timestamp", "description", "amount", "balance_after"]]
        ledger_df.columns = ["Fecha", "Descripción", "Monto", "Saldo resultante"]
        ledger_df["Monto"] = ledger_df["Monto"].apply(lambda x: f"${x:,.2f}")
        ledger_df["Saldo resultante"] = ledger_df["Saldo resultante"].apply(lambda x: f"${x:,.2f}")
        st.dataframe(ledger_df.sort_values("Fecha", ascending=False), use_container_width=True, hide_index=True)
    else:
        st.info("Aún no hay transacciones registradas.")

    st.divider()

    # ─── Rentabilidad por plato ───
    st.write("### Rentabilidad por Plato")
    if not restaurant.menu:
        st.info("No hay platos en el menú para analizar.")
    else:
        profits = []
        for dish_id, dish in restaurant.menu.items():
            recipe_cost = 0.0
            for ing_id, qty in dish.ingredients.items():
                ing = restaurant.ingredients.get(ing_id)
                if ing:
                    recipe_cost += ing.price_per_unit * qty
            profit = dish.price - recipe_cost
            margin = (profit / dish.price) * 100 if dish.price > 0 else 0.0
            profits.append({
                "Plato": dish.name,
                "Precio ($)": dish.price,
                "Costo ($)": recipe_cost,
                "Ganancia ($)": profit,
                "Margen (%)": margin
            })

        profit_df = pd.DataFrame(profits).sort_values("Ganancia ($)", ascending=False)

        # Gráfico de barras de ganancia por plato
        st.bar_chart(profit_df.set_index("Plato")["Ganancia ($)"])

        # Tabla detallada
        st.write("#### Detalle de rentabilidad")
        profit_df_display = profit_df.copy()
        profit_df_display["Precio ($)"] = profit_df_display["Precio ($)"].apply(lambda x: f"${x:.2f}")
        profit_df_display["Costo ($)"] = profit_df_display["Costo ($)"].apply(lambda x: f"${x:.2f}")
        profit_df_display["Ganancia ($)"] = profit_df_display["Ganancia ($)"].apply(lambda x: f"${x:.2f}")
        profit_df_display["Margen (%)"] = profit_df_display["Margen (%)"].apply(lambda x: f"{x:.1f}%")
        st.dataframe(profit_df_display, use_container_width=True, hide_index=True)

        # Consejo rápido
        st.write("---")
        for _, row in profit_df.iterrows():
            if row["Margen (%)"] < 40:
                st.info(f"💡 {row['Plato']}: margen bajo ({row['Margen (%)']:.1f}%). Considera ajustar precio o reducir costos.")
            else:
                st.success(f"💡 {row['Plato']}: margen saludable ({row['Margen (%)']:.1f}%).")