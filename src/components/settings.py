# src/components/settings.py
import streamlit as st
import os
from src.persistence.json_handler import JSONHandler
from src.core.scheduler import EventScheduler
from src.models.restaurant import Restaurant
from datetime import datetime

def render_settings() -> None:
    """Panel de configuración: exportar, importar y reiniciar restaurante."""
    st.subheader("⚙️ Configuración del Sistema")

    # ---- EXPORTAR ----
    st.markdown("### 📤 Exportar estado actual")
    st.caption("Descarga un archivo JSON con toda la información del restaurante (empleados, menú, ingredientes, historial y eventos).")
    if st.button("📥 Generar archivo de exportación"):
        if "restaurant" in st.session_state and "scheduler" in st.session_state:
            # Serializar a JSON (no guardamos en disco, solo para descarga)
            import json
            from dataclasses import asdict

            def json_serial(obj):
                if isinstance(obj, datetime):
                    return obj.isoformat()
                if hasattr(obj, 'value'):
                    return obj.value
                raise TypeError(f"Type not serializable: {type(obj)}")

            restaurant = st.session_state.restaurant
            scheduler = st.session_state.scheduler

            employees_serialized = {}
            for k, v in restaurant.employees.items():
                employees_serialized[k] = {
                    "id": v.id,
                    "name": v.name,
                    "role": v.role.value,
                    "experience": v.experience.value,
                    "specialties": v.specialties,
                    "daily_wage": v.daily_wage,
                    "is_available": v.is_available,
                    "busy_until": v.busy_until.isoformat() if v.busy_until else None
                }

            applicants_serialized = []
            for cand in restaurant.applicants:
                applicants_serialized.append({
                    "name": cand["name"],
                    "role": getattr(cand["role"], 'value', cand["role"]),
                    "experience": getattr(cand["experience"], 'value', cand["experience"]),
                    "specialties": cand["specialties"],
                    "daily_wage": cand["daily_wage"],
                    "bio": cand["bio"]
                })

            data = {
                "name": restaurant.name,
                "balance": restaurant.balance,
                "employees": employees_serialized,
                "tables": {k: asdict(v) for k, v in restaurant.tables.items()},
                "menu": {k: asdict(v) for k, v in restaurant.menu.items()},
                "ingredients": {k: asdict(v) for k, v in restaurant.ingredients.items()},
                "history": restaurant.history,
                "applicants": applicants_serialized,
                "scheduled_events": [e.to_dict() for e in scheduler.scheduled_events]
            }

            json_bytes = json.dumps(data, default=json_serial, indent=4, ensure_ascii=False).encode('utf-8')
            st.download_button(
                label="⬇️ Descargar JSON",
                data=json_bytes,
                file_name="il_gusto_giusto_export.json",
                mime="application/json"
            )
        else:
            st.error("No hay estado del restaurante para exportar.")

    st.divider()

    # ---- IMPORTAR ----
    st.markdown("### 📥 Importar estado desde archivo")
    st.caption("Selecciona un archivo JSON previamente exportado. Esto **reemplazará** el estado actual del restaurante (incluyendo eventos en curso).")
    uploaded_file = st.file_uploader("Cargar archivo JSON", type=["json"])
    if uploaded_file is not None:
        if st.button("📤 Cargar y reemplazar estado actual"):
            try:
                json_str = uploaded_file.read().decode('utf-8')
                new_rest, new_events = JSONHandler.loads(json_str)
                if new_rest is None:
                    st.error("El archivo JSON no tiene un formato válido.")
                else:
                    # Limpiar eventos huérfanos
                    new_events = [e for e in new_events if new_rest.employees.get(e.assigned_chef_id)]
                    # Actualizar session_state
                    st.session_state.restaurant = new_rest
                    st.session_state.scheduler = EventScheduler(new_rest)
                    st.session_state.scheduler.scheduled_events = new_events
                    # Guardar en disco para persistencia
                    JSONHandler.save(new_rest, new_events, "data/restaurant_state.json")
                    st.success("Estado importado correctamente. La aplicación se reiniciará para reflejar los cambios.")
                    st.rerun()
            except Exception as e:
                st.error(f"Error al procesar el archivo: {e}")

    st.divider()

    # ---- REINICIAR (RESET) ----
    st.markdown("### 🔄 Reiniciar restaurante")
    st.caption("Vuelve a cargar la configuración por defecto (ingredientes, menú, empleados iniciales). Se perderán todos los cambios no guardados.")
    if st.button("⚠️ Reiniciar a valores de fábrica"):
        if os.path.exists("data/default_config.json"):
            try:
                rest, events = JSONHandler.load("data/default_config.json")
                if rest:
                    rest.add_transaction(rest.balance, "Capital Inicial de Apertura")
                    st.session_state.restaurant = rest
                    st.session_state.scheduler = EventScheduler(rest)
                    st.session_state.scheduler.scheduled_events = []  # sin eventos previos
                    JSONHandler.save(rest, [], "data/restaurant_state.json")
                    st.success("Restaurante reiniciado con la configuración por defecto.")
                    st.rerun()
                else:
                    st.error("No se pudo cargar la configuración por defecto.")
            except Exception as e:
                st.error(f"Error al reiniciar: {e}")
        else:
            st.error("Archivo de configuración por defecto no encontrado.")