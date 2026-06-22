import streamlit as st
from src.models.restaurant import Restaurant, Employee, EmployeeRole, ExperienceLevel

def calculate_role_deficit(restaurant: Restaurant, role: EmployeeRole) -> int:
    """
    Evalúa la cantidad actual del rol comparada con un modelo balanceado del restaurante:
    Deseable: 1 Camarero por cada 2 mesas, 1 Chef por cada 3 mesas.
    """
    current_count = len([e for e in restaurant.employees.values() if e.role == role])
    num_tables = len(restaurant.tables)

    if role == EmployeeRole.WAITER:
        target = max(1, num_tables // 2)
    else:
        target = max(1, num_tables // 3)

    return target - current_count

def render_staff_manager(restaurant: Restaurant, save_callback):
    st.subheader("👥 Gestión de Recursos Humanos y Bolsa de Trabajo")

    # Bolsa de candidatos disponible para contratación
    applicants = [
        {
            "id": "cand_a",
            "name": "Alessandro Moretti",
            "role": EmployeeRole.WAITER,
            "experience": ExperienceLevel.JUNIOR,
            "specialties": [],
            "daily_wage": 45.0,
            "bio": "Estudiante con buena actitud, dispuesto a dar el mejor servicio de salón."
        },
        {
            "id": "cand_b",
            "name": "Giulia Ferrari",
            "role": EmployeeRole.WAITER,
            "experience": ExperienceLevel.SENIOR,
            "specialties": [],
            "daily_wage": 80.0,
            "bio": "Maître profesional con amplia trayectoria en hostelería gourmet."
        },
        {
            "id": "cand_c",
            "name": "Vincenzo Romano",
            "role": EmployeeRole.CHEF,
            "experience": ExperienceLevel.SENIOR,
            "specialties": ["pizza"],
            "daily_wage": 150.0,
            "bio": "Maestro Pizzaiolo napolitano certificado. Experto en hornos tradicionales."
        },
        {
            "id": "cand_d",
            "name": "Francesca Colombo",
            "role": EmployeeRole.CHEF,
            "experience": ExperienceLevel.JUNIOR,
            "specialties": ["pasta"],
            "daily_wage": 90.0,
            "bio": "Apasionada de las masas frescas artesanales y salsas tradicionales."
        }
    ]

    tab1, tab2 = st.tabs(["Nómina Activa", "Bolsa de Empleo (Contratación Inteligente)"])

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
                    st.write(f"### {emp.name} (Puesto: **{emp.role.value.capitalize()}**)")
                    st.write(f"**Rango:** {emp.experience.value.upper()} | **Salario diario:** ${emp.daily_wage:.2f}")
                    if emp.specialties:
                        st.write(f"**Especialidades:** {', '.join(emp.specialties)}")
                with c2:
                    if st.button("Despedir", key=f"fire_{emp_id}"):
                        del restaurant.employees[emp_id]
                        save_callback()
                        st.warning(f"Se ha dado de baja a {emp.name}.")
                        st.rerun()

    with tab2:
        st.write("### Candidatos Recomendados")
        st.info("El sistema evalúa el balance del personal y posiciona en primer lugar a los roles que más le hacen falta a tu restaurante.")

        # Obtener déficit del restaurante
        chef_def = calculate_role_deficit(restaurant, EmployeeRole.CHEF)
        waiter_def = calculate_role_deficit(restaurant, EmployeeRole.WAITER)

        # Criterio de ordenación: primero los candidatos cuyo rol tenga mayor déficit
        def score_candidate(cand):
            return chef_def if cand["role"] == EmployeeRole.CHEF else waiter_def

        sorted_applicants = sorted(applicants, key=score_candidate, reverse=True)

        for cand in sorted_applicants:
            if cand["id"] in restaurant.employees:
                continue

            deficit = score_candidate(cand)
            tag = "🎯 ALTA PRIORIDAD" if deficit > 0 else ""

            with st.container(border=True):
                co1, co2 = st.columns([4, 1])
                with co1:
                    st.markdown(f"### {cand['name']} :blue[{tag}]")
                    st.write(f"**Puesto:** {cand['role'].value.capitalize()} | **Nivel:** {cand['experience'].value.upper()}")
                    st.write(f"**Sueldo pretendido:** ${cand['daily_wage']:.2f}/día")
                    st.write(f"**Biografía:** *{cand['bio']}*")
                with co2:
                    if st.button("Contratar", key=f"hire_{cand['id']}", type="primary"):
                        if restaurant.balance < cand["daily_wage"]:
                            st.error("No hay suficiente capital para pagar el contrato inicial de este candidato.")
                        else:
                            new_emp = Employee(
                                id=cand["id"],
                                name=cand["name"],
                                role=cand["role"],
                                experience=cand["experience"],
                                specialties=cand["specialties"],
                                daily_wage=cand["daily_wage"]
                            )
                            restaurant.employees[new_emp.id] = new_emp
                            restaurant.add_transaction(-new_emp.daily_wage, f"Contratación de {new_emp.name}")
                            save_callback()
                            st.success(f"¡{new_emp.name} ha sido contratado!")
                            st.rerun()