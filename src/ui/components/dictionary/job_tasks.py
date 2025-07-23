import streamlit as st
import pandas as pd
from src.db import get_job_tasks

def display_job_tasks(company: str, job_code: str):
    """
    Wyświetla słownik zadań dla danego kodu zadania.
    
    Args:
        company: Nazwa firmy
        job_code: Kod zadania
    """
    # Pobieranie zadań
    job_tasks = get_job_tasks(company, job_code)
    
    if not job_tasks:
        st.info(f"Brak zadań dla kodu {job_code} w firmie {company}.")
        return
    
    # Konwersja na DataFrame
    df = pd.DataFrame(job_tasks)
    
    # Wybór kolumn do wyświetlenia
    display_columns = [
        'Job_Task_No', 
        'Description', 
        'Job_Task_Type', 
        'WIP_Total', 
        'Job_Posting_Group'
    ]
    
    # Sprawdzenie, czy wszystkie kolumny istnieją
    display_columns = [col for col in display_columns if col in df.columns]
    
    # Zmiana nazw kolumn na bardziej przyjazne
    column_names = {
        'Job_Task_No': 'Numer zadania',
        'Description': 'Opis',
        'Job_Task_Type': 'Typ zadania',
        'WIP_Total': 'Suma WIP',
        'Job_Posting_Group': 'Grupa księgowania zadania'
    }
    
    # Filtrowanie i zmiana nazw kolumn
    df_display = df[display_columns].rename(columns=column_names)
    
    # Dodanie filtrowania
    st.subheader("Filtrowanie")
    
    # Filtr po numerze zadania
    task_number = st.text_input("Numer zadania")
    
    # Filtr po opisie zadania
    task_description = st.text_input("Opis zadania")
    
    # Filtrowanie danych
    if task_number:
        df_display = df_display[df_display['Numer zadania'].str.contains(task_number, case=False)]
    
    if task_description:
        df_display = df_display[df_display['Opis'].str.contains(task_description, case=False)]
    
    # Wyświetlenie tabeli
    st.subheader(f"Zadania dla kodu {job_code}")
    
    if df_display.empty:
        st.info("Brak zadań spełniających kryteria filtrowania.")
    else:
        st.dataframe(df_display) 