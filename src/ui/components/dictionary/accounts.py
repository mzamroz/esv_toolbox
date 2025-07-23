import streamlit as st
import pandas as pd
from src.db import get_accounts

def display_accounts(company: str):
    """
    Wyświetla słownik kont księgowych.
    
    Args:
        company: Nazwa firmy
    """
    # Pobieranie kont księgowych
    accounts = get_accounts(company)
    
    if not accounts:
        st.info(f"Brak kont księgowych dla firmy {company}.")
        return
    
    # Konwersja na DataFrame
    df = pd.DataFrame(accounts)
    
    # Wybór kolumn do wyświetlenia
    display_columns = [
        'No_', 
        'Name', 
        'Account_Type', 
        'Income_Balance', 
        'Account_Category',
        'Direct_Posting'
    ]
    
    # Sprawdzenie, czy wszystkie kolumny istnieją
    display_columns = [col for col in display_columns if col in df.columns]
    
    # Zmiana nazw kolumn na bardziej przyjazne
    column_names = {
        'No_': 'Numer',
        'Name': 'Nazwa',
        'Account_Type': 'Typ konta',
        'Income_Balance': 'Przychód/Bilans',
        'Account_Category': 'Kategoria konta',
        'Direct_Posting': 'Księgowanie bezpośrednie'
    }
    
    # Filtrowanie i zmiana nazw kolumn
    df_display = df[display_columns].rename(columns=column_names)
    
    # Dodanie filtrowania
    st.subheader("Filtrowanie")
    
    # Filtr po numerze konta
    account_number = st.text_input("Numer konta")
    
    # Filtr po nazwie konta
    account_name = st.text_input("Nazwa konta")
    
    # Filtrowanie danych
    if account_number:
        df_display = df_display[df_display['Numer'].str.contains(account_number, case=False)]
    
    if account_name:
        df_display = df_display[df_display['Nazwa'].str.contains(account_name, case=False)]
    
    # Wyświetlenie tabeli
    st.subheader("Konta księgowe")
    
    if df_display.empty:
        st.info("Brak kont spełniających kryteria filtrowania.")
    else:
        st.dataframe(df_display) 