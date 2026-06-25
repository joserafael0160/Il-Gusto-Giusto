# src/components/menu_admin.py
import streamlit as st
from src.models.restaurant import Dish, Restaurant
import uuid

# Mapa de diseño para categorías temáticas italianas
CATEGORY_DESIGN = {
    "pizza": {"label": "Pizza", "emoji": "🍕", "color": "#e76f51"},
    "pasta": {"label": "Pasta", "emoji": "🍝", "color": "#2a9d8f"},
    "seafood": {"label": "Mariscos", "emoji": "🐟", "color": "#457b9d"},
    "cheese_heavy": {"label": "Queso Pesado", "emoji": "🧀", "color": "#e9c46a"},
    "truffle_specialty": {"label": "Especialidad Trufa", "emoji": "🍄", "color": "#9b5de5"},
    "dessert": {"label": "Postres", "emoji": "🍰", "color": "#ff006e"}
}

def render_menu_manager(restaurant: Restaurant, save_callback) -> None:
    st.subheader("🍕 Gestión de Carta (Menú)")

    # Construir lista de especialidades disponibles de los chefs actuales
    all_specialties = set()
    for emp in restaurant.employees.values():
        all_specialties.update(emp.specialties)
    specialty_options = ["Ninguna"] + sorted(list(all_specialties))

    tab1, tab2 = st.tabs(["Ver y Editar Platos", "➕ Agregar Nuevo Plato"])

    with tab1:
        if not restaurant.menu:
            st.info("No hay platos disponibles en la carta actualmente.")
        else:
            dish_options = {f"{dish.name}": dish_id for dish_id, dish in restaurant.menu.items()}
            selected_label = st.selectbox("Selecciona un plato para visualizar o editar:", list(dish_options.keys()))
            
            if selected_label:
                dish_id = dish_options[selected_label]
                dish = restaurant.menu[dish_id]
                
                # Renderizar tarjeta del plato seleccionada
                with st.container(border=True):
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        # Badge de categoría estilizado
                        cat_info = CATEGORY_DESIGN.get(dish.category, {"label": dish.category, "emoji": "🍽️", "color": "#888888"})
                        badge_html = (
                            f"<span style='background-color: {cat_info['color']}22; color: {cat_info['color']}; "
                            f"padding: 4px 12px; border-radius: 20px; font-size: 0.75rem; font-weight: bold; "
                            f"border: 1px solid {cat_info['color']}44;'>{cat_info['emoji']} {cat_info['label'].upper()}</span>"
                        )
                        st.markdown(badge_html, unsafe_allow_html=True)
                        st.markdown(f"## {dish.name}")
                        
                        # Indicadores de tiempo y precio
                        st.markdown(f"⏱️ **Tiempo:** {dish.prep_time} min &nbsp;&nbsp;|&nbsp;&nbsp; 💰 **Precio:** ${dish.price:.2f}")
                        
                        if dish.requires_specialty:
                            st.markdown(f"🧑‍🍳 *Requiere especialidad de chef:* `{dish.requires_specialty}`")
                        
                        st.markdown("**Ingredientes y Receta:**")
                        for ing_id, qty in dish.ingredients.items():
                            is_base = ing_id in dish.base_ingredients
                            badge_base = (
                                "<span style='color: #e76f51; font-size: 0.85rem;'>🔒 Indispensable</span>" 
                                if is_base else "<span style='color: #2a9d8f; font-size: 0.85rem;'>🍃 Opcional</span>"
                            )
                            ing_obj = restaurant.ingredients.get(ing_id)
                            ing_name = ing_obj.name if ing_obj else ing_id
                            unit = ing_obj.unit if ing_obj else ""
                            st.markdown(f"- **{ing_name}**: `{qty} {unit}` &nbsp;&bull;&nbsp; {badge_base}", unsafe_allow_html=True)
                    
                    with col2:
                        st.markdown("<br>", unsafe_allow_html=True)
                        if st.button("🗑️ Eliminar Plato", key=f"del_{dish_id}", type="secondary", use_container_width=True):
                            del restaurant.menu[dish_id]
                            save_callback()
                            st.success(f"'{dish.name}' eliminado del menú.")
                            st.rerun()

                    st.divider()

                    # Editor de plato optimizado (Expander)
                    with st.expander("✏️ Editar Parámetros del Plato"):
                        edit_name = st.text_input("Nombre del plato", value=dish.name, key=f"edit_name_{dish_id}")
                        
                        c_inputs1, c_inputs2 = st.columns(2)
                        with c_inputs1:
                            edit_price = st.number_input("Precio ($)", min_value=1.0, value=dish.price, step=0.5, key=f"edit_price_{dish_id}")
                        with c_inputs2:
                            edit_prep = st.number_input("Tiempo de preparación (min)", min_value=1, value=dish.prep_time, key=f"edit_prep_{dish_id}")
                        
                        cat_options = ["Pizza", "Pasta", "Seafood", "Cheese Heavy", "Truffle Specialty", "Dessert"]
                        cat_values = ["pizza", "pasta", "seafood", "cheese_heavy", "truffle_specialty", "dessert"]
                        current_cat_index = cat_values.index(dish.category) if dish.category in cat_values else 0
                        edit_cat_display = st.selectbox("Categoría", cat_options, index=current_cat_index, key=f"edit_cat_{dish_id}")
                        edit_cat = cat_values[cat_options.index(edit_cat_display)]
                        
                        current_spec = dish.requires_specialty
                        spec_index = specialty_options.index(current_spec) if current_spec in specialty_options else 0
                        edit_spec = st.selectbox("Especialidad requerida del Chef", specialty_options, index=spec_index, key=f"edit_spec_{dish_id}")
                        edit_spec = None if edit_spec == "Ninguna" else edit_spec

                        st.markdown("#### Ajustar Ingredientes de la Receta")
                        
                        # Selector inteligente multiselect de ingredientes activos
                        all_ingredients = {ing.name: ing_id for ing_id, ing in restaurant.ingredients.items()}
                        active_ingredients_names = [restaurant.ingredients[ing_id].name for ing_id in dish.ingredients.keys() if ing_id in restaurant.ingredients]
                        
                        selected_ingredients_names = st.multiselect(
                            "Selecciona los ingredientes activos para este plato:",
                            options=list(all_ingredients.keys()),
                            default=active_ingredients_names,
                            key=f"edit_multiselect_{dish_id}"
                        )

                        edit_ingredients = {}
                        edit_base = []

                        if selected_ingredients_names:
                            st.markdown("<p style='color: gray; font-size: 0.9rem;'>Configura cantidades y restricciones para los ingredientes seleccionados:</p>", unsafe_allow_html=True)
                            for ing_name in selected_ingredients_names:
                                ing_id = all_ingredients[ing_name]
                                ing_obj = restaurant.ingredients[ing_id]
                                
                                # Cargar valores existentes o asignar valores por defecto
                                existing_qty = dish.ingredients.get(ing_id, 0.1)
                                existing_base = ing_id in dish.base_ingredients
                                
                                c1, c2, c3 = st.columns([3, 2, 2])
                                with c1:
                                    st.markdown(f"<p style='margin-top: 28px;'><b>{ing_obj.name}</b></p>", unsafe_allow_html=True)
                                with c2:
                                    qty = st.number_input(
                                        f"Cant. ({ing_obj.unit})", min_value=0.01, max_value=10.0, 
                                        value=existing_qty, step=0.01, key=f"edit_qty_{dish_id}_{ing_id}"
                                    )
                                    edit_ingredients[ing_id] = qty
                                with c3:
                                    st.markdown("<br>", unsafe_allow_html=True)
                                    base = st.checkbox(
                                        "Es indispensable", value=existing_base, 
                                        key=f"edit_base_{dish_id}_{ing_id}"
                                    )
                                    if base:
                                        edit_base.append(ing_id)
                        else:
                            st.warning("El plato debe poseer al menos un ingrediente para guardarse.")

                        if st.button("💾 Guardar Cambios", key=f"save_edit_{dish_id}", type="primary", use_container_width=True):
                            if not edit_name.strip():
                                st.error("El nombre del plato no puede estar vacío.")
                            elif not edit_ingredients:
                                st.error("Debes seleccionar al menos un ingrediente activo.")
                            else:
                                dish.name = edit_name.strip()
                                dish.price = edit_price
                                dish.prep_time = int(edit_prep)
                                dish.category = edit_cat
                                dish.requires_specialty = edit_spec
                                dish.ingredients = edit_ingredients
                                dish.base_ingredients = edit_base
                                save_callback()
                                st.success("Plato actualizado correctamente en el menú.")
                                st.rerun()

    with tab2:
        st.markdown("### 📝 Crear Nueva Receta")
        
        new_name = st.text_input("Nombre completo de la receta", placeholder="Ej: Pizza Carbonara").strip()
        
        col_new1, col_new2 = st.columns(2)
        with col_new1:
            new_price = st.number_input("Precio de venta ($)", min_value=1.0, value=12.0, step=0.5)
        with col_new2:
            new_prep = st.number_input("Tiempo estimado de cocina (minutos)", min_value=1, value=15)
        
        cat_options = ["Pizza", "Pasta", "Seafood", "Cheese Heavy", "Truffle Specialty", "Dessert"]
        cat_values = ["pizza", "pasta", "seafood", "cheese_heavy", "truffle_specialty", "dessert"]
        new_cat_display = st.selectbox("Categoría del plato", cat_options)
        new_cat = cat_values[cat_options.index(new_cat_display)]
        
        new_spec = st.selectbox("Especialidad de Chef Requerida", specialty_options, help="Selecciona 'Ninguna' si cualquier chef puede elaborarlo.")
        new_spec = None if new_spec == "Ninguna" else new_spec

        st.markdown("#### Composición de Ingredientes (Receta)")
        
        # Selector multiselect dinámico para creación
        all_ingredients = {ing.name: ing_id for ing_id, ing in restaurant.ingredients.items()}
        selected_ingredients_names = st.multiselect(
            "Selecciona los ingredientes que componen esta receta:",
            options=list(all_ingredients.keys()),
            placeholder="Buscar y añadir ingredientes..."
        )

        chosen_ingredients = {}
        base_ingredients = []

        if selected_ingredients_names:
            st.markdown("<p style='color: gray; font-size: 0.9rem;'>Asigna cantidades e indispensables para el nuevo plato:</p>", unsafe_allow_html=True)
            for ing_name in selected_ingredients_names:
                ing_id = all_ingredients[ing_name]
                ing_obj = restaurant.ingredients[ing_id]
                
                c1, c2, c3 = st.columns([3, 2, 2])
                with c1:
                    st.markdown(f"<p style='margin-top: 28px;'><b>{ing_obj.name}</b></p>", unsafe_allow_html=True)
                with c2:
                    qty = st.number_input(
                        f"Cantidad ({ing_obj.unit})", min_value=0.01, max_value=10.0, 
                        value=0.10, step=0.01, key=f"add_qty_{ing_id}"
                    )
                    chosen_ingredients[ing_id] = qty
                with c3:
                    st.markdown("<br>", unsafe_allow_html=True)
                    is_base = st.checkbox(
                        "Es indispensable", value=True, 
                        key=f"add_base_{ing_id}"
                    )
                    if is_base:
                        base_ingredients.append(ing_id)
        else:
            st.info("Añade ingredientes en el selector superior para estructurar la receta.")

        if st.button("📋 Publicar en Menú", type="primary", use_container_width=True):
            if not new_name:
                st.error("Por favor, ingresa el nombre de la receta.")
            elif not chosen_ingredients:
                st.error("Debes asignar al menos un ingrediente para armar la receta.")
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
                st.success(f"¡'{new_name}' ha sido publicado exitosamente en el menú de la carta!")
                st.rerun()