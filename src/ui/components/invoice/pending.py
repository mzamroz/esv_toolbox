import streamlit as st
import pandas as pd
from src.db import get_all_pending_invoices

def display_all_pending_invoices():
    """
    Wyświetla listę wszystkich oczekujących faktur.
    """
    # Pobieranie dokumentów
    results = get_all_pending_invoices()
    
    if not results:
        st.info("Brak oczekujących faktur do wyświetlenia.")
        return
    
    # Konwersja na DataFrame
    df = pd.DataFrame(results)
    
    # Wybór kolumn do wyświetlenia
    if not df.empty:
        display_columns = [
            'No_', 
            'Buy-from Vendor Name', 
            'Posting Date', 
            'Due Date', 
            'Vendor Invoice No_',
            'company'  # Dodajemy kolumnę z nazwą firmy
        ]
        
        # Sprawdzenie, czy wszystkie kolumny istnieją
        display_columns = [col for col in display_columns if col in df.columns]
        
        # Zmiana nazw kolumn na bardziej przyjazne
        column_names = {
            'No_': 'Numer',
            'Buy-from Vendor Name': 'Dostawca',
            'Posting Date': 'Data księgowania',
            'Due Date': 'Termin płatności',
            'Vendor Invoice No_': 'Numer faktury dostawcy',
            'company': 'Firma'
        }
        
        # Filtrowanie i zmiana nazw kolumn
        df_display = df[display_columns].rename(columns=column_names)
        
        # Dodanie filtrowania i sortowania
        st.subheader("Filtrowanie i sortowanie oczekujących faktur")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            filter_number = st.text_input("Filtruj po numerze faktury", key="pending_filter_number")
        with col2:
            filter_vendor = st.text_input("Filtruj po dostawcy", key="pending_filter_vendor")
        with col3:
            sort_option = st.selectbox(
                "Sortuj według",
                options=[
                    "Data księgowania (najnowsze)", 
                    "Data księgowania (najstarsze)", 
                    "Termin płatności (najnowsze)", 
                    "Termin płatności (najstarsze)",
                    "Dostawca (A-Z)",
                    "Dostawca (Z-A)"
                ],
                key="pending_sort_option"
            )
        
        # Filtrowanie danych
        if filter_number:
            df_display = df_display[df_display['Numer'].astype(str).str.contains(filter_number, case=False)]
        if filter_vendor:
            df_display = df_display[df_display['Dostawca'].str.contains(filter_vendor, case=False)]
        
        # Sortowanie danych
        if sort_option == "Data księgowania (najnowsze)":
            df_display = df_display.sort_values(by="Data księgowania", ascending=False)
        elif sort_option == "Data księgowania (najstarsze)":
            df_display = df_display.sort_values(by="Data księgowania", ascending=True)
        elif sort_option == "Termin płatności (najnowsze)":
            df_display = df_display.sort_values(by="Termin płatności", ascending=False)
        elif sort_option == "Termin płatności (najstarsze)":
            df_display = df_display.sort_values(by="Termin płatności", ascending=True)
        elif sort_option == "Dostawca (A-Z)":
            df_display = df_display.sort_values(by="Dostawca", ascending=True)
        elif sort_option == "Dostawca (Z-A)":
            df_display = df_display.sort_values(by="Dostawca", ascending=False)
        
        # Informacja o liczbie znalezionych faktur
        st.write(f"Znaleziono {len(df_display)} oczekujących faktur.")
        
        # Dodanie nagłówków tabeli
        col1, col2, col3, col4, col5, col6, col7 = st.columns([2, 3, 2, 2, 2, 2, 1.5])
        with col1:
            st.markdown("**Numer**")
        with col2:
            st.markdown("**Dostawca**")
        with col3:
            st.markdown("**Data księgowania**")
        with col4:
            st.markdown("**Termin płatności**")
        with col5:
            st.markdown("**Nr faktury dostawcy**")
        with col6:
            st.markdown("**Firma**")
        with col7:
            st.markdown("**Akcje**")
        
        # Linia oddzielająca nagłówki od danych
        st.markdown("---")
        
        # Wyświetlenie tabeli
        if df_display.empty:
            st.info("Brak oczekujących faktur spełniających kryteria filtrowania.")
        else:
            for i, row in df_display.iterrows():
                col1, col2, col3, col4, col5, col6, col7 = st.columns([2, 3, 2, 2, 2, 2, 1.5])
                with col1:
                    st.write(row['Numer'])
                with col2:
                    st.write(row['Dostawca'])
                with col3:
                    st.write(row['Data księgowania'])
                with col4:
                    st.write(row['Termin płatności'])
                with col5:
                    st.write(row['Numer faktury dostawcy'])
                with col6:
                    st.write(row['Firma'])
                with col7:
                    invoice_no = row['Numer']
                    company = row['Firma']
                    if st.button("Szczegóły", key=f"pending_details_{invoice_no}_{company}", type="primary", use_container_width=True):
                        st.session_state.selected_invoice = invoice_no
                        st.session_state.selected_company = company
                        st.session_state.page = "invoice_details"
                        st.rerun()
                
                # Linia oddzielająca wiersze
                st.markdown("---") 