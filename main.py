"""
ESV Toolbox - Główny punkt wejścia aplikacji
"""
import streamlit as st
import os
import sys

# Dodanie katalogu projektu do ścieżki Pythona
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Importy z nowej struktury
from src.core.config import get_config
from src.ui.components import setup_page

# Konfiguracja strony
st.set_page_config(
    page_title="Toolbox_ESV",
    page_icon=":material/calculate:",
    layout="wide"
)

def main():
    """
    Główna funkcja aplikacji
    """
    # Konfiguracja strony
    setup_page()
    
    # Wyświetlenie logo w pasku bocznym
    with st.sidebar:
        st.logo(
            'img/logo.svg',
            size='large'
        )

    # Strona główna
    st.markdown("""
        <div style='text-align: center; padding: 1rem; border-radius: 5px; margin-bottom: 2rem;'>
            <h1>O aplikacji</h1>
            <p>Zestaw narzędzi do analizy danych wszelakich, acz zazwyczaj z prądem związanych.</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### PTPIREE")
    st.markdown("""
    Kalkulator do analizy plików PTPiREE.
    """)

    st.markdown("---")
    st.markdown("### Kalkulator stref.")
    st.markdown("""
    Kalkulator do analizy zużycia energii w strefach.
    """)

    st.markdown("---")
    st.markdown("### Zatwierdzanie faktur.")
    st.markdown("""
    Zatwierdzanie faktur W Microsoft Business Central.
    """)
    st.markdown("---")
    
    # Wyświetlenie wersji aplikacji
    config = get_config()
    st.markdown(f"Wersja {config.get('VERSION', '1.0.0')}")

if __name__ == "__main__":
    main() 