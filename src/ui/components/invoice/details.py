"""
Moduł zawierający komponenty UI do wyświetlania szczegółów faktury
"""
import streamlit as st
import pandas as pd
from datetime import datetime
from src.models.comment import Comment
from src.db.database import (
    get_invoice_details,
    fetch_comments,
    add_comment,
    accept_document,
    delete_comment,
    get_accounts,
    get_dimensions,
    get_budget_positions,
    get_attachment,
    get_job_tasks
)
import uuid

def display_invoice_details(invoice_id: str, company: str):
    """
    Wyświetla szczegóły faktury.
    
    Args:
        invoice_id: ID faktury
        company: Nazwa firmy
    """
    # Inicjalizacja słownika nowy_komentarz w sesji, jeśli nie istnieje
    if 'nowy_komentarz' not in st.session_state:
        st.session_state.nowy_komentarz = {
            'Nr_faktury': invoice_id,
            'Code': "",
            'Komentarz': "",
            'Pozycja_budzetowa': "",
            'Zadanie': "",
            'Nr_konta': "",
            'Kwota_netto': "",
            'W1_Dzialnosc': "",
            'W2_Rejon': "",
            'W3_ZUSL': "",
            'W4': "",
            'W5_Zasoby': "",
            'W6_Nr_poz_budz_inw': "",
            'W7_Zespol5': "",
            'W8_Gr_kapit': "",
            'W9_Rodzaj_inw': "",
            'W10_InformKW': ""
        }
    
    # Inicjalizacja zmiennych sesji
    if 'selected_budget_position' not in st.session_state:
        st.session_state.selected_budget_position = ""
        
    # Add initialization of reset_comment_form flag in display_invoice_details function
    if 'reset_comment_form' not in st.session_state:
        st.session_state.reset_comment_form = False
        
    # Add initialization of selectbox_key_suffix in display_invoice_details
    if 'selectbox_key_suffix' not in st.session_state:
        st.session_state.selectbox_key_suffix = str(uuid.uuid4())
        
    # Pobieranie szczegółów faktury
    with st.spinner('Wczytywanie szczegółów faktury...'):
        invoice_details = get_invoice_details(invoice_id, company)
    
    if not invoice_details:
        st.error(f"Nie znaleziono faktury o numerze {invoice_id} w firmie {company}.")
        return
    
    # Wyświetlanie nagłówka faktury
    st.subheader(f"Faktura {invoice_id} - {company}")
    
    # Przyciski akcji
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("Powrót do listy"):
            st.session_state.selected_invoice = None
            st.session_state.selected_company = None
            st.session_state.page = "invoice_list"
            return
    
    with col2:
        # Sprawdzamy, czy faktura nie jest już zaakceptowana
        accepted = invoice_details.get('Accepted', 0)
        if accepted != 1:
            # Sprawdzamy, czy istnieje przynajmniej jeden komentarz
            with st.spinner('Wczytywanie komentarzy...'):
                comments = fetch_comments(company, invoice_id)
            if not comments:
                st.warning("Nie można zatwierdzić faktury bez dodania komentarza.")
            else:
                # Walidacja sum kwot netto
                comment_total = sum(float(comment.get('Amount', 0) or 0) for comment in comments)
                invoice_net = float(invoice_details.get('NetAmount', 0) or 0)
                
                # Wyświetlenie podsumowania kwot
                st.write(f"**Suma komentarzy:** {comment_total:,.2f} {invoice_details.get('Currency Code', 'PLN')}")
                st.write(f"**Kwota faktury:** {invoice_net:,.2f} {invoice_details.get('Currency Code', 'PLN')}")
                
                # Sprawdzenie czy kwoty się zgadzają (tolerancja 0.01 dla błędów zaokrąglenia)
                amounts_match = abs(comment_total - invoice_net) <= 0.01
                
                if not amounts_match:
                    st.error(f"⚠️ **BŁĄD WALIDACJI:** Suma kwot w komentarzach ({comment_total:,.2f}) nie odpowiada kwocie netto faktury ({invoice_net:,.2f}). Skoryguj kwoty w komentarzach przed zatwierdzeniem.")
                    st.warning("Faktura nie może zostać zatwierdzona dopóki kwoty się nie zgadzają.")
                else:
                    st.success("✅ Kwoty są prawidłowe - suma komentarzy odpowiada kwocie faktury.")
                    
                    if st.button("Akceptuj fakturę", key="accept_invoice_button", disabled=not amounts_match):
                        with st.spinner('Zatwierdzanie faktury...'):
                            success = accept_document(invoice_id, company, st.session_state.username)
                        if success:
                            st.success("Faktura została zaakceptowana.")
                            st.session_state.page = "invoice_list"
                            return
                        else:
                            st.error("Wystąpił błąd podczas akceptacji faktury.")
        elif accepted == 1:
            st.info("Faktura została już zaakceptowana.")
    
    # Wyświetlanie szczegółów faktury
    display_invoice_header(invoice_details)
    
    display_invoice_attachments(invoice_id, company)
    display_invoice_comments(invoice_id, company)

