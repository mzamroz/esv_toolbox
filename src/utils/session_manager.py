import streamlit as st
import os
import time
import json
import datetime
import base64
from dotenv import load_dotenv
from src.ui.components.scripts import COOKIE_SCRIPT, get_set_cookie_script, CLEAR_COOKIE_SCRIPT

# Ładowanie zmiennych środowiskowych
load_dotenv()

# Pobieranie czasu ważności sesji z zmiennych środowiskowych (domyślnie 60 minut)
SESSION_EXPIRY_MINUTES = int(os.getenv('SESSION_EXPIRY_MINUTES', 60))

# Klucz używany do przechowywania danych sesji w cookie
COOKIE_KEY = "bc_integrator_session"

# Flaga wskazująca, czy skrypt cookie został już załadowany
_cookie_script_loaded = False

def init_session():
    """
    Inicjalizuje sesję, jeśli nie istnieje.
    """
    global _cookie_script_loaded
    
    # Inicjalizacja podstawowych zmiennych sesji
    if 'page' not in st.session_state:
        st.session_state.page = "invoice_list"
    
    if 'selected_budget_position' not in st.session_state:
        st.session_state.selected_budget_position = ""
    
    # Inicjalizacja zmiennych związanych z logowaniem
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.session_state.is_admin = False
        st.session_state.user_id = None
        st.session_state.login_time = None
        st.session_state.session_expiry = None
    
    # Próba odzyskania sesji z cookie
    try:
        restore_session_from_cookie()
    except Exception as e:
        print(f"Błąd podczas odzyskiwania sesji: {e}")
    
    # Dodajemy skrypt JavaScript do obsługi ciasteczek tylko raz
    if not _cookie_script_loaded:
        st.components.v1.html(COOKIE_SCRIPT, height=0)
        _cookie_script_loaded = True

def check_session_validity():
    """
    Sprawdza ważność sesji i wylogowuje użytkownika, jeśli sesja wygasła.
    Zwraca True, jeśli sesja jest ważna, False w przeciwnym razie.
    """
    if not st.session_state.get('logged_in', False):
        return False
    
    # Jeśli nie ma czasu wygaśnięcia sesji, ustaw go
    if not st.session_state.get('session_expiry'):
        refresh_session()
        return True
    
    # Sprawdź, czy sesja wygasła
    current_time = time.time()
    if current_time > st.session_state.session_expiry:
        # Sesja wygasła, wyloguj użytkownika
        logout_user()
        st.warning("Twoja sesja wygasła. Zaloguj się ponownie.")
        return False
    
    # Sesja jest ważna, odśwież czas wygaśnięcia
    refresh_session()
    return True

def login_user(user):
    """
    Loguje użytkownika i ustawia czas wygaśnięcia sesji.
    
    Args:
        user: Słownik z danymi użytkownika
    """
    st.session_state.logged_in = True
    st.session_state.username = user['login']
    st.session_state.user_id = user['id']
    st.session_state.is_admin = user['is_admin']
    st.session_state.login_time = time.time()
    
    # Ustaw czas wygaśnięcia sesji
    refresh_session()
    
    # Zapisz sesję w cookie
    save_session_to_cookie()

def refresh_session():
    """
    Odświeża czas wygaśnięcia sesji.
    """
    current_time = time.time()
    # Ustaw czas wygaśnięcia sesji (w sekundach)
    st.session_state.session_expiry = current_time + (SESSION_EXPIRY_MINUTES * 60)
    
    # Zapisz sesję w cookie
    save_session_to_cookie()

def logout_user():
    """
    Wylogowuje użytkownika i czyści dane sesji.
    """
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.session_state.user_id = None
    st.session_state.is_admin = False
    st.session_state.login_time = None
    st.session_state.session_expiry = None
    
    # Usuń cookie sesji
    clear_session_cookie()
    st.rerun()

