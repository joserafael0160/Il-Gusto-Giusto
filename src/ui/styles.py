# src/ui/styles.py
import streamlit as st

def apply_custom_theme() -> None:
    """Injects premium, cohesive CSS styling with Italian-inspired fonts."""
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,700;1,400&family=Lato:wght@300;400;700&display=swap');

        html, body, [class*="css"]  {
            font-family: 'Lato', sans-serif;
        }
        h1, h2, h3, h4, h5, h6 {
            font-family: 'Playfair Display', serif;
        }

        /* 1. SISTEMA DE NAVEGACIÓN (BARRA LATERAL) */
        [data-testid="stSidebar"] .stButton > button {
            display: flex !important;
            justify-content: flex-start !important;
            align-items: center !important;
            text-align: left !important;
            width: 100% !important;
            padding: 12px 16px !important;
            border-radius: 8px !important;
            border: 1px solid rgba(255, 255, 255, 0.05) !important;
            font-size: 1rem !important;
            background-color: transparent !important;
            transition: all 0.2s ease-in-out !important;
        }
        
        [data-testid="stSidebar"] .stButton > button:hover {
            background-color: rgba(231, 111, 81, 0.1) !important;
            border-color: #e76f51 !important;
            color: #e76f51 !important;
        }

        [data-testid="stSidebar"] .stButton > button[kind="primary"] {
            background-color: #e76f51 !important;
            border-color: #e76f51 !important;
            color: #ffffff !important;
            font-weight: 600 !important;
            box-shadow: 0 4px 12px rgba(231, 111, 81, 0.25) !important;
        }
        
        [data-testid="stSidebar"] .stButton > button[kind="primary"]:hover {
            color: #ffffff !important;
            background-color: #d65d45 !important;
            border-color: #d65d45 !important;
        }

        /* 2. DISEÑO DE TARJETAS (CARDS) DEL DASHBOARD */
        div[data-testid="stVerticalBlockBorderContainer"] {
            border: 1px solid rgba(255, 255, 255, 0.08) !important;
            border-radius: 12px !important;
            background-color: #1a1a1a !important;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.15) !important;
            transition: transform 0.25s cubic-bezier(0.4, 0, 0.2, 1), 
                        border-color 0.25s ease-in-out, 
                        box-shadow 0.25s ease-in-out !important;
        }
        
        /* Efecto Elevación (Hover) en las Tarjetas */
        div[data-testid="stVerticalBlockBorderContainer"]:hover {
            transform: translateY(-3px);
            border-color: rgba(231, 111, 81, 0.3) !important;
            box-shadow: 0 8px 16px rgba(231, 111, 81, 0.08) !important;
        }

        /* 3. POP-OVERS Y FORMULARIOS */
        div[data-testid="stPopover"] > button {
            background-color: rgba(255, 255, 255, 0.02) !important;
            border: 1px solid rgba(255, 255, 255, 0.08) !important;
            border-radius: 6px !important;
            font-weight: 500 !important;
            transition: all 0.2s ease !important;
        }
        
        div[data-testid="stPopover"] > button:hover {
            border-color: #e76f51 !important;
            color: #e76f51 !important;
            background-color: rgba(231, 111, 81, 0.05) !important;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

def render_italian_header(title: str, subtitle: str) -> None:
    """Displays an elegant header with subtle Italian flag colors."""
    st.markdown(
        f"""
        <div style="text-align: center; margin-top: 10px; margin-bottom: 30px;">
            <div style="display: flex; justify-content: center; gap: 8px; margin-bottom: 12px;">
                <span style="display: inline-block; width: 12px; height: 12px; background-color: #2a9d8f; border-radius: 50%;"></span>
                <span style="display: inline-block; width: 12px; height: 12px; background-color: #f4f4f9; border-radius: 50%;"></span>
                <span style="display: inline-block; width: 12px; height: 12px; background-color: #e76f51; border-radius: 50%;"></span>
            </div>
            <h1 style="margin: 0; font-family: 'Playfair Display', serif; font-size: 2.5rem; color: #f4f4f9;">{title}</h1>
            <p style="color: #a0a0a5; font-size: 1rem; font-style: italic; margin-top: 5px;">{subtitle}</p>
        </div>
        """,
        unsafe_allow_html=True
    )