def display_invoice_header(invoice_details: dict):
    """
    Wyświetla nagłówek faktury.
    
    Args:
        invoice_details: Szczegóły faktury
    """
    st.subheader("Dane podstawowe")
    
    # Tworzenie kolumn dla danych podstawowych
    col1, col2, col3 = st.columns(3)
    
    # Określenie statusu faktury w przyjaznej formie
    accepted = invoice_details.get('Accepted', 0)
    status_text = "Zatwierdzona" if accepted == 1 else "Nowa"
    
    with col1:
        st.write("**Dostawca:**", invoice_details.get('Buy-from Vendor Name', ''))
        st.write("**Numer faktury dostawcy:**", invoice_details.get('Vendor Invoice No_', ''))
        st.write("**Status:**", status_text)
    
    with col2:
        st.write("**Data księgowania:**", invoice_details.get('Posting Date', ''))
        st.write("**Termin płatności:**", invoice_details.get('Due Date', ''))
        
    
    with col3:
        #st.write("**Kwota netto:**", f"{invoice_details.get('NetAmount', 0):,.2f} {invoice_details.get('Currency Code', 'PLN')}")
        #st.write("**Kwota brutto:**", f"{invoice_details.get('GrossAmount', 0):,.2f} {invoice_details.get('Currency Code', 'PLN')}")
        
        #bez przecinka
        st.write("**Kwota netto:**", f"{invoice_details.get('NetAmount', 0):.2f} {invoice_details.get('Currency Code', 'PLN')}")
        st.write("**Kwota brutto:**", f"{invoice_details.get('GrossAmount', 0):.2f} {invoice_details.get('Currency Code', 'PLN')}")


def display_invoice_attachments(invoice_id: str, company: str):
    """
    Wyświetla załączniki do faktury.
    
    Args:
        invoice_id: Identyfikator faktury
        company: Nazwa firmy
    """
    st.subheader("Załączniki")
    
    # Pobieranie załączników
    attachments = get_attachment(company, invoice_id)
    
    if not attachments:
        st.info("Brak załączników.")
        return
    
    # Wyświetlanie załączników
    for attachment in attachments:
        # Określenie typu MIME na podstawie rozszerzenia pliku
        file_extension = attachment['file_name'].lower().split('.')[-1] if '.' in attachment['file_name'] else ''
        mime_type = 'application/pdf' if file_extension == 'pdf' else 'application/octet-stream'
        
        st.download_button(
            label=f"Pobierz {attachment['file_name']}",
            data=attachment['file_content'],
            file_name=attachment['file_name'],
            mime=mime_type
        )

