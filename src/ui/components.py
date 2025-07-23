"""
Moduł zawierający komponenty UI dla aplikacji ESV Toolbox
"""
import streamlit as st
from src.core.config import get_config

def setup_page():
    """
    Konfiguruje stronę Streamlit
    """
    # Dodanie niestandardowego CSS
    st.markdown("""
        <style>
        .main {
            padding: 1rem;
        }
        .stApp {
            max-width: 1200px;
            margin: 0 auto;
        }
        .stSidebar {
            background-color: #f5f5f5;
        }
        h1, h2, h3 {
            color: #2c3e50;
        }
        .info-box {
            padding: 1rem;
            border-radius: 5px;
            background-color: #e8f4f8;
            border-left: 5px solid #4b8bbf;
            margin-bottom: 1rem;
        }
        .warning-box {
            padding: 1rem;
            border-radius: 5px;
            background-color: #fff3cd;
            border-left: 5px solid #ffc107;
            margin-bottom: 1rem;
        }
        .error-box {
            padding: 1rem;
            border-radius: 5px;
            background-color: #f8d7da;
            border-left: 5px solid #dc3545;
            margin-bottom: 1rem;
        }
        .success-box {
            padding: 1rem;
            border-radius: 5px;
            background-color: #d4edda;
            border-left: 5px solid #28a745;
            margin-bottom: 1rem;
        }
        </style>
    """, unsafe_allow_html=True)

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