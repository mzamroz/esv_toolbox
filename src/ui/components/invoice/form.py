import streamlit as st
from src.utils import COMPANIES

def display_invoice_form():
    """
    Wyświetla formularz do wyszukiwania faktur.
    """
    st.subheader("Wyszukiwanie faktur")
    
    with st.form("invoice_search_form"):
        # Wybór firmy
        company = st.selectbox(
            "Firma",
            options=COMPANIES
        )
        
        # Numer faktury
        invoice_number = st.text_input("Numer faktury")
        
        # Przyciski
        col1, col2 = st.columns(2)
        with col1:
            search_button = st.form_submit_button("Szukaj")
        with col2:
            clear_button = st.form_submit_button("Wyczyść")
        
        if search_button and invoice_number:
            st.session_state.selected_invoice = invoice_number
            st.session_state.selected_company = company
            st.session_state.page = "invoice_details"
            st.rerun()
        
        if clear_button:
            st.session_state.selected_invoice = None
            st.session_state.selected_company = None 