def get_session_expiry_formatted():
    """
    Zwraca sformatowany czas wygaśnięcia sesji.
    """
    if not st.session_state.get('session_expiry'):
        return "Sesja nie jest aktywna"
    
    expiry_time = datetime.datetime.fromtimestamp(st.session_state.session_expiry)
    return expiry_time.strftime("%H:%M:%S %d-%m-%Y")

def save_session_to_cookie():
    """
    Zapisuje dane sesji w cookie.
    """
    if not st.session_state.get('logged_in', False):
        return
    
    # Dane sesji do zapisania
    session_data = {
        'logged_in': st.session_state.logged_in,
        'username': st.session_state.username,
        'user_id': st.session_state.user_id,
        'is_admin': st.session_state.is_admin,
        'login_time': st.session_state.login_time,
        'session_expiry': st.session_state.session_expiry
    }
    
    # Serializacja danych sesji do JSON
    serialized_data = json.dumps(session_data)
    
    # Zapisanie danych w cookie
    st.session_state[COOKIE_KEY] = serialized_data
    
    # Zapisujemy dane w query params
    try:
        # Kodowanie danych do base64 i zapisanie w query params
        st.query_params['session'] = base64.b64encode(serialized_data.encode()).decode()
    except:
        # Jeśli wystąpił błąd, ignorujemy go
        pass
    
    # Ustawiamy również ciasteczko w przeglądarce
    st.components.v1.html(get_set_cookie_script(serialized_data), height=0)

def restore_session_from_cookie():
    """
    Odzyskuje dane sesji z cookie.
    """
    # Próba odzyskania sesji z session_state
    if COOKIE_KEY in st.session_state:
        try:
            # Pobranie danych z cookie
            serialized_data = st.session_state[COOKIE_KEY]
            
            # Deserializacja danych sesji
            session_data = json.loads(serialized_data)
            
            # Sprawdzenie, czy sesja nie wygasła
            if session_data.get('session_expiry', 0) < time.time():
                clear_session_cookie()
                return
            
            # Przywrócenie danych sesji
            restore_session_data(session_data)
            return
        except:
            # Jeśli wystąpił błąd, ignorujemy go i próbujemy odzyskać sesję z query params
            pass
    
    # Próba odzyskania sesji z query params
    try:
        # Sprawdzamy, czy parametr sesji istnieje w query params
        if 'session' in st.query_params:
            # Dekodowanie danych z base64
            encoded_data = st.query_params['session']
            serialized_data = base64.b64decode(encoded_data).decode()
            
            # Deserializacja danych sesji
            session_data = json.loads(serialized_data)
            
            # Sprawdzenie, czy sesja nie wygasła
            if session_data.get('session_expiry', 0) < time.time():
                clear_session_cookie()
                return
            
            # Przywrócenie danych sesji
            restore_session_data(session_data)
            
            # Zapisanie danych również w session_state
            st.session_state[COOKIE_KEY] = serialized_data
    except:
        # Jeśli wystąpił błąd, ignorujemy go
        pass

def restore_session_data(session_data):
    """
    Przywraca dane sesji z podanego słownika.
    
    Args:
        session_data: Słownik z danymi sesji
    """
    st.session_state.logged_in = session_data.get('logged_in', False)
    st.session_state.username = session_data.get('username', "")
    st.session_state.user_id = session_data.get('user_id', None)
    st.session_state.is_admin = session_data.get('is_admin', False)
    st.session_state.login_time = session_data.get('login_time', None)
    st.session_state.session_expiry = session_data.get('session_expiry', None)

def clear_session_cookie():
    """
    Usuwa cookie sesji.
    """
    if COOKIE_KEY in st.session_state:
        del st.session_state[COOKIE_KEY]
    
    # Usuwamy parametr sesji z query params
    try:
        if 'session' in st.query_params:
            del st.query_params['session']
    except:
        pass
    
    # Usuwamy również ciasteczko w przeglądarce
    st.components.v1.html(CLEAR_COOKIE_SCRIPT, height=0) 