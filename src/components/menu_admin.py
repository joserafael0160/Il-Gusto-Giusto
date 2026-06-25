# src/components/menu_admin.py
import streamlit as st
from src.models.restaurant import Restaurant
from src.services.restaurant_service import RestaurantService

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

    # Mostrar notificaciones persistentes
    if "menu_alert" in st.session_state and st.session_state.menu_alert:
        alert = st.session_state.menu_alert
        if alert["type"] == "success":
            st.success(alert["msg"])
        elif alert["type"] == "error":
            st.error(alert["msg"])
        del st.session_state.menu_alert

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
                
                with st.container(border=True):
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        cat_info = CATEGORY_DESIGN.get(dish.category, {"label": dish.category, "emoji": "🍽️", "color": "#888888"})
                        badge_html = (
                            f"<span style='background-color: {cat_info['color']}22; color: {cat_info['color']}; "
                            f"padding: 4px 12px; border-radius: 20px; font-size: 0.75rem; font-weight: bold; "
                            f"border: 1px solid {cat_info['color']}44;'>{cat_info['emoji']} {cat_info['label'].upper()}</span>"
                        )
                        st.markdown(badge_html, unsafe_allow_html=True)
                        st.markdown(f"## {dish.name}")
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
                        if st.button("🗑️ Eliminar Plato", key=f"del_{dish_id}", type="secondary", width='stretch'):
                            success, message = RestaurantService.delete_dish(restaurant, dish_id)
                            st.session_state.menu_alert = {
                                "type": "success" if success else "error",
                                "msg": message
                            }
                            if success:
                                save_callback()
                            st.rerun()

                    st.divider()

                    with st.expander("✏️ Editar Parámetros del Plato"):
                        edit_name = st.text_input("Nombre del plato", value=dish.name, key=f"edit_name_{dish_id}")
                        col_inputs1, col_inputs2 = st.columns(2)
                        with col_inputs1:
                            edit_price = st.number_input("Precio ($)", min_value=1.0, value=dish.price, step=0.5, key=f"edit_price_{dish_id}")
                        with col_inputs2:
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
                            for ing_name in selected_ingredients_names:
                                ing_id = all_ingredients[ing_name]
                                ing_obj = restaurant.ingredients[ing_id]
                                existing_qty = dish.ingredients.get(ing_id, 0.1)
                                existing_base = ing_id in dish.base_ingredients
                                
                                col_i1, col_i2, col_i3 = st.columns([3, 2, 2])
                                with col_i1:
                                    st.markdown(f"<p style='margin-top: 28px;'><b>{ing_obj.name}</b></p>", unsafe_allow_html=True)
                                with col_i2:
                                    qty = st.number_input(
                                        f"Cant. ({ing_obj.unit})", min_value=0.01, max_value=10.0, 
                                        value=existing_qty, step=0.01, key=f"edit_qty_{dish_id}_{ing_id}"
                                    )
                                    edit_ingredients[ing_id] = qty
                                with col_i3:
                                    st.markdown("<br>", unsafe_allow_html=True)
                                    base = st.checkbox(
                                        "Es indispensable", value=existing_base, 
                                        key=f"edit_base_{dish_id}_{ing_id}"
                                    )
                                    if base:
                                        edit_base.append(ing_id)

                        if st.button("💾 Guardar Cambios", key=f"save_edit_{dish_id}", type="primary", width='stretch'):
                            dish_payload = {
                                "name": edit_name.strip(),
                                "price": edit_price,
                                "prep_time": int(edit_prep),
                                "category": edit_cat,
                                "requires_specialty": edit_spec,
                                "ingredients": edit_ingredients,
                                "base_ingredients": edit_base
                            }
                            success, message = RestaurantService.update_dish(restaurant, dish_id, dish_payload)
                            st.session_state.menu_alert = {
                                "type": "success" if success else "error",
                                "msg": message
                            }
                            if success:
                                save_callback()
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
        new_spec = st.selectbox("Especialidad de Chef Requerida", specialty_options)
        new_spec = None if new_spec == "Ninguna" else new_spec

        st.markdown("#### Composición de Ingredientes (Receta)")
        all_ingredients = {ing.name: ing_id for ing_id, ing in restaurant.ingredients.items()}
        selected_ingredients_names = st.multiselect(
            "Selecciona los ingredientes que componen esta receta:",
            options=list(all_ingredients.keys()),
            placeholder="Buscar y añadir ingredientes..."
        )

        chosen_ingredients = {}
        base_ingredients = []

        if selected_ingredients_names:
            for ing_name in selected_ingredients_names:
                ing_id = all_ingredients[ing_name]
                ing_obj = restaurant.ingredients[ing_id]
                
                col_c1, col_c2, col_c3 = st.columns([3, 2, 2])
                with col_c1:
                    st.markdown(f"<p style='margin-top: 28px;'><b>{ing_obj.name}</b></p>", unsafe_allow_html=True)
                with col_c2:
                    qty = st.number_input(
                        f"Cantidad ({ing_obj.unit})", min_value=0.01, max_value=10.0, 
                        value=0.10, step=0.01, key=f"add_qty_{ing_id}"
                    )
                    chosen_ingredients[ing_id] = qty
                with col_c3:
                    st.markdown("<br>", unsafe_allow_html=True)
                    is_base = st.checkbox(
                        "Es indispensable", value=True, 
                        key=f"add_base_{ing_id}"
                    )
                    if is_base:
                        base_ingredients.append(ing_id)

        if st.button("📋 Publicar en Menú", type="primary", width='stretch'):
            dish_payload = {
                "name": new_name,
                "price": new_price,
                "prep_time": int(new_prep),
                "category": new_cat,
                "requires_specialty": new_spec,
                "ingredients": chosen_ingredients,
                "base_ingredients": base_ingredients
            }
            success, message = RestaurantService.publish_dish(restaurant, dish_payload)
            st.session_state.menu_alert = {
                "type": "success" if success else "error",
                "msg": message
            }
            if success:
                save_callback()
            st.rerun()