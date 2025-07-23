import streamlit as st
from src.utils import COMPANIES
from .accounts import display_accounts
from .dimensions import display_dimensions
from .job_tasks import display_job_tasks

def display_dictionaries():
    """
    Wyświetla interfejs do przeglądania słowników.
    """
    # Inicjalizacja stanu sesji dla wybranej firmy, jeśli nie istnieje
    if 'selected_company_dictionary' not in st.session_state:
        st.session_state.selected_company_dictionary = COMPANIES[0] if COMPANIES else ""
    
    # Wybór firmy z zapamiętaną wartością
    company = st.selectbox(
        "Wybierz firmę", 
        options=[c for c in COMPANIES], 
        key="company_dictionary_selector",
        index=COMPANIES.index(st.session_state.selected_company_dictionary) if st.session_state.selected_company_dictionary in COMPANIES else 0,
        on_change=lambda: setattr(st.session_state, 'selected_company_dictionary', st.session_state.company_dictionary_selector)
    )
    
    # Inicjalizacja stanu sesji dla wybranego słownika, jeśli nie istnieje
    if 'selected_dictionary' not in st.session_state:
        st.session_state.selected_dictionary = "Konta księgowe"
    
    # Wybór słownika z zapamiętaną wartością
    dictionary_type = st.selectbox(
        "Wybierz słownik",
        options=[
            "Konta księgowe",
            "Wymiary Z.USL",
            "Wymiary 1REJON",
            "Wymiary 1DZIAL",
            "Wymiary ZASOBY",
            "Wymiary ZESPOL5",
            "Wymiary inwestycyjne",
            "Wymiary GR.KAPIT.",
            "Wymiary INFORM. KW",
            "Wymiary RODZAJ INWESTYCJI",
            "Wymiary NR POZ.BUDŻ.INWEST.",
            "Wymiary pozycji biznesowych"
        ],
        key="dictionary_selector",
        index=list([
            "Konta księgowe",
            "Wymiary Z.USL",
            "Wymiary 1REJON",
            "Wymiary 1DZIAL",
            "Wymiary ZASOBY",
            "Wymiary ZESPOL5",
            "Wymiary inwestycyjne",
            "Wymiary GR.KAPIT.",
            "Wymiary INFORM. KW",
            "Wymiary RODZAJ INWESTYCJI",
            "Wymiary NR POZ.BUDŻ.INWEST.",
            "Wymiary pozycji biznesowych"
        ]).index(st.session_state.selected_dictionary) if st.session_state.selected_dictionary in [
            "Konta księgowe",
            "Wymiary Z.USL",
            "Wymiary 1REJON",
            "Wymiary 1DZIAL",
            "Wymiary ZASOBY",
            "Wymiary ZESPOL5",
            "Wymiary inwestycyjne",
            "Wymiary GR.KAPIT.",
            "Wymiary INFORM. KW",
            "Wymiary RODZAJ INWESTYCJI",
            "Wymiary NR POZ.BUDŻ.INWEST.",
            "Wymiary pozycji biznesowych"
        ] else 0,
        on_change=lambda: setattr(st.session_state, 'selected_dictionary', st.session_state.dictionary_selector)
    )
    
    # Wyświetlanie odpowiedniego słownika
    if dictionary_type == "Konta księgowe":
        display_accounts(company)
    elif dictionary_type.startswith("Wymiary"):
        dimension_type = dictionary_type.replace("Wymiary ", "")
        display_dimensions(dimension_type, company)
    elif dictionary_type == "Wymiary pozycji biznesowych":
        # Dodatkowy wybór kodu zadania dla wymiarów pozycji biznesowych
        job_code = st.text_input("Kod zadania")
        if job_code:
            display_job_tasks(company, job_code) 