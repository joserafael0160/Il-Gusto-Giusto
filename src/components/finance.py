# src/components/finance.py
import streamlit as st
import pandas as pd
from src.models.restaurant import Restaurant

def render_finances(restaurant: Restaurant) -> None:
    st.subheader("📊 Análisis Contable y Rentabilidad")

    # ─── PESTAÑAS PRINCIPALES DE FINANZAS ───
    tab_overview, tab_profitability = st.tabs([
        "💰 Balance y Flujo de Caja", 
        "🍝 Rentabilidad de Recetas"
    ])

    # ─── PESTAÑA 1: BALANCE Y FLUJO DE CAJA ───
    with tab_overview:
        # 📊 KPIs del Balance de Caja
        col_kpi1, col_kpi2, col_kpi3 = st.columns(3)
        
        with col_kpi1:
            st.metric(
                label="Capital Disponible Neto", 
                value=f"${restaurant.balance:,.2f}",
                help="Dinero líquido disponible en la caja del restaurante."
            )
            
        with col_kpi2:
            num_transactions = len(restaurant.history)
            st.metric(
                label="Transacciones Registradas", 
                value=f"{num_transactions} operaciones",
                help="Cantidad de movimientos financieros históricos."
            )
            
        with col_kpi3:
            if restaurant.history:
                last_tx = restaurant.history[-1]
                delta_val = f"{'+' if last_tx['amount'] >= 0 else ''}${last_tx['amount']:,.2f}"
                st.metric(
                    label="Último Movimiento", 
                    value=delta_val,
                    delta=last_tx["description"],
                    delta_color="normal" if last_tx["amount"] >= 0 else "inverse"
                )
            else:
                st.metric(label="Último Movimiento", value="$0.00")

        st.divider()

        if restaurant.history:
            st.markdown("### 📈 Evolución del Balance")
            df = pd.DataFrame(restaurant.history)
            
            # Parseo robusto de fechas
            df["timestamp"] = pd.to_datetime(df["timestamp"], format="ISO8601", errors='coerce')
            df = df.dropna(subset=["timestamp"]).sort_values("timestamp")
            df.set_index("timestamp", inplace=True)
            df["balance_after"] = pd.to_numeric(df["balance_after"], errors='coerce')

            if not df.empty:
                st.area_chart(df["balance_after"], color="#e76f51")

            st.markdown("### 📜 Libro Diario de Transacciones")
            st.caption("Usa los encabezados de la tabla para filtrar u ordenar los movimientos.")
            
            ledger_df = df.reset_index()[["timestamp", "description", "amount", "balance_after"]]
            ledger_df.columns = ["Fecha", "Descripción", "Monto", "Saldo Resultante"]

            st.dataframe(
                ledger_df.sort_values("Fecha", ascending=False),
                column_config={
                    "Fecha": st.column_config.DatetimeColumn("Fecha y Hora", format="DD/MM/YYYY HH:mm"),
                    "Descripción": st.column_config.TextColumn("Descripción de la Operación"),
                    "Monto": st.column_config.NumberColumn("Monto transaccionado", format="$%.2f"),
                    "Saldo Resultante": st.column_config.NumberColumn("Balance en Caja", format="$%.2f")
                },
                width='stretch',
                hide_index=True
            )
        else:
            st.info("Aún no se han registrado transacciones en el historial contable.")

    # ─── PESTAÑA 2: RENTABILIDAD DE RECETAS ───
    with tab_profitability:
        if not restaurant.menu:
            st.info("No hay platos cargados en la carta para analizar.")
        else:
            # Cálculo de márgenes y ganancias por plato
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
                    "Margen de Ganancia": margin / 100.0  # Convertido a fracción decimal para ProgressColumn
                })

            profit_df = pd.DataFrame(profits).sort_values("Ganancia ($)", ascending=False)

            # KPIs del menú
            avg_margin = profit_df["Margen de Ganancia"].mean() * 100
            best_dish = profit_df.iloc[0]["Plato"] if not profit_df.empty else "N/A"
            worst_dish = profit_df.iloc[-1]["Plato"] if not profit_df.empty else "N/A"

            col_menu1, col_menu2, col_menu3 = st.columns(3)
            with col_menu1:
                st.metric(
                    label="Margen Promedio de la Carta", 
                    value=f"{avg_margin:.1f}%",
                    help="Margen de beneficio neto promedio de todas tus recetas."
                )
            with col_menu2:
                st.metric(
                    label="Plato más Rentable (Neto)", 
                    value=best_dish,
                    help="El plato de la carta que genera más ganancia neta por unidad."
                )
            with col_menu3:
                st.metric(
                    label="Plato de menor Margen", 
                    value=worst_dish,
                    help="El plato con menor retorno en base a su costo de ingredientes."
                )

            st.divider()

            st.markdown("### 📊 Detalle de Rentabilidad del Menú")
            st.caption("La columna 'Margen de Retorno' representa el porcentaje de ganancia sobre el precio de venta final.")

            # Renderizado de la tabla con barras de progreso integradas (ProgressColumn)
            st.dataframe(
                profit_df,
                column_config={
                    "Plato": st.column_config.TextColumn("Plato de la Carta", width="medium"),
                    "Precio ($)": st.column_config.NumberColumn("Precio de Venta", format="$%.2f"),
                    "Costo ($)": st.column_config.NumberColumn("Costo Ingredientes", format="$%.2f"),
                    "Ganancia ($)": st.column_config.NumberColumn("Ganancia por Unidad", format="$%.2f"),
                    "Margen de Ganancia": st.column_config.ProgressColumn(
                        "Margen de Retorno",
                        help="Porcentaje de beneficio de la receta",
                        format="%.1f%%",
                        min_value=0.0,
                        max_value=1.0
                    )
                },
                width='stretch',
                hide_index=True
            )

            st.divider()

            # ─── CONSEJOS ESTRATÉGICOS CONSOLIDADOS ───
            st.markdown("### 💡 Diagnóstico de Precios y Costes")
            
            critical_dishes = profit_df[profit_df["Margen de Ganancia"] < 0.40]
            healthy_dishes = profit_df[profit_df["Margen de Ganancia"] >= 0.40]

            col_crit, col_healthy = st.columns(2)

            with col_crit:
                with st.container(border=True):
                    st.markdown("<h4 style='color: #e76f51; margin-top:0;'>⚠️ Oportunidades de Mejora</h4>", unsafe_allow_html=True)
                    st.caption("Platos con márgenes de ganancia inferiores al 40%. Considera ajustar precios o optimizar costos unitarios:")
                    if not critical_dishes.empty:
                        for _, row in critical_dishes.iterrows():
                            st.write(f"- **{row['Plato']}** (Margen: `{row['Margen de Ganancia']*100:.1f}%` | Costo receta: `${row['Costo ($)']:.2f}`)")
                    else:
                        st.write("¡Excelente! Todos tus platos poseen márgenes de rentabilidad robustos.")

            with col_healthy:
                with st.container(border=True):
                    st.markdown("<h4 style='color: #2a9d8f; margin-top:0;'>🟢 Platos Estrella</h4>", unsafe_allow_html=True)
                    st.caption("Platos saludables con márgenes de rentabilidad óptimos superiores al 40%:")
                    if not healthy_dishes.empty:
                        for _, row in healthy_dishes.iterrows():
                            st.write(f"- **{row['Plato']}** (Margen: `{row['Margen de Ganancia']*100:.1f}%` | Ganancia: `${row['Ganancia ($)']:.2f}`)")
                    else:
                        st.write("No se detectan platos estrella. Es aconsejable revisar los precios de venta de tus recetas.")