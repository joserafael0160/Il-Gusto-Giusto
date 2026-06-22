import streamlit as st
from src.models.restaurant import Dish, Restaurant

def render_menu_manager(restaurant: Restaurant, save_callback):
    st.subheader("🍕 Gestión de Carta (Menú)")

    tab1, tab2 = st.tabs(["Ver y Editar", "Agregar Nuevo Plato"])

    with tab1:
        if not restaurant.menu:
            st.info("No hay platos disponibles en la carta.")
        else:
            for dish_id, dish in list(restaurant.menu.items()):
                with st.container(border=True):
                    col1, col2, col3 = st.columns([3, 2, 1])
                    with col1:
                        st.markdown(f"### {dish.name} (`{dish.id}`)")
                        st.markdown(f"**Categoría:** {dish.category} | **Prep:** {dish.prep_time} min")
                    with col2:
                        st.write("**Ingredientes:**")
                        for ing_id, qty in dish.ingredients.items():
                            base_label = "Indispensable" if ing_id in dish.base_ingredients else "Opcional"
                            st.write(f"- {ing_id}: {qty} ({base_label})")
                    with col3:
                        st.markdown(f"### ${dish.price:.2f}")
                        if st.button("Quitar Plato", key=f"del_{dish_id}", type="secondary"):
                            del restaurant.menu[dish_id]
                            save_callback()
                            st.success("Plato retirado de la carta.")
                            st.rerun()

    with tab2:
        st.write("### Crear Nueva Receta")
        new_id = st.text_input("ID del plato (ej: d3)", "").strip()
        new_name = st.text_input("Nombre comercial", "").strip()
        new_price = st.number_input("Precio ($)", min_value=1.0, value=15.0, step=0.5)
        new_prep = st.number_input("Tiempo de elaboración (minutos)", min_value=1, value=15)
        new_cat = st.selectbox("Categoría", ["pizza", "pasta", "seafood", "cheese_heavy", "truffle_specialty", "dessert"])
        new_spec = st.text_input("Especialidad requerida del Chef (Opcional)", "").strip() or None

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
                    is_base = st.checkbox("¿Es base indispensable?", value=True, key=f"base_add_{ing_id}")
                    if is_base:
                        base_ingredients.append(ing_id)

        if st.button("Publicar en Menú", type="primary"):
            if not new_id or not new_name:
                st.error("Por favor completa el ID y Nombre.")
            elif new_id in restaurant.menu:
                st.error("Ya existe un plato registrado con ese ID.")
            elif not chosen_ingredients:
                st.error("Debes asignarle al menos un ingrediente para construir la receta.")
            else:
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
                st.success("¡Plato guardado y publicado con éxito!")
                st.rerun()