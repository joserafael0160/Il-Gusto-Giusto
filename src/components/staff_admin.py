# src/components/staff_admin.py
import streamlit as st
import uuid
from src.models.restaurant import Restaurant, Employee, EmployeeRole, ExperienceLevel
from src.services.restaurant_service import calculate_role_deficit

# Configuración de diseño CSS para roles y rangos
ROLE_CSS = {
    "chef": "<span style='background-color: rgba(231, 111, 81, 0.15); color: #e76f51; padding: 3px 8px; border-radius: 4px; font-size: 0.75rem; font-weight: bold; border: 1px solid rgba(231, 111, 81, 0.25);'>👨‍🍳 CHEF</span>",
    "waiter": "<span style='background-color: rgba(42, 157, 143, 0.15); color: #2a9d8f; padding: 3px 8px; border-radius: 4px; font-size: 0.75rem; font-weight: bold; border: 1px solid rgba(42, 157, 143, 0.25);'>🤵 CAMARERO</span>"
}

EXP_CSS = {
    "senior": "<span style='background-color: rgba(233, 196, 106, 0.15); color: #e9c46a; padding: 3px 8px; border-radius: 4px; font-size: 0.75rem; font-weight: bold; border: 1px solid rgba(233, 196, 106, 0.25);'>⭐ SENIOR</span>",
    "junior": "<span style='background-color: rgba(244, 244, 249, 0.1); color: #a0a0a5; padding: 3px 8px; border-radius: 4px; font-size: 0.75rem; font-weight: bold; border: 1px solid rgba(244, 244, 249, 0.2);'>🌱 JUNIOR</span>"
}

