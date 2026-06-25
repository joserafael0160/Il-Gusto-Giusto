# src/components/staff_admin.py
import streamlit as st
import uuid
from src.models.restaurant import Restaurant, Employee, EmployeeRole, ExperienceLevel
from src.services.restaurant_service import RestaurantService, calculate_role_deficit
from src.core.scheduler import EventScheduler

ROLE_CSS = {
    "chef": "<span style='background-color: rgba(231, 111, 81, 0.15); color: #e76f51; padding: 3px 8px; border-radius: 4px; font-size: 0.75rem; font-weight: bold; border: 1px solid rgba(231, 111, 81, 0.25);'>👨‍🍳 CHEF</span>",
    "waiter": "<span style='background-color: rgba(42, 157, 143, 0.15); color: #2a9d8f; padding: 3px 8px; border-radius: 4px; font-size: 0.75rem; font-weight: bold; border: 1px solid rgba(42, 157, 143, 0.25);'>🤵 CAMARERO</span>"
}

EXP_CSS = {
    "senior": "<span style='background-color: rgba(233, 196, 106, 0.15); color: #e9c46a; padding: 3px 8px; border-radius: 4px; font-size: 0.75rem; font-weight: bold; border: 1px solid rgba(233, 196, 106, 0.25);'>⭐ SENIOR</span>",
    "junior": "<span style='background-color: rgba(244, 244, 249, 0.1); color: #a0a0a5; padding: 3px 8px; border-radius: 4px; font-size: 0.75rem; font-weight: bold; border: 1px solid rgba(244, 244, 249, 0.2);'>🌱 JUNIOR</span>"
}

