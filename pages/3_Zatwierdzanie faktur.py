import streamlit as st
import os
from dotenv import load_dotenv

# Konfiguracja strony MUSI być pierwszym wywołaniem Streamlit
st.set_page_config(
    page_title="System Zatwierdzania Faktur",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

with st.sidebar:
    st.logo(
        'img/logo.svg',
        size='large'
        
    )

# Ładowanie zmiennych środowiskowych
load_dotenv()

# Importy z modułów aplikacji
from src.models.comment import Comment
from src.db import get_documents_for_user, get_invoice_details, accept_document
from src.db.database import SQL_SERVER_AVAILABLE, DB_NAME
from src.ui import display_invoice_details, display_invoice_form, display_invoice_list, display_login_form, display_user_management, display_all_pending_invoices, display_dictionaries
from src.utils.session_manager import init_session, check_session_validity, logout_user, get_session_expiry_formatted

# Inicjalizacja sesji na samym początku
init_session()

# Funkcja do ładowania pliku CSS
def load_css(css_file):
    with open(css_file, "r", encoding="utf-8") as f:
        css = f"<style>{f.read()}</style>"
        st.markdown(css, unsafe_allow_html=True)

def main():
    """
    Główna funkcja aplikacji.
    """
    # Ładowanie CSS
    css_path = os.path.join(os.path.dirname(__file__), "ui", "components", "styles.css")
    if os.path.exists(css_path):
        load_css(css_path)
    
    # Pasek boczny
    with st.sidebar:
        
        st.title("System Zatwierdzania Faktur")
        
        # Sprawdzenie ważności sesji
        is_session_valid = check_session_validity()
        
        if not st.session_state.logged_in:
            display_login_form()
        else:
            st.markdown(f'<p>Zalogowany jako: {st.session_state.username}</p>', unsafe_allow_html=True)
            
            # Wyświetlanie informacji o bazie danych
            if DB_NAME == "ESV-LIVE":
                st.markdown(f'<p><span style="color:red; font-weight:bold;">Baza produkcyjna</span></p>', unsafe_allow_html=True)
            elif DB_NAME == "ESV-LIVE-DEV":
                st.markdown(f'<p>Baza testowa</p>', unsafe_allow_html=True)
            
            # Wyświetlanie informacji o czasie wygaśnięcia sesji
            expiry_time = get_session_expiry_formatted()
            st.markdown(f'<p>Sesja wygaśnie: {expiry_time}</p>', unsafe_allow_html=True)
            
            # Informacja o braku połączenia z bazą danych SQL Server
            if not SQL_SERVER_AVAILABLE:
                st.warning("Brak połączenia z bazą danych SQL Server. Niektóre funkcje mogą być niedostępne.")
            
            # Separator
            st.markdown('<div class="sidebar-separator"></div>', unsafe_allow_html=True)
            
            # Menu nawigacyjne
            st.markdown("<h3>Menu</h3>", unsafe_allow_html=True)
            
            if SQL_SERVER_AVAILABLE:
                if st.button("📄 Lista faktur"):
                    st.session_state.page = "invoice_list"
            
            # Opcje tylko dla administratorów
            if st.session_state.get('is_admin', False):
                if st.button("👥 Zarządzanie użytkownikami"):
                    st.session_state.page = "user_management"
                
                if SQL_SERVER_AVAILABLE:
                    if st.button("📚 Słowniki"):
                        st.session_state.page = "dictionaries"
            
            # Separator
            st.markdown('<div class="sidebar-separator"></div>', unsafe_allow_html=True)
            
            if st.button("🚪 Wyloguj"):
                logout_user()
            
            # Stopka
            st.markdown('<div class="sidebar-footer">© 2025 System Zatwierdzania Faktur</div>', unsafe_allow_html=True)
    
    # Główna zawartość
    if not st.session_state.logged_in:
        st.title("Witaj w Systemie Zatwierdzania Faktur :)")
        st.write("Zaloguj się, aby uzyskać dostęp do systemu.")
    else:
        if not SQL_SERVER_AVAILABLE and st.session_state.page not in ["invoice_list", "user_management"]:
            st.error("Brak połączenia z bazą danych SQL Server. Ta funkcja jest obecnie niedostępna.")
            st.session_state.page = "invoice_list"
            return
        
        if st.session_state.page == "invoice_list":
            st.title("Lista faktur do zatwierdzenia")
            with st.spinner('Wczytywanie listy faktur...'):
                if st.session_state.get('is_admin', False):
                    display_all_pending_invoices()
                else:
                    display_invoice_list(st.session_state.username)
        
        elif st.session_state.page == "dictionaries":
            st.title("Słowniki")
            if st.session_state.get('is_admin', False):
                display_dictionaries()
            else:
                st.error("Brak uprawnień do wyświetlenia tej strony.")
                st.session_state.page = "invoice_list"
        
        elif st.session_state.page == "user_management":
            st.title("Zarządzanie użytkownikami")
            display_user_management()
        
        elif st.session_state.page == "invoice_details":
            if 'selected_invoice' in st.session_state and 'selected_company' in st.session_state:
                display_invoice_details(st.session_state.selected_invoice, st.session_state.selected_company)
            else:
                st.error("Brak danych faktury do wyświetlenia.")
                st.session_state.page = "invoice_list"

if __name__ == "__main__":
    main() 