def render_staff_manager(restaurant: Restaurant, save_callback) -> None:
    st.subheader("👥 Gestión de Recursos Humanos y Bolsa de Trabajo")

    # Inicializar candidatos base si no existen en persistencia
    default_applicants = [
        {"name": "Alessandro Moretti", "role": EmployeeRole.WAITER, "experience": ExperienceLevel.JUNIOR, "specialties": [], "daily_wage": 45.0, "bio": "Estudiante con buena actitud, dispuesto a dar el mejor servicio de salón."},
        {"name": "Giulia Ferrari", "role": EmployeeRole.WAITER, "experience": ExperienceLevel.SENIOR, "specialties": [], "daily_wage": 80.0, "bio": "Maître profesional con amplia trayectoria en hostelería gourmet."},
        {"name": "Vincenzo Romano", "role": EmployeeRole.CHEF, "experience": ExperienceLevel.SENIOR, "specialties": ["pizza"], "daily_wage": 150.0, "bio": "Maestro Pizzaiolo napolitano certificado. Experto en hornos tradicionales."},
        {"name": "Francesca Colombo", "role": EmployeeRole.CHEF, "experience": ExperienceLevel.JUNIOR, "specialties": ["pasta"], "daily_wage": 90.0, "bio": "Apasionada de las masas frescas artesanales y salsas tradicionales."}
    ]

    if not restaurant.applicants:
        restaurant.applicants = default_applicants

    # Extraer especialidades existentes en la nómina activa para recomendaciones
    all_existing_specialties = sorted(list({spec for emp in restaurant.employees.values() for spec in emp.specialties}))

    tab1, tab2, tab3 = st.tabs(["Nómina Activa", "💼 Bolsa de Empleo", "➕ Añadir Candidato"])

    # ─── PESTAÑA 1: EMPLEADOS ACTUALES ───
    with tab1:
        role_filter = st.selectbox("Filtrar por puesto:", ["Todos", "Chef", "Camarero"])
        
        # Filtrar y renderizar la nómina activa
        active_employees = list(restaurant.employees.items())
        
        if not active_employees:
            st.info("No hay empleados registrados en la nómina. Contrata personal en la pestaña de 'Bolsa de Empleo'.")
        else:
            for emp_id, emp in active_employees:
                if role_filter == "Chef" and emp.role != EmployeeRole.CHEF:
                    continue
                if role_filter == "Camarero" and emp.role != EmployeeRole.WAITER:
                    continue

                with st.container(border=True):
                    c1, c2 = st.columns([3, 1])
                    with c1:
                        # Mapear strings a enums para compatibilidad robusta
                        role_str = emp.role.value if isinstance(emp.role, EmployeeRole) else emp.role
                        exp_str = emp.experience.value if isinstance(emp.experience, ExperienceLevel) else emp.experience
                        
                        role_badge = ROLE_CSS.get(role_str, f"<span>{role_str}</span>")
                        exp_badge = EXP_CSS.get(exp_str, f"<span>{exp_str}</span>")
                        
                        st.markdown(f"### {emp.name} &nbsp;&nbsp; {role_badge} &nbsp; {exp_badge}", unsafe_allow_html=True)
                        st.markdown(f"💰 **Sueldo:** ${emp.daily_wage:.2f}/día")
                        if emp.specialties:
                            st.markdown(f"🍳 **Especialidades:** {', '.join(chef_spec.capitalize() for chef_spec in emp.specialties)}")
                    
                    with c2:
                        st.markdown("<br>", unsafe_allow_html=True)
                        if st.button("🔴 Despedir", key=f"fire_{emp_id}", type="secondary", use_container_width=True):
                            del restaurant.employees[emp_id]
                            save_callback()
                            st.warning(f"{emp.name} ha sido retirado de la nómina activa.")
                            st.rerun()

    # ─── PESTAÑA 2: BOLSA DE EMPLEO ───
    with tab2:
        st.markdown("### Recomendación Estratégica de Candidatos")
        st.markdown("<p style='color: gray;'>El motor prioriza automáticamente los puestos que poseen mayor déficit en base a la configuración de tu salón.</p>", unsafe_allow_html=True)

        # 📊 Cuadro de Métricas de Personal (Algoritmo transparente)
        chef_def = calculate_role_deficit(restaurant, EmployeeRole.CHEF)
        waiter_def = calculate_role_deficit(restaurant, EmployeeRole.WAITER)

        c_metric1, c_metric2 = st.columns(2)
        with c_metric1:
            st.metric(
                label="Déficit de Chefs", 
                value=f"{chef_def} vacantes" if chef_def > 0 else "Estable", 
                delta=f"+{chef_def}" if chef_def > 0 else "Balanceado",
                delta_color="inverse" if chef_def > 0 else "off"
            )
        with c_metric2:
            st.metric(
                label="Déficit de Camareros", 
                value=f"{waiter_def} vacantes" if waiter_def > 0 else "Estable", 
                delta=f"+{waiter_def}" if waiter_def > 0 else "Balanceado",
                delta_color="inverse" if waiter_def > 0 else "off"
            )

        st.divider()

        # Normalizar y ordenar candidatos según prioridad
        def score_candidate(cand) -> int:
            role_enum = cand["role"] if isinstance(cand["role"], EmployeeRole) else EmployeeRole(cand["role"])
            return chef_def if role_enum == EmployeeRole.CHEF else waiter_def

        sorted_applicants = sorted(restaurant.applicants, key=score_candidate, reverse=True)

        for idx, cand in enumerate(sorted_applicants):
            # Evitar colisión si ya fue contratado en sesión activa
            if any(emp.name == cand["name"] for emp in restaurant.employees.values()):
                continue

            deficit = score_candidate(cand)
            priority_tag = (
                "<span style='background-color: rgba(231, 111, 81, 0.2); color: #e76f51; "
                "padding: 3px 8px; border-radius: 4px; font-size: 0.7rem; font-weight: bold; "
                "border: 1px solid rgba(231, 111, 81, 0.3);'>🎯 ALTA PRIORIDAD</span>"
                if deficit > 0 else ""
            )

            with st.container(border=True):
                co1, co2 = st.columns([3, 1])
                with co1:
                    role_str = cand["role"].value if isinstance(cand["role"], EmployeeRole) else cand["role"]
                    exp_str = cand["experience"].value if isinstance(cand["experience"], ExperienceLevel) else cand["experience"]
                    
                    role_badge = ROLE_CSS.get(role_str, f"<span>{role_str}</span>")
                    exp_badge = EXP_CSS.get(exp_str, f"<span>{exp_str}</span>")
                    
                    st.markdown(f"### {cand['name']} &nbsp;&nbsp; {role_badge} &nbsp; {exp_badge} &nbsp; {priority_tag}", unsafe_allow_html=True)
                    st.markdown(f"💰 **Pretensión salarial:** `${cand['daily_wage']:.2f}/día`")
                    st.markdown(f"📖 **Biografía:** *\"{cand['bio']}\"*")
                    if cand.get("specialties"):
                        st.markdown(f"🍳 **Especialidades:** {', '.join(spec.capitalize() for spec in cand['specialties'])}")
                
                with co2:
                    st.markdown("<br>", unsafe_allow_html=True)
                    if st.button("✅ Contratar", key=f"hire_{idx}", type="primary", use_container_width=True):
                        if restaurant.balance < cand["daily_wage"]:
                            st.error("Saldo insuficiente en el balance para costear la inducción diaria de este candidato.")
                        else:
                            # Parseo estricto a enums para prevenir fallos en ejecuciones futuras
                            role_enum = cand["role"] if isinstance(cand["role"], EmployeeRole) else EmployeeRole(cand["role"])
                            exp_enum = cand["experience"] if isinstance(cand["experience"], ExperienceLevel) else ExperienceLevel(cand["experience"])
                            
                            emp_id = f"emp_{uuid.uuid4().hex[:6]}"
                            new_emp = Employee(
                                id=emp_id,
                                name=cand["name"],
                                role=role_enum,
                                experience=exp_enum,
                                specialties=cand["specialties"],
                                daily_wage=cand["daily_wage"]
                            )
                            # Registrar contratación y deducir capital inicial de contratación
                            restaurant.employees[emp_id] = new_emp
                            restaurant.add_transaction(-new_emp.daily_wage, f"Contratación de {new_emp.name}")
                            restaurant.applicants.remove(cand)
                            save_callback()
                            st.success(f"¡{new_emp.name} se ha unido formalmente a tu equipo!")
                            st.rerun()

                    if st.button("🗑️ Descartar", key=f"del_cand_{idx}", type="secondary", use_container_width=True):
                        restaurant.applicants.remove(cand)
                        save_callback()
                        st.rerun()

