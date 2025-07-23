import streamlit as st
import pandas as pd
from src.db import get_dimensions

def display_dimensions(dimension_type: str, company: str):
    """
    Wyświetla słownik wymiarów.
    
    Args:
        dimension_type: Typ wymiaru
        company: Nazwa firmy
    """
    # Informacja o specjalnych wymiarach
    if dimension_type == "Z.USL":
        st.info("Wymiary Z.USL są używane do klasyfikacji usług.")
    elif dimension_type == "1REJON":
        st.info("Wymiary 1REJON są używane do klasyfikacji rejonów geograficznych.")
    elif dimension_type == "inwestycyjne":
        st.info("Wymiary inwestycyjne są używane do klasyfikacji projektów inwestycyjnych.")
    elif dimension_type == "NR POZ.BUDŻ.INWEST.":
        st.info("Wymiary NR POZ.BUDŻ.INWEST. są używane do klasyfikacji pozycji budżetowych inwestycyjnych.")
    
    # Pobieranie wymiarów
    dimensions = get_dimensions(company, dimension_type)
    
    if not dimensions:
        st.info(f"Brak wymiarów typu {dimension_type} dla firmy {company}.")
        return
    
    # Konwersja na DataFrame
    df = pd.DataFrame(dimensions)
    
    # Wybór kolumn do wyświetlenia
    display_columns = [
        'Code', 
        'Name', 
        'Dimension_Value_Type', 
        'Totaling', 
        'Blocked'
    ]
    
    # Sprawdzenie, czy wszystkie kolumny istnieją
    display_columns = [col for col in display_columns if col in df.columns]
    
    # Zmiana nazw kolumn na bardziej przyjazne
    column_names = {
        'Code': 'Kod',
        'Name': 'Nazwa',
        'Dimension_Value_Type': 'Typ wartości wymiaru',
        'Totaling': 'Sumowanie',
        'Blocked': 'Zablokowany'
    }
    
    # Filtrowanie i zmiana nazw kolumn
    df_display = df[display_columns].rename(columns=column_names)
    
    # Dodanie filtrowania
    st.subheader("Filtrowanie")
    
    # Filtr po kodzie wymiaru
    dimension_code = st.text_input("Kod wymiaru")
    
    # Filtr po nazwie wymiaru
    dimension_name = st.text_input("Nazwa wymiaru")
    
    # Filtrowanie danych
    if dimension_code:
        df_display = df_display[df_display['Kod'].str.contains(dimension_code, case=False)]
    
    if dimension_name:
        df_display = df_display[df_display['Nazwa'].str.contains(dimension_name, case=False)]
    
    # Wyświetlenie tabeli
    st.subheader(f"Wymiary {dimension_type}")
    
    if df_display.empty:
        st.info("Brak wymiarów spełniających kryteria filtrowania.")
    else:
        st.dataframe(df_display) 