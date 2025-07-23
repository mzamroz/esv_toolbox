import streamlit as st
from src.db import verify_user
from src.utils.session_manager import login_user

def display_login_form():
    """Wyświetla formularz logowania."""
    # Dodajemy skrypt JavaScript do obsługi localStorage
    st.markdown("""
    <script>
    // Funkcja do zapisywania danych sesji w localStorage
    function saveSessionToLocalStorage(sessionData) {
        localStorage.setItem('bc_integrator_session', JSON.stringify(sessionData));
    }
    
    // Funkcja do odczytywania danych sesji z localStorage
    function getSessionFromLocalStorage() {
        const sessionData = localStorage.getItem('bc_integrator_session');
        return sessionData ? JSON.parse(sessionData) : null;
    }
    
    // Funkcja do usuwania danych sesji z localStorage
    function clearSessionFromLocalStorage() {
        localStorage.removeItem('bc_integrator_session');
    }
    
    // Sprawdzenie, czy w localStorage są dane sesji
    document.addEventListener('DOMContentLoaded', function() {
        const sessionData = getSessionFromLocalStorage();
        if (sessionData) {
            // Jeśli są dane sesji, wysyłamy je do Streamlit
            window.parent.postMessage({
                type: 'streamlit:setComponentValue',
                value: sessionData
            }, '*');
        }
    });
    </script>
    """, unsafe_allow_html=True)
    
    st.markdown("<h3>Logowanie</h3>", unsafe_allow_html=True)
    
    with st.form("login_form"):
        username = st.text_input("Nazwa użytkownika")
        password = st.text_input("Hasło", type="password")
        
        # Stylizowany przycisk logowania
        submit = st.form_submit_button("Zaloguj")
        
        if submit:
            if username and password:
                user = verify_user(username, password)
                if user:
                    # Używamy nowej funkcji login_user z menedżera sesji
                    login_user(user)
                    st.rerun()
                else:
                    st.error("Nieprawidłowa nazwa użytkownika lub hasło.")
            else:
                st.error("Proszę podać nazwę użytkownika i hasło.")
    
    # Informacja o aplikacji
    st.markdown('<div class="sidebar-separator"></div>', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-footer">Wprowadź dane logowania, aby uzyskać dostęp do systemu.</div>', unsafe_allow_html=True) 