# ─── PESTAÑA 3: AÑADIR NUEVO CANDIDATO ───
    with tab3:
        st.markdown("### Registrar Postulación Externa")
        with st.form("nuevo_candidato"):
            nombre = st.text_input("Nombre y Apellidos completos", placeholder="Ej: Roberto Rossi")
            
            col_form1, col_form2, col_form3 = st.columns(3)
            with col_form1:
                rol = st.selectbox("Puesto de Postulación", ["Chef", "Camarero"])
            with col_form2:
                experiencia = st.selectbox("Nivel de Experiencia", ["Junior", "Senior"])
            with col_form3:
                salario = st.number_input("Pretensión salarial ($/día)", min_value=10.0, value=75.0, step=5.0)

            # Selección de especialidades existentes o añadir nueva
            st.markdown("##### Especialidades")
            especialidades_seleccionadas = st.multiselect(
                "Especialidades culinarias aplicables (Solo Chefs):",
                options=all_existing_specialties,
                help="Selecciona especialidades preexistentes para el catálogo del restaurante."
            )
            
            otra_especialidad = st.text_input("Especialidad personalizada (Si no está en la lista)", placeholder="Ej: repostería")
            if otra_especialidad.strip():
                clean_spec = otra_especialidad.strip().lower()
                if clean_spec not in especialidades_seleccionadas:
                    especialidades_seleccionadas.append(clean_spec)

            biografia = st.text_area("Biografía y Referencias", placeholder="Breve historia o referencias culinarias de anteriores restaurantes...")
            
            enviado = st.form_submit_button("📋 Registrar Candidato", use_container_width=True)

            if enviado:
                if not nombre.strip():
                    st.error("El nombre del candidato es obligatorio.")
                else:
                    role_enum = EmployeeRole.CHEF if rol == "Chef" else EmployeeRole.WAITER
                    exp_enum = ExperienceLevel.SENIOR if experiencia == "Senior" else ExperienceLevel.JUNIOR

                    nuevo = {
                        "name": nombre.strip(),
                        "role": role_enum,
                        "experience": exp_enum,
                        "specialties": especialidades_seleccionadas if role_enum == EmployeeRole.CHEF else [],
                        "daily_wage": salario,
                        "bio": biografia.strip() if biografia else "Candidato registrado externamente."
                    }
                    restaurant.applicants.append(nuevo)
                    save_callback()
                    st.success(f"Candidato '{nombre.strip()}' registrado con éxito en la bolsa de empleo.")
                    st.rerun()