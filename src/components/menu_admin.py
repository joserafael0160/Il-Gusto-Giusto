import streamlit as st
from src.models.restaurant import Dish, Restaurant
import uuid

def render_menu_manager(restaurant: Restaurant, save_callback):
    st.subheader("🍕 Gestión de Carta (Menú)")

    # Construir lista de especialidades disponibles (de los chefs actuales)
    all_specialties = set()
    for emp in restaurant.employees.values():
        all_specialties.update(emp.specialties)
    specialty_options = ["Ninguna"] + sorted(list(all_specialties))

    tab1, tab2 = st.tabs(["Ver y Editar", "Agregar Nuevo Plato"])

    with tab1:
        if not restaurant.menu:
            st.info("No hay platos disponibles en la carta.")
        else:
            # Mostrar lista de platos por nombre para seleccionar
            dish_options = {f"{dish.name}": dish_id for dish_id, dish in restaurant.menu.items()}
            selected_label = st.selectbox("Selecciona un plato para ver o editar", list(dish_options.keys()))
            if selected_label:
                dish_id = dish_options[selected_label]
                dish = restaurant.menu[dish_id]
                with st.container(border=True):
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.markdown(f"### {dish.name}")
                        st.write(f"**Categoría:** {dish.category.replace('_', ' ').title()} | **Tiempo:** {dish.prep_time} min | **Precio:** ${dish.price:.2f}")
                        st.write("**Ingredientes:**")
                        for ing_id, qty in dish.ingredients.items():
                            base_label = "Indispensable" if ing_id in dish.base_ingredients else "Opcional"
                            ing_obj = restaurant.ingredients.get(ing_id)
                            ing_name = ing_obj.name if ing_obj else ing_id
                            st.write(f"- {ing_name}: {qty} ({base_label})")
                    with col2:
                        if st.button("🗑️ Eliminar plato", key=f"del_{dish_id}"):
                            del restaurant.menu[dish_id]
                            save_callback()
                            st.success(f"'{dish.name}' eliminado del menú.")
                            st.rerun()

                    # Editor expandible
                    with st.expander("✏️ Editar este plato"):
                        new_name = st.text_input("Nombre del plato", value=dish.name, key=f"edit_name_{dish_id}")
                        new_price = st.number_input("Precio ($)", min_value=1.0, value=dish.price, step=0.5, key=f"edit_price_{dish_id}")
                        new_prep = st.number_input("Tiempo de preparación (min)", min_value=1, value=dish.prep_time, key=f"edit_prep_{dish_id}")
                        
                        # Categorías sin guiones bajos para mostrar
                        cat_options = ["Pizza", "Pasta", "Seafood", "Cheese Heavy", "Truffle Specialty", "Dessert"]
                        cat_values = ["pizza", "pasta", "seafood", "cheese_heavy", "truffle_specialty", "dessert"]
                        current_cat_index = cat_values.index(dish.category) if dish.category in cat_values else 0
                        new_cat_display = st.selectbox("Categoría", cat_options, index=current_cat_index, key=f"edit_cat_{dish_id}")
                        new_cat = cat_values[cat_options.index(new_cat_display)]
                        
                        # Especialidad requerida: menú desplegable
                        current_spec = dish.requires_specialty
                        if current_spec and current_spec in all_specialties:
                            spec_index = specialty_options.index(current_spec)
                        else:
                            spec_index = 0  # "Ninguna"
                        new_spec = st.selectbox(
                            "Especialidad requerida del chef",
                            specialty_options,
                            index=spec_index,
                            key=f"edit_spec_{dish_id}"
                        )
                        new_spec = None if new_spec == "Ninguna" else new_spec

                        st.write("**Ajustar ingredientes:**")
                        new_ingredients = {}
                        new_base = []
                        for ing_id, ing in restaurant.ingredients.items():
                            current_qty = dish.ingredients.get(ing_id, 0.0)
                            is_base = ing_id in dish.base_ingredients
                            c1, c2, c3 = st.columns([2, 2, 2])
                            with c1:
                                use = st.checkbox(f"Lleva {ing.name}", value=current_qty > 0, key=f"edit_use_{dish_id}_{ing_id}")
                            if use:
                                with c2:
                                    qty = st.number_input(f"Cantidad ({ing.unit})", min_value=0.01, max_value=10.0, value=current_qty if current_qty > 0 else 0.1, step=0.01, key=f"edit_qty_{dish_id}_{ing_id}")
                                    new_ingredients[ing_id] = qty
                                with c3:
                                    base = st.checkbox("Indispensable", value=is_base, key=f"edit_base_{dish_id}_{ing_id}")
                                    if base:
                                        new_base.append(ing_id)

                        if st.button("💾 Guardar cambios", key=f"save_edit_{dish_id}"):
                            if not new_name.strip():
                                st.error("El nombre no puede estar vacío.")
                            elif not new_ingredients:
                                st.error("El plato debe tener al menos un ingrediente.")
                            else:
                                dish.name = new_name.strip()
                                dish.price = new_price
                                dish.prep_time = int(new_prep)
                                dish.category = new_cat
                                dish.requires_specialty = new_spec
                                dish.ingredients = new_ingredients
                                dish.base_ingredients = new_base
                                save_callback()
                                st.success("Plato actualizado correctamente.")
                                st.rerun()

    with tab2:
        st.write("### Crear Nueva Receta")
        new_name = st.text_input("Nombre del plato", "").strip()
        new_price = st.number_input("Precio ($)", min_value=1.0, value=15.0, step=0.5)
        new_prep = st.number_input("Tiempo de elaboración (minutos)", min_value=1, value=15)
        
        cat_options = ["Pizza", "Pasta", "Seafood", "Cheese Heavy", "Truffle Specialty", "Dessert"]
        cat_values = ["pizza", "pasta", "seafood", "cheese_heavy", "truffle_specialty", "dessert"]
        new_cat_display = st.selectbox("Categoría", cat_options)
        new_cat = cat_values[cat_options.index(new_cat_display)]
        
        # Especialidad requerida: menú desplegable
        new_spec = st.selectbox(
            "Especialidad requerida del Chef",
            specialty_options,
            help="Selecciona 'Ninguna' si el plato no requiere una especialidad particular."
        )
        new_spec = None if new_spec == "Ninguna" else new_spec

        st.write("#### Asignación de Ingredientes:")
        chosen_ingredients = {}
        base_ingredients = []

        for ing_id, ing in restaurant.ingredients.items():
            c1, c2, c3 = st.columns([2, 2, 2])
            with c1:
                use_it = st.checkbox(f"Lleva {ing.name}", key=f"add_{ing_id}")
            if use_it:
                with c2:
                    qty = st.number_input(f"Cantidad ({ing.unit})", min_value=0.01, max_value=10.0, value=0.1, step=0.01, key=f"qty_add_{ing_id}")
                    chosen_ingredients[ing_id] = qty
                with c3:
                    is_base = st.checkbox("Es indispensable", value=True, key=f"base_add_{ing_id}")
                    if is_base:
                        base_ingredients.append(ing_id)

        if st.button("📋 Publicar en Menú", type="primary"):
            if not new_name:
                st.error("Debes darle un nombre al plato.")
            elif not chosen_ingredients:
                st.error("Asigna al menos un ingrediente.")
            else:
                new_id = f"dish_{uuid.uuid4().hex[:6]}"
                new_dish = Dish(
                    id=new_id,
                    name=new_name,
                    price=new_price,
                    prep_time=int(new_prep),
                    ingredients=chosen_ingredients,
                    base_ingredients=base_ingredients,
                    category=new_cat,
                    requires_specialty=new_spec
                )
                restaurant.menu[new_id] = new_dish
                save_callback()
                st.success(f"¡'{new_name}' añadido al menú!")
                st.rerun()