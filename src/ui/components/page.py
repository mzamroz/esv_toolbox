"""
Moduł zawierający funkcje konfiguracyjne strony.
"""
import streamlit as st
import os

def setup_page():
    """
    Konfiguruje podstawowe ustawienia strony.
    """
    # Wczytanie pliku CSS
    css_path = os.path.join(os.path.dirname(__file__), 'styles.css')
    if os.path.exists(css_path):
        with open(css_path) as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
    
    # Ukrycie menu i stopki Streamlit
    hide_streamlit_style = """
        <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        </style>
    """
    st.markdown(hide_streamlit_style, unsafe_allow_html=True) 