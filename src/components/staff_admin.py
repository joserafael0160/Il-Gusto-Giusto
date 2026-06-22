import streamlit as st
import uuid
from src.models.restaurant import Restaurant, Employee, EmployeeRole, ExperienceLevel
from src.services.restaurant_service import calculate_role_deficit

def render_staff_manager(restaurant: Restaurant, save_callback):
    st.subheader("👥 Gestión de Recursos Humanos y Bolsa de Trabajo")

    # Candidatos fijos iniciales (solo se usan si la lista de applicants está vacía)
    default_applicants = [
        {
            "name": "Alessandro Moretti",
            "role": EmployeeRole.WAITER,
            "experience": ExperienceLevel.JUNIOR,
            "specialties": [],
            "daily_wage": 45.0,
            "bio": "Estudiante con buena actitud, dispuesto a dar el mejor servicio de salón."
        },
        {
            "name": "Giulia Ferrari",
            "role": EmployeeRole.WAITER,
            "experience": ExperienceLevel.SENIOR,
            "specialties": [],
            "daily_wage": 80.0,
            "bio": "Maître profesional con amplia trayectoria en hostelería gourmet."
        },
        {
            "name": "Vincenzo Romano",
            "role": EmployeeRole.CHEF,
            "experience": ExperienceLevel.SENIOR,
            "specialties": ["pizza"],
            "daily_wage": 150.0,
            "bio": "Maestro Pizzaiolo napolitano certificado. Experto en hornos tradicionales."
        },
        {
            "name": "Francesca Colombo",
            "role": EmployeeRole.CHEF,
            "experience": ExperienceLevel.JUNIOR,
            "specialties": ["pasta"],
            "daily_wage": 90.0,
            "bio": "Apasionada de las masas frescas artesanales y salsas tradicionales."
        }
    ]

    # Inicializar applicants si está vacío
    if not restaurant.applicants:
        restaurant.applicants = default_applicants

    applicants = restaurant.applicants

    # Recolectar todas las especialidades existentes en el restaurante (para sugerencias)
    all_existing_specialties = sorted(list({
        spec for emp in restaurant.employees.values() for spec in emp.specialties
    }))

    tab1, tab2, tab3 = st.tabs(["Nómina Activa", "Bolsa de Empleo", "Añadir Candidato"])

    # ─── Pestaña 1: Empleados actuales ───
    with tab1:
        role_filter = st.selectbox("Filtrar por puesto", ["Todos", "Chef", "Camarero"])
        for emp_id, emp in list(restaurant.employees.items()):
            if role_filter == "Chef" and emp.role != EmployeeRole.CHEF:
                continue
            if role_filter == "Camarero" and emp.role != EmployeeRole.WAITER:
                continue

            with st.container(border=True):
                c1, c2 = st.columns([4, 1])
                with c1:
                    st.write(f"### {emp.name} ({emp.role.value.capitalize()})")
                    st.write(f"**Experiencia:** {emp.experience.value.capitalize()} | **Salario diario:** ${emp.daily_wage:.2f}")
                    if emp.specialties:
                        st.write(f"**Especialidades:** {', '.join(emp.specialties)}")
                with c2:
                    if st.button("Despedir", key=f"fire_{emp_id}"):
                        del restaurant.employees[emp_id]
                        save_callback()
                        st.warning(f"{emp.name} ha sido despedido.")
                        st.rerun()

    # ─── Pestaña 2: Bolsa de empleo con contratación inteligente ───
    with tab2:
        st.write("### Candidatos Recomendados")
        st.info("El sistema prioriza los roles que más necesita tu restaurante en este momento.")

        chef_def = calculate_role_deficit(restaurant, EmployeeRole.CHEF)
        waiter_def = calculate_role_deficit(restaurant, EmployeeRole.WAITER)

        def score_candidate(cand):
            return chef_def if cand["role"] == EmployeeRole.CHEF else waiter_def

        sorted_applicants = sorted(applicants, key=score_candidate, reverse=True)

        for idx, cand in enumerate(sorted_applicants):
            if any(emp.name == cand["name"] for emp in restaurant.employees.values()):
                continue

            deficit = score_candidate(cand)
            tag = "🎯 Alta prioridad" if deficit > 0 else ""

            with st.container(border=True):
                co1, co2 = st.columns([4, 1])
                with co1:
                    st.markdown(f"### {cand['name']} :blue[{tag}]")
                    st.write(f"**Puesto:** {cand['role'].value.capitalize()} | **Nivel:** {cand['experience'].value.capitalize()}")
                    st.write(f"**Sueldo pretendido:** ${cand['daily_wage']:.2f}/día")
                    st.write(f"**Biografía:** *{cand['bio']}*")
                with co2:
                    col_hire, col_del = st.columns(2)
                    with col_hire:
                        if st.button("Contratar", key=f"hire_{idx}", type="primary"):
                            if restaurant.balance < cand["daily_wage"]:
                                st.error("Saldo insuficiente para contratar a este candidato.")
                            else:
                                emp_id = f"emp_{uuid.uuid4().hex[:6]}"
                                new_emp = Employee(
                                    id=emp_id,
                                    name=cand["name"],
                                    role=cand["role"],
                                    experience=cand["experience"],
                                    specialties=cand["specialties"],
                                    daily_wage=cand["daily_wage"]
                                )
                                restaurant.employees[emp_id] = new_emp
                                restaurant.add_transaction(-new_emp.daily_wage, f"Contratación de {new_emp.name}")
                                restaurant.applicants.remove(cand)
                                save_callback()
                                st.success(f"¡{new_emp.name} se ha unido al equipo!")
                                st.rerun()
                    with col_del:
                        if st.button("🗑️", key=f"del_cand_{idx}", help="Eliminar candidato de la bolsa"):
                            restaurant.applicants.remove(cand)
                            save_callback()
                            st.rerun()

    # ─── Pestaña 3: Añadir nuevo candidato ───
    with tab3:
        st.write("### Registrar nuevo candidato")
        with st.form("nuevo_candidato"):
            nombre = st.text_input("Nombre completo")
            rol = st.selectbox("Puesto", ["Chef", "Camarero"])
            experiencia = st.selectbox("Experiencia", ["Junior", "Senior"])
            salario = st.number_input("Sueldo pretendido ($/día)", min_value=10.0, value=70.0, step=5.0)

            # Especialidades: multiselect con opción de añadir una personalizada
            st.write("**Especialidades**")
            especialidades_seleccionadas = st.multiselect(
                "Selecciona las especialidades",
                options=all_existing_specialties,
                help="Puedes elegir entre las que ya existen en el restaurante."
            )
            otra_especialidad = ""
            if st.checkbox("Añadir especialidad no listada"):
                otra_especialidad = st.text_input("Especialidad personalizada", placeholder="Ej.: sushi")
                if otra_especialidad.strip():
                    # La añadimos a la lista sin duplicar
                    if otra_especialidad.strip() not in especialidades_seleccionadas:
                        especialidades_seleccionadas = especialidades_seleccionadas + [otra_especialidad.strip()]

            biografia = st.text_area("Biografía", placeholder="Breve descripción del candidato...")
            enviado = st.form_submit_button("Agregar candidato")

            if enviado:
                if not nombre.strip():
                    st.error("El nombre es obligatorio.")
                else:
                    role_enum = EmployeeRole.CHEF if rol == "Chef" else EmployeeRole.WAITER
                    exp_enum = ExperienceLevel.SENIOR if experiencia == "Senior" else ExperienceLevel.JUNIOR

                    nuevo = {
                        "name": nombre.strip(),
                        "role": role_enum,
                        "experience": exp_enum,
                        "specialties": especialidades_seleccionadas,
                        "daily_wage": salario,
                        "bio": biografia.strip() if biografia else "Sin información adicional."
                    }
                    restaurant.applicants.append(nuevo)
                    save_callback()
                    st.success(f"{nombre} añadido a la bolsa de empleo.")
                    st.rerun()