def display_invoice_comments(invoice_id: str, company: str):
    """
    Wyświetla komentarze do faktury i umożliwia dodawanie nowych.
    
    Args:
        invoice_id: Identyfikator faktury
        company: Nazwa firmy
    """
    # Sprawdzenie, czy formularz powinien zostać zresetowany
    if st.session_state.get('reset_comment_form', False):
        # Resetowanie wszystkich pól i stanów sesji
        st.session_state.nowy_komentarz = {
            'Nr_faktury': invoice_id,
            'Code': "",
            'Komentarz': "",
            'Pozycja_budzetowa': "",
            'Zadanie': "",
            'Nr_konta': "",
            'Kwota_netto': "",
            'W1_Dzialnosc': "",
            'W2_Rejon': "",
            'W3_ZUSL': "",
            'W4': "",
            'W5_Zasoby': "",
            'W6_Nr_poz_budz_inw': "",
            'W7_Zespol5': "",
            'W8_Gr_kapit': "",
            'W9_Rodzaj_inw': "",
            'W10_InformKW': ""
        }
        st.session_state.selected_budget_position = ""
        
        # Generowanie unikalnego identyfikatora dla kluczy selectboxów
        st.session_state.selectbox_key_suffix = str(uuid.uuid4())
        
        # Resetowanie flagi
        st.session_state.reset_comment_form = False
    
    st.subheader("Komentarze")
    
    # Lista komentarzy na całą szerokość
    st.subheader("Lista komentarzy")
    
    # Pobieranie komentarzy
    comments = fetch_comments(company, invoice_id)

    # Konwersja komentarzy na DataFrame dla lepszej prezentacji
    if comments:
        df_comments = pd.DataFrame(comments)
        
        # Formatowanie daty jeśli kolumna istnieje
        if 'Date' in df_comments.columns:
            df_comments['Date'] = df_comments['Date'].apply(
                lambda x: x.strftime('%Y-%m-%d %H:%M') if isinstance(x, datetime) else str(x)
            )
        
        # Przeorganizowanie kolumn - Amount na 4. pozycję
        if 'Amount' in df_comments.columns:
            columns = list(df_comments.columns)
            columns.remove('Amount')
            # Wstawienie Amount na pozycję 3 (indeks 3 = 4. pozycja)
            columns.insert(3, 'Amount')
            df_comments = df_comments[columns]
        
        # Wyświetlenie wszystkich pól w DataFrame
        st.dataframe(df_comments, use_container_width=True)
    
    if not comments:
        st.info("Brak komentarzy.")
    
    # Dodanie selectbox do wyboru komentarza
    if comments:
        comment_options = [f"{comment['Line No_']}: {comment['Comment']}" for comment in comments]
        selected_comment = st.selectbox("Wybierz komentarz do usunięcia", options=comment_options, key="select_comment")
        
        # Przycisk do usunięcia wybranego komentarza
        if st.button("Usuń wybrany komentarz"):
            st.session_state.confirm_delete = True

    if st.session_state.get('confirm_delete', False):
        if st.button("Potwierdź usunięcie komentarza"):
            line_no = selected_comment.split(':')[0]
            delete_comment(invoice_id, company, line_no)
            st.success("Komentarz został usunięty.")
            st.session_state.confirm_delete = False
            st.rerun()
        elif st.button("Anuluj"):
            st.session_state.confirm_delete = False
    
    # Formularz do dodawania nowych komentarzy poniżej listy
    st.subheader("Dodaj nowy komentarz")
    
    # Formularz do dodawania komentarzy
    with st.form("comment_form"):
        # Ukryte pole do przechowywania poprzedniej wartości pozycji budżetowej
        if 'previous_budget_position' not in st.session_state:
            st.session_state.previous_budget_position = ""
        
        # Pole tekstowe komentarza
        comment_text = st.text_area(
            "Treść komentarza",
            value=st.session_state.nowy_komentarz.get('Komentarz', ''), 
            height=150,
            key=f"comment_text_input_{st.session_state.selectbox_key_suffix}"
        )
        st.session_state.nowy_komentarz['Komentarz'] = comment_text

        # Pole kwota netto z kalkulatorem
        kwota_netto_input = st.text_input(
            "Kwota netto (pole obliczeniowe)", 
            help="Wprowadź wartość liczbową lub działanie matematyczne (np. 2+2-1). Przecinek zostanie automatycznie zamieniony na kropkę. Naciśnij Enter aby obliczyć działanie.",
            value=st.session_state.nowy_komentarz.get('Kwota_netto', ''),
            key=f"kwota_netto_input_{st.session_state.selectbox_key_suffix}"
        )
        
        # Walidacja i konwersja kwoty netto z obsługą działań matematycznych
        kwota_netto = ""
        if kwota_netto_input:
            kwota_netto_input = kwota_netto_input.replace(',', '.')
            
            # Sprawdzenie czy wprowadzono działanie matematyczne
            if any(op in kwota_netto_input for op in ['+', '-', '*', '/', '(', ')']):
                try:
                    # Bezpieczne obliczenie wyrażenia matematycznego
                    # Usunięcie białych znaków i sprawdzenie dozwolonych znaków
                    cleaned_input = ''.join(kwota_netto_input.split())
                    allowed_chars = set('0123456789+-*/().')
                    if set(cleaned_input).issubset(allowed_chars):
                        result = eval(cleaned_input)
                        kwota_netto = f"{result:.2f}"
                        st.session_state.nowy_komentarz['Kwota_netto'] = kwota_netto
                        st.info(f"Obliczone: {kwota_netto_input} = {kwota_netto}")
                    else:
                        st.error("Działanie zawiera niedozwolone znaki. Używaj tylko cyfr i operatorów: + - * / ( )")
                        kwota_netto = ""
                except (ValueError, SyntaxError, ZeroDivisionError):
                    st.error("Nieprawidłowe działanie matematyczne. Sprawdź składnię.")
                    kwota_netto = ""
            else:
                # Standardowa walidacja dla pojedynczej liczby
                try:
                    kwota_float = float(kwota_netto_input)
                    kwota_netto = f"{kwota_float:.2f}"
                    st.session_state.nowy_komentarz['Kwota_netto'] = kwota_netto
                except ValueError:
                    st.error("Wprowadzona wartość nie jest liczbą ani prawidłowym działaniem matematycznym.")
                    kwota_netto = ""

        # Pobieranie pozycji budżetowych
        budget_positions = get_budget_positions(company)
        if budget_positions:
            # Przygotowanie opcji do selectboxa
            budget_options = []
            budget_codes_map = {}
            account_no_map = {}
            
            for position in budget_positions:
                code = position.get('Code', '')
                account_no = position.get('Account No_', '')
                if code:
                    display_text = f"{code} - {account_no}" if account_no else code
                    budget_options.append(display_text)
                    budget_codes_map[display_text] = code
                    account_no_map[code] = account_no
            
            # Dodanie pustej opcji na początku
            budget_options.insert(0, "")
            
            # Selectbox do wyboru pozycji budżetowej
            selected_option = st.selectbox(
                "Wybierz pozycję budżetową",
                options=budget_options,
                index=0,
                key=f"budget_position_selectbox_{st.session_state.selectbox_key_suffix}"
            )
            
            # Pobieranie numeru konta dla wybranej pozycji budżetowej
            if selected_option:
                selected_code = budget_codes_map.get(selected_option, '')
                account_no = account_no_map.get(selected_code, '')
                
                # Aktualizacja stanu sesji
                st.session_state.nowy_komentarz['Pozycja_budzetowa'] = selected_code
                
                # Automatyczne ustawienie numeru konta
                if account_no:
                    st.session_state.nowy_komentarz['Nr_konta'] = account_no
                    
                # Sprawdzenie, czy pozycja budżetowa się zmieniła
                if selected_code != st.session_state.previous_budget_position:
                    st.session_state.previous_budget_position = selected_code
                    st.info("Wybrano nową pozycję budżetową. Kliknij 'Zastosuj zmiany', aby zaktualizować numer konta.")
            
            # Pobieranie wszystkich kont
            accounts = get_accounts(company)
            if accounts:
                # Tworzenie DataFrame z kontami
                accounts_df = pd.DataFrame(accounts)
                display_columns = ['No_', 'Name', 'Search Name']
                display_columns = [col for col in display_columns if col in accounts_df.columns]
                column_names = {
                    'No_': 'Numer konta',
                    'Name': 'Nazwa',
                    'Search Name': 'Nazwa wyszukiwania'
                }
                accounts_df_display = accounts_df[display_columns].rename(columns=column_names)
                
                # Przygotowanie opcji do selectboxa
                account_options = [f"{row['No_']} - {row['Name']}" for _, row in accounts_df.iterrows()]
                account_options.insert(0, "")  # Dodanie pustej opcji na początku
                
                # Znalezienie domyślnej wartości dla selectboxa kont
                default_index = 0
                current_account_no = st.session_state.nowy_komentarz.get('Nr_konta', '')
                
                if current_account_no:
                    for i, option in enumerate(account_options):
                        if option.startswith(current_account_no + " -"):
                            default_index = i
                            break
                
                # Selectbox do wyboru konta
                selected_account = st.selectbox(
                    "Wybierz konto",
                    options=account_options,
                    index=default_index,
                    key=f"account_selectbox_{st.session_state.selectbox_key_suffix}"
                )
                
                # Dodanie przycisku "Ustaw konto" obok wyboru konta
                set_account_button = st.form_submit_button("Ustaw konto")
                
                # Aktualizacja stanu sesji
                if selected_account:
                    selected_account_no = selected_account.split(' - ')[0]
                    st.session_state.nowy_komentarz['Nr_konta'] = selected_account_no
                
                # Obsługa przycisku "Ustaw konto"
                if set_account_button:
                    # Wymuszenie odświeżenia strony
                    st.rerun()
        
        # Wymiary
        col_dim1, col_dim2 = st.columns(2)
        
        with col_dim1:
            # Działalności
            dzialalnosci = get_dimensions(company, "1DZIAL")
            if dzialalnosci:
                dzialalnosci_options = [f"{dim['Code']} - {dim['Name']}" for dim in dzialalnosci]
                dzialalnosci_options.insert(0, "")
                selected_dzialalnosc = st.selectbox(
                    "Działalność", 
                    options=dzialalnosci_options,
                    index=0,
                    key=f"dzialalnosc_selectbox_{st.session_state.selectbox_key_suffix}"
                )
                if selected_dzialalnosc:
                    st.session_state.nowy_komentarz['W1_Dzialnosc'] = selected_dzialalnosc.split(' - ')[0]
            
            # Rejony
            rejony = get_dimensions(company, "1REJON")
            if rejony:
                rejony_options = [f"{dim['Code']} - {dim['Name']}" for dim in rejony]
                rejony_options.insert(0, "")
                selected_rejon = st.selectbox(
                    "Rejon", 
                    options=rejony_options,
                    index=0,
                    key=f"rejon_selectbox_{st.session_state.selectbox_key_suffix}"
                )
                if selected_rejon:
                    st.session_state.nowy_komentarz['W2_Rejon'] = selected_rejon.split(' - ')[0]
            
            # Zadania usługowe
            zusl = get_dimensions(company, "Z.USL")
            if zusl:
                zusl_options = [f"{dim['Code']} - {dim['Name']}" for dim in zusl]
                zusl_options.insert(0, "")
                selected_zusl = st.selectbox(
                    "Zadanie usługowe", 
                    options=zusl_options,
                    index=0,
                    key=f"zusl_selectbox_{st.session_state.selectbox_key_suffix}"
                )
                if selected_zusl:
                    st.session_state.nowy_komentarz['W3_ZUSL'] = selected_zusl.split(' - ')[0]

            # Pozycje budżetowe inwestycyjne
            nr_poz_budz_inwest = get_dimensions(company, "NR POZ.BUDŻ.INWEST.")
            if nr_poz_budz_inwest:
                nr_poz_budz_inwest_options = [f"{dim['Code']} - {dim['Name']}" for dim in nr_poz_budz_inwest]
                nr_poz_budz_inwest_options.insert(0, "")
                selected_nr_poz_budz_inwest = st.selectbox(
                    "Nr poz. budż. inwest.", 
                    options=nr_poz_budz_inwest_options,
                    index=0,
                    key=f"nr_poz_budz_inwest_selectbox_{st.session_state.selectbox_key_suffix}"
                )
                if selected_nr_poz_budz_inwest:
                    st.session_state.nowy_komentarz['W6_Nr_poz_budz_inw'] = selected_nr_poz_budz_inwest.split(' - ')[0]
        
        with col_dim2:
            # Zasoby
            zasoby = get_dimensions(company, "ZASOBY")
            if zasoby:
                zasoby_options = [f"{dim['Code']} - {dim['Name']}" for dim in zasoby]
                zasoby_options.insert(0, "")
                selected_zasob = st.selectbox(
                    "Zasób", 
                    options=zasoby_options,
                    index=0,
                    key=f"zasoby_selectbox_{st.session_state.selectbox_key_suffix}"
                )
                if selected_zasob:
                    st.session_state.nowy_komentarz['W5_Zasoby'] = selected_zasob.split(' - ')[0]
            
            # Zespoły 5
            zespol5 = get_dimensions(company, "ZESPOL5")
            if zespol5:
                zespol5_options = [f"{dim['Code']} - {dim['Name']}" for dim in zespol5]
                zespol5_options.insert(0, "")
                selected_zespol5 = st.selectbox(
                    "Zespół 5", 
                    options=zespol5_options,
                    index=0,
                    key=f"zespol5_selectbox_{st.session_state.selectbox_key_suffix}"
                )
                if selected_zespol5:
                    st.session_state.nowy_komentarz['W7_Zespol5'] = selected_zespol5.split(' - ')[0]
            
            # Grupy kapitałowe
            grupa_kapit = get_dimensions(company, "GR.KAPIT.")
            if grupa_kapit:
                grupa_kapit_options = [f"{dim['Code']} - {dim['Name']}" for dim in grupa_kapit]
                grupa_kapit_options.insert(0, "")
                selected_grupa_kapit = st.selectbox(
                    "Grupa kapitałowa", 
                    options=grupa_kapit_options,
                    index=0,
                    key=f"grupa_kapit_selectbox_{st.session_state.selectbox_key_suffix}"
                )
                if selected_grupa_kapit:
                    st.session_state.nowy_komentarz['W8_Gr_kapit'] = selected_grupa_kapit.split(' - ')[0]

            # INFORM. KW
            inform_kw = get_dimensions(company, "INFORM. KW")
            if inform_kw:
                inform_kw_options = [f"{dim['Code']} - {dim['Name']}" for dim in inform_kw]
                inform_kw_options.insert(0, "")
                selected_inform_kw = st.selectbox(
                    "INFORM. KW", 
                    options=inform_kw_options,
                    index=0,
                    key=f"inform_kw_selectbox_{st.session_state.selectbox_key_suffix}"
                )
                if selected_inform_kw:
                    st.session_state.nowy_komentarz['W10_InformKW'] = selected_inform_kw.split(' - ')[0]
            
            # Zadania
            zadanie_task = get_dimensions(company, "JOB TASK")
            if zadanie_task:
                zadanie_task_options = [f"{dim['Code']} - {dim['Name']}" for dim in zadanie_task]
                zadanie_task_options.insert(0, "")
                selected_zadanie_task = st.selectbox(
                    "Zadanie", 
                    options=zadanie_task_options,
                    index=0,
                    key=f"zadanie_task_selectbox_{st.session_state.selectbox_key_suffix}"
                )
                if selected_zadanie_task:
                    st.session_state.nowy_komentarz['Zadanie'] = selected_zadanie_task.split(' - ')[0]
        
        # Przycisk do dodawania komentarza
        submit_button = st.form_submit_button("Dodaj komentarz")
        
        if submit_button:
            # Tworzenie nowego komentarza z danych w stanie sesji
            new_comment = Comment(
                document_no=invoice_id,
                company=company,
                comment=st.session_state.nowy_komentarz.get('Komentarz', ''),
                nr_poz_budz=st.session_state.nowy_komentarz.get('Pozycja_budzetowa', ''),
                nr_konta=st.session_state.nowy_komentarz.get('Nr_konta', ''),
                kwota_netto=st.session_state.nowy_komentarz.get('Kwota_netto', ''),
                dzialalnosc=st.session_state.nowy_komentarz.get('W1_Dzialnosc', ''),
                rejon=st.session_state.nowy_komentarz.get('W2_Rejon', ''),
                zusl=st.session_state.nowy_komentarz.get('W3_ZUSL', ''),
                zasoby=st.session_state.nowy_komentarz.get('W5_Zasoby', ''),
                nr_poz_budz_inwest=st.session_state.nowy_komentarz.get('W6_Nr_poz_budz_inw', ''),
                zespol5=st.session_state.nowy_komentarz.get('W7_Zespol5', ''),
                grupa_kapit=st.session_state.nowy_komentarz.get('W8_Gr_kapit', ''),
                rodzaj_inwestycji=st.session_state.nowy_komentarz.get('W9_Rodzaj_inw', ''),
                inform_kw=st.session_state.nowy_komentarz.get('W10_InformKW', '')
            )
            
            # Dodawanie komentarza do bazy danych
            success = add_comment(new_comment)
            if success:
                st.success("Komentarz został dodany.")
                # Ustawienie flagi resetowania formularza
                st.session_state.reset_comment_form = True
                st.rerun()
            else:
                st.error("Wystąpił błąd podczas dodawania komentarza.")
        
        