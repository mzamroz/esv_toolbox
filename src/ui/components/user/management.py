import streamlit as st
import pandas as pd
import re
from src.db import add_user, get_all_users, delete_user, update_user

def is_valid_email(email: str) -> bool:
    """Sprawdza, czy podany adres email jest poprawny."""
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return bool(re.match(pattern, email))

def display_user_management():
    """Wyświetla panel zarządzania użytkownikami (tylko dla administratorów)."""
    if not st.session_state.get('is_admin', False):
        st.warning("Tylko administratorzy mają dostęp do zarządzania użytkownikami.")
        return
    
    st.subheader("Zarządzanie użytkownikami")
    
    # Zakładki dla różnych funkcji zarządzania użytkownikami
    tab1, tab2 = st.tabs(["Lista użytkowników", "Dodaj użytkownika"])
    
    # Zakładka z listą użytkowników
    with tab1:
        display_user_list()
    
    # Zakładka z formularzem dodawania użytkownika
    with tab2:
        display_add_user_form()

def display_user_list():
    """Wyświetla listę użytkowników z możliwością edycji i usuwania."""
    users = get_all_users()
    if not users:
        st.info("Brak użytkowników w systemie.")
    else:
        # Konwersja danych do formatu DataFrame dla lepszej prezentacji
        df = pd.DataFrame(users)
        
        # Wybór kolumn do wyświetlenia
        display_columns = ['id', 'login', 'email', 'is_admin']
        
        # Zmiana nazw kolumn na bardziej przyjazne
        column_names = {
            'login': 'Login',
            'email': 'Email',
            'is_admin': 'Administrator'
        }
        
        # Filtrowanie i zmiana nazw kolumn (zachowujemy kolumnę id)
        df_display = df[display_columns].rename(columns=column_names)
        
        # Dodanie filtrowania
        st.subheader("Filtrowanie i sortowanie")
        col1, col2, col3 = st.columns(3)
        with col1:
            filter_login = st.text_input("Filtruj po loginie")
        with col2:
            filter_email = st.text_input("Filtruj po emailu")
        with col3:
            sort_option = st.selectbox(
                "Sortuj według",
                options=["Login (A-Z)", "Login (Z-A)", "Email (A-Z)", "Email (Z-A)"]
            )
        
        # Filtrowanie danych
        if filter_login:
            df_display = df_display[df_display['Login'].str.contains(filter_login, case=False)]
        if filter_email:
            df_display = df_display[df_display['Email'].str.contains(filter_email, case=False)]
        
        # Sortowanie danych
        if sort_option == "Login (A-Z)":
            df_display = df_display.sort_values(by="Login", ascending=True)
        elif sort_option == "Login (Z-A)":
            df_display = df_display.sort_values(by="Login", ascending=False)
        elif sort_option == "Email (A-Z)":
            df_display = df_display.sort_values(by="Email", ascending=True)
        elif sort_option == "Email (Z-A)":
            df_display = df_display.sort_values(by="Email", ascending=False)
        
        # Informacja o liczbie znalezionych użytkowników
        st.write(f"Znaleziono {len(df_display)} użytkowników.")
        
        # Dodanie nagłówków tabeli
        col1, col2, col3, col4, col5 = st.columns([2, 3, 2, 1, 1])
        with col1:
            st.markdown("**Login**")
        with col2:
            st.markdown("**Email**")
        with col3:
            st.markdown("**Administrator**")
        with col4:
            st.markdown("**Edycja**")
        with col5:
            st.markdown("**Usuwanie**")
        
        # Linia oddzielająca nagłówki od danych
        st.markdown("---")
        
        # Wyświetlenie tabeli z przyciskami akcji
        if df_display.empty:
            st.info("Brak użytkowników spełniających kryteria filtrowania.")
        else:
            # Tworzymy kopię DataFrame bez kolumny id do wyświetlenia
            display_df_without_id = df_display.drop(columns=['id'])
            
            for i, row in df_display.iterrows():
                col1, col2, col3, col4, col5 = st.columns([2, 3, 2, 1, 1])
                with col1:
                    st.write(row['Login'])
                with col2:
                    st.write(row['Email'])
                with col3:
                    st.write("Tak" if row['Administrator'] else "Nie")
                with col4:
                    # Przycisk edycji - używamy id z aktualnego wiersza
                    user_id = row['id']
                    user_login = row['Login']
                    user_email = row['Email']
                    user_is_admin = row['Administrator']
                    
                    if st.button("Edytuj", key=f"edit_user_{user_id}"):
                        st.session_state.edit_user_id = user_id
                        st.session_state.edit_user_login = user_login
                        st.session_state.edit_user_email = user_email
                        st.session_state.edit_user_is_admin = user_is_admin
                with col5:
                    # Przycisk usuwania - używamy id z aktualnego wiersza
                    if st.button("Usuń", key=f"delete_user_{user_id}"):
                        if delete_user(user_id):
                            st.success(f"Użytkownik {user_login} został usunięty.")
                            st.rerun()
                        else:
                            st.error(f"Nie udało się usunąć użytkownika {user_login}.")
                
                # Linia oddzielająca wiersze
                st.markdown("---")
        
        # Formularz edycji użytkownika (wyświetlany tylko gdy wybrano użytkownika do edycji)
        if 'edit_user_id' in st.session_state:
            st.markdown("---")
            st.subheader(f"Edycja użytkownika: {st.session_state.edit_user_login}")
            
            with st.container():
                with st.form("edit_user_form"):
                    st.markdown(f"**Login:** {st.session_state.edit_user_login} (nie można zmienić)")
                    email = st.text_input("Email", value=st.session_state.edit_user_email)
                    is_admin = st.checkbox("Administrator", value=st.session_state.edit_user_is_admin)
                    password = st.text_input("Nowe hasło (pozostaw puste, aby nie zmieniać)", type="password")
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        submit = st.form_submit_button("Zapisz zmiany")
                    with col2:
                        cancel = st.form_submit_button("Anuluj edycję")
                    with col3:
                        delete_btn = st.form_submit_button("Usuń użytkownika")
                    
                    if submit:
                        if not is_valid_email(email):
                            st.error("Podany adres email jest nieprawidłowy.")
                        else:
                            if update_user(st.session_state.edit_user_id, email, is_admin, password, ):
                                st.success(f"Użytkownik {st.session_state.edit_user_login} został zaktualizowany.")
                                # Usunięcie danych edytowanego użytkownika z sesji
                                del st.session_state.edit_user_id
                                del st.session_state.edit_user_login
                                del st.session_state.edit_user_email
                                del st.session_state.edit_user_is_admin
                                st.rerun()
                            else:
                                st.error(f"Nie udało się zaktualizować użytkownika {st.session_state.edit_user_login}.")
                    
                    if cancel:
                        # Usunięcie danych edytowanego użytkownika z sesji
                        del st.session_state.edit_user_id
                        del st.session_state.edit_user_login
                        del st.session_state.edit_user_email
                        del st.session_state.edit_user_is_admin
                        st.rerun()
                    
                    if delete_btn:
                        if delete_user(st.session_state.edit_user_id):
                            st.success(f"Użytkownik {st.session_state.edit_user_login} został usunięty.")
                            # Usunięcie danych edytowanego użytkownika z sesji
                            del st.session_state.edit_user_id
                            del st.session_state.edit_user_login
                            del st.session_state.edit_user_email
                            del st.session_state.edit_user_is_admin
                            st.rerun()
                        else:
                            st.error(f"Nie udało się usunąć użytkownika {st.session_state.edit_user_login}.")

def display_add_user_form():
    """Wyświetla formularz dodawania nowego użytkownika."""
    st.subheader("Dodaj nowego użytkownika")
    
    with st.form("add_user_form"):
        login = st.text_input("Login")
        email = st.text_input("Email")
        password = st.text_input("Hasło", type="password")
        is_admin = st.checkbox("Administrator")
        
        col1, col2 = st.columns(2)
        with col1:
            submit = st.form_submit_button("Dodaj użytkownika")
        with col2:
            reset = st.form_submit_button("Wyczyść formularz")
        
        if submit:
            if not login or not email or not password:
                st.error("Wszystkie pola są wymagane.")
            elif not is_valid_email(email):
                st.error("Podany adres email jest nieprawidłowy.")
            else:
                if add_user(login, password, email, is_admin):
                    st.success(f"Użytkownik {login} został dodany.")
                    # Wyczyszczenie formularza
                    st.rerun()
                else:
                    st.error(f"Nie udało się dodać użytkownika {login}. Możliwe, że login jest już zajęty.")
        
        if reset:
            # Wyczyszczenie formularza
            st.rerun() 