"""
Moduł zawierający komponenty box UI dla aplikacji ESV Toolbox
"""
import streamlit as st
from src.core.config import get_config

def info_box(text, title=None):
    """
    Wyświetla pole informacyjne
    
    Args:
        text (str): Tekst do wyświetlenia
        title (str, optional): Tytuł pola
    """
    title_html = f"<h4>{title}</h4>" if title else ""
    st.markdown(f"""
        <div class="info-box">
            {title_html}
            <p>{text}</p>
        </div>
    """, unsafe_allow_html=True)

def warning_box(text, title=None):
    """
    Wyświetla pole ostrzegawcze
    
    Args:
        text (str): Tekst do wyświetlenia
        title (str, optional): Tytuł pola
    """
    title_html = f"<h4>{title}</h4>" if title else ""
    st.markdown(f"""
        <div class="warning-box">
            {title_html}
            <p>{text}</p>
        </div>
    """, unsafe_allow_html=True)

def error_box(text, title=None):
    """
    Wyświetla pole błędu
    
    Args:
        text (str): Tekst do wyświetlenia
        title (str, optional): Tytuł pola
    """
    title_html = f"<h4>{title}</h4>" if title else ""
    st.markdown(f"""
        <div class="error-box">
            {title_html}
            <p>{text}</p>
        </div>
    """, unsafe_allow_html=True)

def success_box(text, title=None):
    """
    Wyświetla pole sukcesu
    
    Args:
        text (str): Tekst do wyświetlenia
        title (str, optional): Tytuł pola
    """
    title_html = f"<h4>{title}</h4>" if title else ""
    st.markdown(f"""
        <div class="success-box">
            {title_html}
            <p>{text}</p>
        </div>
    """, unsafe_allow_html=True)

def display_footer():
    """
    Wyświetla stopkę aplikacji
    """
    config = get_config()
    st.markdown("---")
    st.markdown(f"<p style='text-align: center;'>{config.get('APP_NAME')} | Wersja {config.get('VERSION')}</p>", unsafe_allow_html=True) 