def render_staff_manager(restaurant: Restaurant, save_callback, scheduler: EventScheduler = None) -> None:
    st.subheader("👥 Gestión de Recursos Humanos y Bolsa de Trabajo")

    if "staff_alert" in st.session_state and st.session_state.staff_alert:
        alert = st.session_state.staff_alert
        if alert["type"] == "success":
            st.success(alert["msg"])
        elif alert["type"] == "error":
            st.error(alert["msg"])
        del st.session_state.staff_alert

    default_applicants = [
        {"name": "Alessandro Moretti", "role": EmployeeRole.WAITER, "experience": ExperienceLevel.JUNIOR, "specialties": [], "daily_wage": 45.0, "bio": "Estudiante con buena actitud, dispuesto a dar el mejor servicio de salón."},
        {"name": "Giulia Ferrari", "role": EmployeeRole.WAITER, "experience": ExperienceLevel.SENIOR, "specialties": [], "daily_wage": 80.0, "bio": "Maître profesional con amplia trayectoria en hostelería gourmet."},
        {"name": "Vincenzo Romano", "role": EmployeeRole.CHEF, "experience": ExperienceLevel.SENIOR, "specialties": ["pizza"], "daily_wage": 150.0, "bio": "Maestro Pizzaiolo napolitano certificado. Experto en hornos tradicionales."},
        {"name": "Francesca Colombo", "role": EmployeeRole.CHEF, "experience": ExperienceLevel.JUNIOR, "specialties": ["pasta"], "daily_wage": 90.0, "bio": "Apasionada de las masas frescas artesanales y salsas tradicionales."}
    ]

    if not restaurant.applicants:
        restaurant.applicants = default_applicants

    all_existing_specialties = sorted(list({spec for emp in restaurant.employees.values() for spec in emp.specialties}))

    tab1, tab2, tab3 = st.tabs(["Nómina Activa", "💼 Bolsa de Empleo", "➕ Añadir Candidato"])

    # ─── PESTAÑA 1: EMPLEADOS ACTUALES ───
    with tab1:
        role_filter = st.selectbox("Filtrar por puesto:", ["Todos", "Chef", "Camarero"])
        active_employees = list(restaurant.employees.items())
        
        if not active_employees:
            st.info("No hay empleados en nómina. Contrata personal en la pestaña de 'Bolsa de Empleo'.")
        else:
            for emp_id, emp in active_employees:
                if role_filter == "Chef" and emp.role != EmployeeRole.CHEF:
                    continue
                if role_filter == "Camarero" and emp.role != EmployeeRole.WAITER:
                    continue

                with st.container(border=True):
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        role_str = emp.role.value if isinstance(emp.role, EmployeeRole) else emp.role
                        exp_str = emp.experience.value if isinstance(emp.experience, ExperienceLevel) else emp.experience
                        
                        role_badge = ROLE_CSS.get(role_str, f"<span>{role_str}</span>")
                        exp_badge = EXP_CSS.get(exp_str, f"<span>{exp_str}</span>")
                        
                        st.markdown(f"### {emp.name} &nbsp;&nbsp; {role_badge} &nbsp; {exp_badge}", unsafe_allow_html=True)
                        st.markdown(f"💰 **Sueldo:** ${emp.daily_wage:.2f}/día")
                        if emp.specialties:
                            st.markdown(f"🍳 **Especialidades:** {', '.join(chef_spec.capitalize() for chef_spec in emp.specialties)}")
                    
                    with col2:
                        st.markdown("<br>", unsafe_allow_html=True)
                        if st.button("🔴 Despedir", key=f"fire_{emp_id}", type="secondary", width='stretch'):
                            cancelled_events = 0
                            if scheduler and emp.role == EmployeeRole.CHEF:
                                events_to_cancel = [
                                    e for e in scheduler.scheduled_events
                                    if e.assigned_chef_id == emp_id
                                ]
                                for evt in events_to_cancel:
                                    scheduler.cancel_event(evt.id)
                                    cancelled_events += 1
                            
                            success, message = RestaurantService.fire_employee(restaurant, emp_id)
                            if success:
                                final_msg = message
                                if cancelled_events > 0:
                                    final_msg += f" También se cancelaron {cancelled_events} comanda(s) activa(s)."
                                st.session_state.staff_alert = {"type": "success", "msg": final_msg}
                            else:
                                st.session_state.staff_alert = {"type": "error", "msg": message}
                            save_callback()
                            st.rerun()

    # ─── PESTAÑA 2: BOLSA DE EMPLEO ───
    with tab2:
        st.markdown("### Recomendación Estratégica de Candidatos")
        st.caption("Priorización automática según el déficit operativo de tu salón, nivel de experiencia y costo salarial.")

        chef_deficit = calculate_role_deficit(restaurant, EmployeeRole.CHEF)
        waiter_deficit = calculate_role_deficit(restaurant, EmployeeRole.WAITER)

        col_metric1, col_metric2 = st.columns(2)
        with col_metric1:
            st.metric(
                label="Déficit de Chefs", 
                value=f"{chef_deficit} vacantes" if chef_deficit > 0 else "Estable", 
                delta=f"+{chef_deficit}" if chef_deficit > 0 else "Balanceado",
                delta_color="inverse" if chef_deficit > 0 else "off"
            )
        with col_metric2:
            st.metric(
                label="Déficit de Camareros", 
                value=f"{waiter_deficit} vacantes" if waiter_deficit > 0 else "Estable", 
                delta=f"+{waiter_deficit}" if waiter_deficit > 0 else "Balanceado",
                delta_color="inverse" if waiter_deficit > 0 else "off"
            )

        st.divider()

        def score_candidate(cand) -> tuple:
            role_enum = cand["role"]
            exp_enum = cand["experience"]
            deficit_score = chef_deficit if role_enum == EmployeeRole.CHEF else waiter_deficit
            experience_score = 1 if exp_enum == ExperienceLevel.SENIOR else 0
            wage_score = -cand["daily_wage"]
            return (deficit_score, experience_score, wage_score)

        sorted_applicants = sorted(restaurant.applicants, key=score_candidate, reverse=True)

        for idx, cand in enumerate(sorted_applicants):
            if any(emp.name == cand["name"] for emp in restaurant.employees.values()):
                continue

            role_enum = cand["role"]
            exp_enum = cand["experience"]
            deficit = chef_deficit if role_enum == EmployeeRole.CHEF else waiter_deficit
            priority_tag = (
                "<span style='background-color: rgba(231, 111, 81, 0.2); color: #e76f51; "
                "padding: 3px 8px; border-radius: 4px; font-size: 0.7rem; font-weight: bold; "
                "border: 1px solid rgba(231, 111, 81, 0.3);'>🎯 ALTA PRIORIDAD</span>"
                if deficit > 0 else ""
            )

            with st.container(border=True):
                col_c1, col_c2 = st.columns([3, 1])
                with col_c1:
                    role_str = role_enum.value
                    exp_str = exp_enum.value
                    role_badge = ROLE_CSS.get(role_str, f"<span>{role_str}</span>")
                    exp_badge = EXP_CSS.get(exp_str, f"<span>{exp_str}</span>")
                    
                    st.markdown(f"### {cand['name']} &nbsp;&nbsp; {role_badge} &nbsp; {exp_badge} &nbsp; {priority_tag}", unsafe_allow_html=True)
                    st.markdown(f"💰 **Pretensión salarial:** `${cand['daily_wage']:.2f}/día`")
                    st.markdown(f"📖 **Biografía:** *\"{cand['bio']}\"*")
                    if cand.get("specialties"):
                        st.markdown(f"🍳 **Especialidades:** {', '.join(spec.capitalize() for spec in cand['specialties'])}")
                
                with col_c2:
                    st.markdown("<br>", unsafe_allow_html=True)
                    if st.button("✅ Contratar", key=f"hire_{idx}", type="primary", width='stretch'):
                        success, message = RestaurantService.hire_employee(restaurant, cand)
                        if success:
                            st.session_state.staff_alert = {"type": "success", "msg": message}
                            save_callback()
                            st.rerun()
                        else:
                            st.error(message)

                    if st.button("Descartar", key=f"del_cand_{idx}", type="secondary", width='stretch'):
                        restaurant.applicants.remove(cand)
                        st.session_state.staff_alert = {"type": "success", "msg": f"Candidato '{cand['name']}' descartado."}
                        save_callback()
                        st.rerun()

    # ─── PESTAÑA 3: AÑADIR NUEVO CANDIDATO ───
    with tab3:
        st.markdown("### Registrar Postulación Externa")
        with st.form("nuevo_candidato"):
            form_name = st.text_input("Nombre y Apellidos completos", placeholder="Ej: Roberto Rossi")
            col_form1, col_form2, col_form3 = st.columns(3)
            with col_form1:
                form_role = st.selectbox("Puesto de Postulación", ["Chef", "Camarero"])
            with col_form2:
                form_experience = st.selectbox("Nivel de Experiencia", ["Junior", "Senior"])
            with col_form3:
                form_wage = st.number_input("Pretensión salarial ($/día)", min_value=10.0, value=75.0, step=5.0)

            st.markdown("##### Especialidades")
            if not all_existing_specialties:
                st.info("No hay especialidades registradas aún. Puedes añadir nuevas abajo.")
            selected_specialties = st.multiselect(
                "Especialidades culinarias aplicables (Solo Chefs):",
                options=all_existing_specialties,
                key="specialties_multiselect"
            )
            
            other_specialty = st.text_input("Especialidad personalizada (Si no está en la lista)", placeholder="Ej: repostería")
            if other_specialty.strip():
                clean_spec = other_specialty.strip().lower()
                if clean_spec not in selected_specialties:
                    selected_specialties.append(clean_spec)

            biography = st.text_area("Biografía y Referencias", placeholder="Trayectoria o referencias de cocinas anteriores...")
            submitted = st.form_submit_button("📋 Registrar Candidato", width='stretch')

            if submitted:
                if not form_name.strip():
                    st.error("El nombre del candidato es obligatorio.")
                else:
                    role_enum = EmployeeRole.CHEF if form_role == "Chef" else EmployeeRole.WAITER
                    exp_enum = ExperienceLevel.SENIOR if form_experience == "Senior" else ExperienceLevel.JUNIOR

                    new_applicant = {
                        "name": form_name.strip(),
                        "role": role_enum,
                        "experience": exp_enum,
                        "specialties": selected_specialties if role_enum == EmployeeRole.CHEF else [],
                        "daily_wage": form_wage,
                        "bio": biography.strip() if biography else "Candidato registrado externamente."
                    }
                    restaurant.applicants.append(new_applicant)
                    st.session_state.staff_alert = {"type": "success", "msg": f"Candidato '{form_name.strip()}' registrado con éxito en la bolsa de empleo."}
                    save_callback()
                    st.rerun()