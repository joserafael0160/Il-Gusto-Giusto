import streamlit as st
import os
from datetime import datetime, timedelta
from src.engine import PlanningEngine
from src.models import Event
from src.persistence import load_from_json, save_to_json

# --- CONFIGURACIÓN DE RUTAS ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, "data", "restaurant_state.json")

st.set_page_config(page_title="El Dragón del Sabor", layout="wide")

# --- INICIALIZACIÓN ---
if 'engine' not in st.session_state:
    engine = PlanningEngine()
    r, i, c = load_from_json(DATA_PATH)
    engine.resources, engine.ingredients, engine.constraints = r, i, c
    st.session_state.engine = engine

engine = st.session_state.engine

# --- ESTILO ---
st.markdown("""<style> .stButton>button { width: 100%; height: 100px; font-size: 20px; } </style>""", unsafe_allow_html=True)

st.title("🏮 El Dragón del Sabor - Centro de Mando")

# --- KPIs SUPERIORES ---
cols = st.columns(4)
cols[0].metric("Órdenes", len(engine.events))
cols[1].metric("Chef Takeshi", "OCUPADO" if any("emp_01" in e.resource_ids for e in engine.events) else "LIBRE")
cols[2].metric("Mesas Libres", len([r for r in engine.resources.values() if r.type == 'tables']) - 
               len(set([rid for e in engine.events for rid in e.resource_ids if rid.startswith('tab')])))

st.divider()

col_main, col_side = st.columns([3, 1])

with col_main:
    st.subheader("👨‍🍳 Plano del Restaurante")
    
    # Renderizar Mesas como botones de acción
    mesa_cols = st.columns(3)
    tables = [res for res in engine.resources.values() if res.type == 'tables']
    
    for i, table in enumerate(tables):
        is_occupied = any(table.id in e.resource_ids for e in engine.events)
        with mesa_cols[i % 3]:
            btn_label = f"🪑 {table.name}\n" + ("(Ocupada)" if is_occupied else "(Libre)")
            if st.button(btn_label, key=table.id):
                st.session_state.active_mesa = table.id

    st.divider()
    
    # SECCIÓN DE COMANDA (Aparece al tocar una mesa)
    if 'active_mesa' in st.session_state:
        
        mesa_id = st.session_state.active_mesa
        st.subheader(f"📝 Tomar Orden para: {engine.resources[mesa_id].name}")
        
        with st.container(border=True):
            col_f1, col_f2 = st.columns(2)
            pedido = col_f1.selectbox("Plato del Menú", ["Ramen Especial", "Sushi Roll", "Limpieza de Cocina"])
            duracion = col_f2.number_input("Duración (min)", 15, 120, 45)
            
            # Selección de ingredientes (esto hace que el stock baje)
            st.write("🥗 **Ingredientes a consumir:**")
            ing_needed = {}
            for ing_id, ing in engine.ingredients.items():
                qty = st.number_input(f"Cantidad de {ing.name} ({ing.unit})", 0.0, 5.0, 0.0, key=f"ing_{ing_id}")
                if qty > 0: ing_needed[ing_id] = qty

            # Recursos automáticos según el tipo de pedido
            recursos_finales = [mesa_id, "emp_01", "eq_01"] # Lógica simplificada: Chef + Estación

            if st.button("🚀 Enviar a Cocina", type="primary"):
                try:
                    # 1. Identificar recursos básicos
                    recursos_finales = [mesa_id, "emp_01", "eq_01"] # Mesa + Chef + Estación

                    # 2. LÓGICA DE AUTO-ASIGNACIÓN (Para que tenga sentido operativo)
                    # Si es la Mesa Principal (tab_01), añadimos a Yuki (emp_02) automáticamente
                    if mesa_id == "tab_01" and "emp_02" not in recursos_finales:
                        recursos_finales.append("emp_02")
                        st.info("ℹ️ Yuki (Mesero) ha sido asignado automáticamente a esta mesa.")

                    new_ev = Event(
                        id=f"EV-{int(datetime.now().timestamp())}",
                        name=f"{pedido} ({engine.resources[mesa_id].name})",
                        start_time=datetime.now(),
                        end_time=datetime.now() + timedelta(minutes=duracion),
                        resource_ids=recursos_finales,
                        ingredients_needed=ing_needed
                    )
        
                    engine.add_event(new_ev)
                    save_to_json(DATA_PATH, engine)
                    st.success("✅ ¡Orden en marcha!")
                    st.rerun()
        
                except ValueError as e:
                  st.error(f"❌ {e}")

    # LINEA DE TIEMPO (Solo órdenes activas)
    if engine.events:
        st.subheader("🔥 Órdenes en Preparación")
        for ev in engine.events:
            with st.expander(f"{ev.name} - Finaliza {ev.end_time.strftime('%H:%M')}"):
                st.write(f"Recursos: {', '.join([engine.resources[r].name for r in ev.resource_ids])}")
                if st.button("Completar / Cancelar", key=f"del_{ev.id}"):
                    engine.events.remove(ev)
                    save_to_json(DATA_PATH, engine)
                    st.rerun()

with col_side:
    st.subheader("📦 Almacén")
    for ing in engine.ingredients.values():
        color = "red" if ing.current_stock <= ing.min_stock else "green"
        st.markdown(f"<p style='color:{color}; font-weight:bold;'>{ing.name}: {ing.current_stock:.2f} {ing.unit}</p>", unsafe_allow_html=True)