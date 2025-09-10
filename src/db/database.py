import os
import pyodbc
from typing import List, Dict, Any
from dotenv import load_dotenv
from src.models.comment import Comment
import streamlit as st
from src.utils.constants import COMPANIES as COMPANIES_TUPLES
import zlib
import io
import zipfile

# Ładowanie zmiennych środowiskowych
load_dotenv()

# Pobieranie konfiguracji z zmiennych środowiskowych
DB_SERVER = os.getenv("DB_SERVER")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")
ADMIN_MAIL = os.getenv("ADMIN_MAIL")

# Flaga określająca, czy połączenie z SQL Server jest dostępne
SQL_SERVER_AVAILABLE = True

# Ciąg połączenia do bazy danych
connection_string = f'DRIVER={{ODBC Driver 18 for SQL Server}};SERVER={DB_SERVER};DATABASE={DB_NAME};UID={DB_USER};PWD={DB_PASSWORD}; TrustServerCertificate=yes; Encrypt=yes;'

def get_connection():
    """Tworzy i zwraca połączenie do bazy danych."""
    global SQL_SERVER_AVAILABLE
    try:
        return pyodbc.connect(connection_string)
    except Exception as e:
        print(f"Błąd połączenia z bazą danych SQL Server: {str(e)}")
        SQL_SERVER_AVAILABLE = False
        # Zwracamy None, aby funkcje mogły obsłużyć brak połączenia
        return None

def fetch_dict_data(company: str = None, table: str = None, fields: str = None, condition: str = None) -> List[Dict[str, Any]]:
    """
    Pobiera dane z tabeli w formacie słownika.
    
    Args:
        company: Nazwa firmy
        table: Nazwa tabeli
        fields: Pola do pobrania
        condition: Warunek WHERE
        
    Returns:
        Lista słowników z danymi
    """
    conn = get_connection()
    if not conn:
        return []
    
    try:
        # Zabezpieczenie przed znakami specjalnymi w nazwach tabel
        if company and "." in company:
            st.warning(f"Nazwa firmy '{company}' zawiera znaki specjalne, które mogą powodować problemy z zapytaniem SQL.")
        
        # Tworzenie zapytania SQL
        if condition is not None:
            SQL_QUERY = f'SELECT {fields} FROM [dbo].[{company}${table}] WHERE {condition}'
        else:
            SQL_QUERY = f'SELECT {fields} FROM [dbo].[{company}${table}]'
        
        # Logowanie zapytania SQL (tylko w trybie deweloperskim)
        if os.environ.get('DEBUG_MODE') == 'True':
            print(f"Wykonywane zapytanie SQL: {SQL_QUERY}")
        
        # Wykonanie zapytania
        cursor = conn.cursor()
        try:
            cursor.execute(SQL_QUERY)
        except Exception as e:
            # Jeśli wystąpił błąd, spróbuj alternatywnego zapytania dla wymiarów z kropkami
            if "Invalid object name" in str(e) and "Dimension" in table and condition and "Z.USL" in condition:
                # Próba z alternatywnym kodem wymiaru
                alternative_condition = condition.replace("Z.USL", "Z_USL")
                SQL_QUERY = f'SELECT {fields} FROM [dbo].[{company}${table}] WHERE {alternative_condition}'
                
                if os.environ.get('DEBUG_MODE') == 'True':
                    print(f"Próba alternatywnego zapytania SQL: {SQL_QUERY}")
                
                cursor.execute(SQL_QUERY)
            else:
                # Jeśli to nie jest problem z wymiarem Z.USL, przekaż wyjątek dalej
                raise
        
        # Przetwarzanie wyników
        columns = [column[0] for column in cursor.description]
        results = []
        data = cursor.fetchall()
        for row in data:
            results.append(dict(zip(columns, row)))
        cursor.close()
        return results
    except Exception as e:
        error_msg = str(e)
        st.error(f"Błąd podczas pobierania danych: {error_msg}")
        
        # Dodatkowe informacje diagnostyczne
        if "Invalid object name" in error_msg:
            st.error(f"Nie znaleziono tabeli. Sprawdź nazwę firmy '{company}' i tabeli '{table}'.")
        
        return []
    finally:
        conn.close()

def get_documents(company: str) -> List[Dict[str, Any]]:
    """
    Pobiera listę dokumentów dla danej firmy.
    
    Args:
        company: Nazwa firmy
        
    Returns:
        Lista dokumentów
    """
    fields = '''[No_]
      ,[Buy-from Vendor No_]
      ,[Posting Date]
      ,[Allert]
      ,[Payment Terms Code]
      ,[Due Date]
      ,[Shortcut Dimension 1 Code]
      ,[Shortcut Dimension 2 Code]
      ,[Currency Code]
      ,[Vendor Order No_]
      ,[Vendor Shipment No_]
      ,[Vendor Invoice No_]
      ,[Vat Registration No_]
      ,[Vat Country_Region Code]
      ,[Buy-from Vendor Name]
      ,[Buy-from Vendor Name 2]
      ,[Buy-from Address]
      ,[Buy-from Address 2]
      ,[Buy-from City]
      ,[Buy-from Contact]
      ,[Buy-from Post Code]
      ,[Buy-from County]
      ,[Buy-from Country_Region Code]
      ,[Document Date]
      ,[Payment Method Code]
      ,[No_ Series]
      ,[Posting No_ Series]
      ,[Dimension Set ID]
      ,[Buy-from Contact No_]
      ,[Document Receipt Date]
      ,[Registration No_]
      ,[Registration No_ 2]
      ,[VAT Date]
      ,[Attachment]
      ,[AttachName]
      ,[PageLink]
      ,[SendToMer]
      ,[SendToAcc]
      ,[SendToFinan]
      ,[Vendor Bank Account No_]
      ,[NetAmount]
      ,[Register Date]
      ,[Register Date_Time]
      ,[Registered By]
      ,[Document Type]
      ,[Zarejestrowany]
      ,[Exist Purchase Header]
      ,[Accepted]
      ,[Akcepted Mer By]
      ,[Akcepted Date Time]
      ,[Send to]
      ,[Financial Acceptance]
      ,[Payment Acceptance]
      ,[Fin_ Act_ By]
      ,[Pay_ Act_ By]
      ,[SendToAccept]
      ,[UserString]
      ,[CreatedBy]
      ,[Order No_]
      ,[GrossAmount]
      ,[Cash]
      ,[Vendor Bank Account Code]
    '''
    
    result = fetch_dict_data(
        company=company, 
        fields=fields, 
        table='Log Incoming Document$b64d2b42-739a-4647-b44a-fd892d64fff6'
    )
    
    return result

def get_documents_for_user(user: str) -> List[Dict[str, Any]]:
    """
    Pobiera listę dokumentów dla danego użytkownika.
    
    Args:
        user: Nazwa użytkownika
        
    Returns:
        Lista dokumentów
    """
    user = user.upper()
    fields = '''[No_]
      ,[Buy-from Vendor No_]
      ,[Posting Date]
      ,[Allert]
      ,[Payment Terms Code]
      ,[Due Date]
      ,[Shortcut Dimension 1 Code]
      ,[Shortcut Dimension 2 Code]
      ,[Currency Code]
      ,[Vendor Order No_]
      ,[Vendor Shipment No_]
      ,[Vendor Invoice No_]
      ,[Vat Registration No_]
      ,[Vat Country_Region Code]
      ,[Buy-from Vendor Name]
      ,[Buy-from Vendor Name 2]
      ,[Buy-from Address]
      ,[Buy-from Address 2]
      ,[Buy-from City]
      ,[Buy-from Contact]
      ,[Buy-from Post Code]
      ,[Buy-from County]
      ,[Buy-from Country_Region Code]
      ,[Document Date]
      ,[Payment Method Code]
      ,[No_ Series]
      ,[Posting No_ Series]
      ,[Dimension Set ID]
      ,[Buy-from Contact No_]
      ,[Document Receipt Date]
      ,[Registration No_]
      ,[Registration No_ 2]
      ,[VAT Date]
      ,[Attachment]
      ,[AttachName]
      ,[PageLink]
      ,[SendToMer]
      ,[SendToAcc]
      ,[SendToFinan]
      ,[Vendor Bank Account No_]
      ,[NetAmount]
      ,[Register Date]
      ,[Register Date_Time]
      ,[Registered By]
      ,[Document Type]
      ,[Zarejestrowany]
      ,[Exist Purchase Header]
      ,[Accepted]
      ,[Akcepted Mer By]
      ,[Akcepted Date Time]
      ,[Send to]
      ,[Financial Acceptance]
      ,[Payment Acceptance]
      ,[Fin_ Act_ By]
      ,[Pay_ Act_ By]
      ,[SendToAccept]
      ,[UserString]
      ,[CreatedBy]
      ,[Order No_]
      ,[GrossAmount]
      ,[Cash]
      ,[Vendor Bank Account Code]
    '''
    
    results = []
    for company_code, _ in COMPANIES_TUPLES:
        result = fetch_dict_data(
            company=company_code, 
            fields=fields, 
            table='Log Incoming Document$b64d2b42-739a-4647-b44a-fd892d64fff6', 
            condition=f'[Send to] = \'ESV\\{user}\' AND [Accepted] !=1'
        )
        if result:
            for doc in result:
                doc['company'] = company_code
            results.extend(result)
    
    return results

def get_all_pending_invoices() -> List[Dict[str, Any]]:
    """
    Pobiera listę wszystkich faktur do zatwierdzenia ze wszystkich firm.
    
    Returns:
        Lista faktur do zatwierdzenia
    """
    fields = '''[No_]
      ,[Buy-from Vendor No_]
      ,[Posting Date]
      ,[Allert]
      ,[Payment Terms Code]
      ,[Due Date]
      ,[Shortcut Dimension 1 Code]
      ,[Shortcut Dimension 2 Code]
      ,[Currency Code]
      ,[Vendor Order No_]
      ,[Vendor Shipment No_]
      ,[Vendor Invoice No_]
      ,[Vat Registration No_]
      ,[Vat Country_Region Code]
      ,[Buy-from Vendor Name]
      ,[Buy-from Vendor Name 2]
      ,[Buy-from Address]
      ,[Buy-from Address 2]
      ,[Buy-from City]
      ,[Buy-from Contact]
      ,[Buy-from Post Code]
      ,[Buy-from County]
      ,[Buy-from Country_Region Code]
      ,[Document Date]
      ,[Payment Method Code]
      ,[No_ Series]
      ,[Posting No_ Series]
      ,[Dimension Set ID]
      ,[Buy-from Contact No_]
      ,[Document Receipt Date]
      ,[Registration No_]
      ,[Registration No_ 2]
      ,[VAT Date]
      ,[Attachment]
      ,[AttachName]
      ,[PageLink]
      ,[SendToMer]
      ,[SendToAcc]
      ,[SendToFinan]
      ,[Vendor Bank Account No_]
      ,[NetAmount]
      ,[Register Date]
      ,[Register Date_Time]
      ,[Registered By]
      ,[Document Type]
      ,[Zarejestrowany]
      ,[Exist Purchase Header]
      ,[Accepted]
      ,[Akcepted Mer By]
      ,[Akcepted Date Time]
      ,[Send to]
      ,[Financial Acceptance]
      ,[Payment Acceptance]
      ,[Fin_ Act_ By]
      ,[Pay_ Act_ By]
      ,[SendToAccept]
      ,[UserString]
      ,[CreatedBy]
      ,[Order No_]
      ,[GrossAmount]
      ,[Cash]
      ,[Vendor Bank Account Code]
    '''
    
    results = []
    for company_code, _ in COMPANIES_TUPLES:
        result = fetch_dict_data(
            company=company_code, 
            fields=fields, 
            table='Log Incoming Document$b64d2b42-739a-4647-b44a-fd892d64fff6', 
            condition='[Accepted] !=1'
        )
        if result:
            for doc in result:
                doc['company'] = company_code
            results.extend(result)
    
    return results

def fetch_comments(company: str, document_no: str) -> List[Dict[str, Any]]:
    """
    Pobiera komentarze dla danego dokumentu.
    
    Args:
        company: Nazwa firmy
        document_no: Numer dokumentu
        
    Returns:
        Lista komentarzy
    """
    conn = get_connection()
    if not conn:
        return []
    
    try:
        SQL_QUERY_1 = f'''
            SELECT 
            [dbo].[{company}$Comment Line$437dbf0e-84ff-417a-965d-ed2bb9650972].[No_]
            ,[dbo].[{company}$Comment Line$437dbf0e-84ff-417a-965d-ed2bb9650972].[Line No_]
            ,[dbo].[{company}$Comment Line$437dbf0e-84ff-417a-965d-ed2bb9650972].[Date]
            ,[dbo].[{company}$Comment Line$437dbf0e-84ff-417a-965d-ed2bb9650972].[Code]
            ,[dbo].[{company}$Comment Line$437dbf0e-84ff-417a-965d-ed2bb9650972].[Comment]
            FROM [dbo].[{company}$Comment Line$437dbf0e-84ff-417a-965d-ed2bb9650972]
            WHERE [dbo].[{company}$Comment Line$437dbf0e-84ff-417a-965d-ed2bb9650972].[No_] = \'{document_no}\'
        '''

        SQL_QUERY_2 = f'''
            SELECT 
            [dbo].[{company}$Comment Line$b64d2b42-739a-4647-b44a-fd892d64fff6].[Line No_]
            ,[dbo].[{company}$Comment Line$b64d2b42-739a-4647-b44a-fd892d64fff6].[Pozycja budżetowa]
            ,[dbo].[{company}$Comment Line$b64d2b42-739a-4647-b44a-fd892d64fff6].[Zadanie]
            ,[dbo].[{company}$Comment Line$b64d2b42-739a-4647-b44a-fd892d64fff6].[Account No_]
            ,[dbo].[{company}$Comment Line$b64d2b42-739a-4647-b44a-fd892d64fff6].[Amount]
            ,[dbo].[{company}$Comment Line$b64d2b42-739a-4647-b44a-fd892d64fff6].[Wymiar1]
            ,[dbo].[{company}$Comment Line$b64d2b42-739a-4647-b44a-fd892d64fff6].[Wymiar2]
            ,[dbo].[{company}$Comment Line$b64d2b42-739a-4647-b44a-fd892d64fff6].[Wymiar3]
            ,[dbo].[{company}$Comment Line$b64d2b42-739a-4647-b44a-fd892d64fff6].[Wymiar4]
            ,[dbo].[{company}$Comment Line$b64d2b42-739a-4647-b44a-fd892d64fff6].[Wymiar5]
            ,[dbo].[{company}$Comment Line$b64d2b42-739a-4647-b44a-fd892d64fff6].[Wymiar6]
            ,[dbo].[{company}$Comment Line$b64d2b42-739a-4647-b44a-fd892d64fff6].[Wymiar7]
            ,[dbo].[{company}$Comment Line$b64d2b42-739a-4647-b44a-fd892d64fff6].[Wymiar8]
            ,[dbo].[{company}$Comment Line$b64d2b42-739a-4647-b44a-fd892d64fff6].[Wymiar9]
            ,[dbo].[{company}$Comment Line$b64d2b42-739a-4647-b44a-fd892d64fff6].[Wymiar10]
            FROM [dbo].[{company}$Comment Line$b64d2b42-739a-4647-b44a-fd892d64fff6]
            WHERE [dbo].[{company}$Comment Line$b64d2b42-739a-4647-b44a-fd892d64fff6].[No_] = \'{document_no}\'
        '''

        cursor = conn.cursor()
        cursor.execute(SQL_QUERY_1)
        columns = [column[0] for column in cursor.description]
        results_1 = []
        data = cursor.fetchall()
        for row in data:
            results_1.append(dict(zip(columns, row)))
        
        cursor.execute(SQL_QUERY_2)
        columns = [column[0] for column in cursor.description]
        results_2 = []
        data = cursor.fetchall()
        for row in data:
            results_2.append(dict(zip(columns, row)))
        
        merged_results = []
        for item1 in results_1:
            for item2 in results_2:
                if item1['Line No_'] == item2['Line No_']:
                    merged_item = {**item1, **item2}
                    merged_results.append(merged_item)
        
        return merged_results
    except Exception as e:
        st.error(f"Błąd podczas pobierania komentarzy: {str(e)}")
        return []
    finally:
        conn.close()

def add_comment(comment: Comment, user: str) -> Dict[str, str]:
    """
    Dodaje komentarz do dokumentu.
    
    Args:
        comment: Obiekt komentarza
        user: Nazwa użytkownika
        
    Returns:
        Status operacji
    """
    conn = get_connection()
    if not conn:
        return {"status": "error", "message": "Brak połączenia z bazą danych"}
    
    try:
        SQL_QUERY = f'''
            Declare @LineNo int
            IF EXISTS (SELECT * FROM [dbo].[{comment.company}$Comment Line$437dbf0e-84ff-417a-965d-ed2bb9650972] WHERE No_ = \'{comment.document_no}\')
            BEGIN
                Set @LineNo = (Select max([Line No_])+1 from [dbo].[{comment.company}$Comment Line$437dbf0e-84ff-417a-965d-ed2bb9650972] where No_ =  \'{comment.document_no}\' )
            END
            ELSE
            BEGIN
                Set @LineNo = 10000
            END
            INSERT INTO [dbo].[{comment.company}$Comment Line$437dbf0e-84ff-417a-965d-ed2bb9650972] (
            [timestamp]
            ,[Table Name]
            ,[No_]
            ,[Line No_]
            ,[Date]
            ,[Code]
            ,[Comment]
            ,[$systemId]
            ,[$systemCreatedAt]
            ,[$systemCreatedBy]
            ,[$systemModifiedAt]
            ,[$systemModifiedBy]
            )
            VALUES (
            default
            ,0
            ,'{comment.document_no}'
            ,@LineNo
            ,Convert(Date,GETDATE())
            ,'ESV\\{user}'
            ,'{comment.comment}'
            ,default
            ,GETDATE()
            ,default
            ,GETDATE()
            ,default
            )
            
            Insert into [dbo].[{comment.company}$Comment Line$b64d2b42-739a-4647-b44a-fd892d64fff6]
            (
                [timestamp]
                ,[Table Name]
                ,[No_]
                ,[Line No_]
                ,[Table Name Extended]
                ,[Pozycja budżetowa]
                ,[Zadanie]
                ,[Account No_]
                ,[Amount]
                ,[Wymiar1]
                ,[Wymiar2]
                ,[Wymiar3]
                ,[Wymiar4]
                ,[Wymiar5]
                ,[Wymiar6]
                ,[Wymiar7]
                ,[Wymiar8]
                ,[Wymiar9]
                ,[Wymiar10]
                ,[DimSetId]
            )
            
            Values (
            default
            ,0
            ,\'{comment.document_no}\'
            ,@LineNo
            ,0
            ,\'{comment.nr_poz_budz}\'
            ,'{comment.zadanie_task or ""}'
            ,\'{comment.nr_konta}\'
            ,\'{comment.kwota_netto}\'
            ,\'{comment.dzialalnosc}\'
            ,\'{comment.rejon}\'
            ,\'{comment.zusl}\'
            ,\'{comment.zasoby}\'
            ,\'{comment.nr_poz_budz_inwest}\'
            ,\'{comment.zespol5}\'
            ,\'{comment.grupa_kapit}\'
            ,\'{comment.rodzaj_inwestycji}\'
            ,\'{comment.inform_kw}\'
            ,\'{comment.zadanie_task}\'
            ,0
            )
        '''
        
        cursor = conn.cursor()
        cursor.execute(SQL_QUERY)
        conn.commit()
        return {"status": "success"}
    except Exception as e:
        st.error(f"Błąd podczas dodawania komentarza: {str(e)}")
        return {"status": "error", "message": str(e)}
    finally:
        conn.close()

def update_comment(document_no: str, company: str, line_no: str, comment_data: Dict[str, str], user: str) -> Dict[str, str]:
    """
    Aktualizuje komentarz - wszystkie pola.
    
    Args:
        document_no: Numer dokumentu
        company: Nazwa firmy
        line_no: Numer linii komentarza
        comment_data: Słownik z danymi komentarza do aktualizacji
        user: Nazwa użytkownika
        
    Returns:
        Status operacji
    """
    conn = get_connection()
    if not conn:
        return {"status": "error", "message": "Brak połączenia z bazą danych"}
    
    try:
        company = company.upper()
        user = user.upper()
        
        # Przygotowanie wartości z escapowaniem apostrofów
        comment_text = comment_data.get('comment', '').replace("'", "''")
        amount = comment_data.get('amount', '')
        budget_pos = comment_data.get('budget_pos', '').replace("'", "''")
        account = comment_data.get('account', '').replace("'", "''")
        task = comment_data.get('task', '').replace("'", "''")
        dzialanosc = comment_data.get('dzialanosc', '').replace("'", "''")
        rejon = comment_data.get('rejon', '').replace("'", "''")
        zusl = comment_data.get('zusl', '').replace("'", "''")
        zasoby = comment_data.get('zasoby', '').replace("'", "''")
        nr_poz_budz_inwest = comment_data.get('nr_poz_budz_inwest', '').replace("'", "''")
        zespol5 = comment_data.get('zespol5', '').replace("'", "''")
        grupa_kapit = comment_data.get('grupa_kapit', '').replace("'", "''")
        rodzaj_inwest = comment_data.get('rodzaj_inwest', '').replace("'", "''")
        
        # Aktualizacja pierwszej tabeli (podstawowe informacje o komentarzu)
        SQL_QUERY_1 = f'''
            UPDATE [dbo].[{company}$Comment Line$437dbf0e-84ff-417a-965d-ed2bb9650972]
            SET [Comment] = '{comment_text}'
            ,[Date] = GETDATE()
            ,[Code] = 'ESV\\{user}'
            WHERE [No_] = '{document_no}' AND [Line No_] = {line_no}
        '''
        
        # Aktualizacja drugiej tabeli (dodatkowe pola)
        SQL_QUERY_2 = f'''
            UPDATE [dbo].[{company}$Comment Line$b64d2b42-739a-4647-b44a-fd892d64fff6]
            SET [Amount] = '{amount}'
            ,[Pozycja budżetowa] = '{budget_pos}'
            ,[Account No_] = '{account}'
            ,[Wymiar1] = '{dzialanosc}'
            ,[Wymiar2] = '{rejon}'
            ,[Wymiar3] = '{zusl}'
            ,[Wymiar4] = '{zasoby}'
            ,[Wymiar5] = '{nr_poz_budz_inwest}'
            ,[Wymiar6] = '{zespol5}'
            ,[Wymiar7] = '{grupa_kapit}'
            ,[Wymiar8] = '{rodzaj_inwest}'
            ,[Wymiar9] = '{comment_data.get("inform_kw", "").replace("'", "''") if "inform_kw" in comment_data else ""}'
            ,[Wymiar10] = '{task}'
            ,[Zadanie] = '{task}'
            WHERE [No_] = '{document_no}' AND [Line No_] = {line_no}
        '''
        
        cursor = conn.cursor()
        # Wykonanie obu zapytań
        cursor.execute(SQL_QUERY_1)
        cursor.execute(SQL_QUERY_2)
        conn.commit()
        return {"status": "success"}
    except Exception as e:
        st.error(f"Błąd podczas aktualizacji komentarza: {str(e)}")
        return {"status": "error", "message": str(e)}
    finally:
        conn.close()

def delete_comment(document_no: str, company: str, line_no: int) -> Dict[str, str]:
    """
    Usuwa komentarz.
    
    Args:
        document_no: Numer dokumentu
        company: Nazwa firmy
        line_no: Numer linii komentarza
        
    Returns:
        Status operacji
    """
    conn = get_connection()
    if not conn:
        return {"status": "error", "message": "Brak połączenia z bazą danych"}
    
    try:
        SQL_QUERY = f'''
            DELETE FROM [dbo].[{company}$Comment Line$437dbf0e-84ff-417a-965d-ed2bb9650972]
            WHERE [No_] = '{document_no}' AND [Line No_] = {line_no}
            Delete from [dbo].[{company}$Comment Line$b64d2b42-739a-4647-b44a-fd892d64fff6]
            WHERE [No_] = '{document_no}' AND [Line No_] = {line_no}
        '''
        cursor = conn.cursor()
        cursor.execute(SQL_QUERY)
        conn.commit()
        return {"status": "success"}
    except Exception as e:
        st.error(f"Błąd podczas usuwania komentarza: {str(e)}")
        return {"status": "error", "message": str(e)}
    finally:
        conn.close()

def accept_document(document_no: str, company: str, user: str) -> Dict[str, str]:
    """
    Akceptuje dokument.
    
    Args:
        document_no: Numer dokumentu
        company: Nazwa firmy
        user: Nazwa użytkownika
        
    Returns:
        Status operacji
    """
    conn = get_connection()
    if not conn:
        return {"status": "error", "message": "Brak połączenia z bazą danych"}
    
    try:
        company = company.upper()
        user = user.upper()
        SQL_QUERY = f'''
            UPDATE [dbo].[{company}$Log Incoming Document$b64d2b42-739a-4647-b44a-fd892d64fff6]
            SET [Accepted] = 1
            ,[Akcepted Mer By] = \'ESV\\{user}\'
            ,[Akcepted Date Time] = GETDATE()
            WHERE [No_] = '{document_no}'
        '''
        cursor = conn.cursor()
        cursor.execute(SQL_QUERY)
        conn.commit()
        return {"status": "success"}
    except Exception as e:
        st.error(f"Błąd podczas akceptacji dokumentu: {str(e)}")
        return {"status": "error", "message": str(e)}
    finally:
        conn.close()

def get_invoice_details(invoice_id: str, company: str) -> Dict[str, Any]:
    """
    Pobiera szczegóły faktury.
    
    Args:
        invoice_id: ID faktury
        company: Nazwa firmy
        
    Returns:
        Szczegóły faktury
    """
    fields = '''[No_]
      ,[Buy-from Vendor No_]
      ,[Posting Date]
      ,[Allert]
      ,[Payment Terms Code]
      ,[Due Date]
      ,[Shortcut Dimension 1 Code]
      ,[Shortcut Dimension 2 Code]
      ,[Currency Code]
      ,[Vendor Order No_]
      ,[Vendor Shipment No_]
      ,[Vendor Invoice No_]
      ,[Vat Registration No_]
      ,[Vat Country_Region Code]
      ,[Buy-from Vendor Name]
      ,[Buy-from Vendor Name 2]
      ,[Buy-from Address]
      ,[Buy-from Address 2]
      ,[Buy-from City]
      ,[Buy-from Contact]
      ,[Buy-from Post Code]
      ,[Buy-from County]
      ,[Buy-from Country_Region Code]
      ,[Document Date]
      ,[Payment Method Code]
      ,[No_ Series]
      ,[Posting No_ Series]
      ,[Dimension Set ID]
      ,[Buy-from Contact No_]
      ,[Document Receipt Date]
      ,[Registration No_]
      ,[Registration No_ 2]
      ,[VAT Date]
      ,[Attachment]
      ,[AttachName]
      ,[PageLink]
      ,[SendToMer]
      ,[SendToAcc]
      ,[SendToFinan]
      ,[Vendor Bank Account No_]
      ,[NetAmount]
      ,[Register Date]
      ,[Register Date_Time]
      ,[Registered By]
      ,[Document Type]
      ,[Zarejestrowany]
      ,[Exist Purchase Header]
      ,[Accepted]
      ,[Akcepted Mer By]
      ,[Akcepted Date Time]
      ,[Send to]
      ,[Financial Acceptance]
      ,[Payment Acceptance]
      ,[Fin_ Act_ By]
      ,[Pay_ Act_ By]
      ,[SendToAccept]
      ,[UserString]
      ,[CreatedBy]
      ,[Order No_]
      ,[GrossAmount]
      ,[Cash]
      ,[Vendor Bank Account Code]
    '''
    
    result = fetch_dict_data(
        company=company, 
        fields=fields, 
        table='Log Incoming Document$b64d2b42-739a-4647-b44a-fd892d64fff6', 
        condition=f'[No_] = \'{invoice_id}\''
    )
    
    if result:
        return result[0]
    return {}

def get_attachment(company: str, document_no: str):
    """
    Pobiera załączniki PDF dla danego dokumentu.
    
    Args:
        company: Nazwa firmy
        document_no: Numer dokumentu
        
    Returns:
        Lista słowników z plikami PDF: [{"file_name": ..., "file_content": ...}]
    """
    fields = '[Attachment],[FileName]'
    company = company.upper()
    results = fetch_dict_data(
        company=company, 
        fields=fields, 
        table='DocumentAttachmentOD$b64d2b42-739a-4647-b44a-fd892d64fff6', 
        condition=f'[Document No_] = \'{document_no}\''
    )
    
    attachments = []
    for result in results:
        file_name = result["FileName"]
        file_content = result["Attachment"]
        file_content_decompressed = zlib.decompress(file_content[4:], -zlib.MAX_WBITS)
        
        # Sprawdź czy plik to PDF (na podstawie rozszerzenia lub nagłówka PDF)
        if file_name.lower().endswith('.pdf') or file_content_decompressed[:4] == b'%PDF':
            attachments.append({
                "file_name": file_name,
                "file_content": file_content_decompressed
            })
    
    return attachments

def get_accounts(company: str) -> List[Dict[str, Any]]:
    """
    Pobiera listę kont księgowych.
    
    Args:
        company: Nazwa firmy
        
    Returns:
        Lista kont księgowych
    """
    company = company.upper()
    results = fetch_dict_data(
        company=company, 
        fields='[No_],[Name],[Search Name]', 
        table='G_L Account$437dbf0e-84ff-417a-965d-ed2bb9650972'
    )
    return results

def get_dimensions(company: str, dimension_code: str = None) -> List[Dict[str, Any]]:
    """
    Pobiera listę wymiarów.
    
    Args:
        company: Nazwa firmy
        dimension_code: Kod wymiaru (opcjonalnie)
        
    Returns:
        Lista wymiarów
    """
    company = company.upper()
    
    # Specjalne traktowanie dla wymiaru Z.USL
    if dimension_code == "Z.USL":
        try:
            # Dla Z.USL używamy specjalnego zapytania
            SQL_QUERY = f"""
                SELECT 
                    'Z.USL' AS [Dimension Code],
                    [Code],
                    [Name],
                    [Dimension Value Type] AS [Dimension_Value_Type],
                    [Totaling],
                    [Blocked]
                FROM [dbo].[{company}$Dimension Value$437dbf0e-84ff-417a-965d-ed2bb9650972]
                WHERE [Dimension Code] = 'Z.USL' AND [Blocked] != 1
            """
            
            conn = get_connection()
            if not conn:
                return []
                
            cursor = conn.cursor()
            cursor.execute(SQL_QUERY)
            columns = [column[0] for column in cursor.description]
            results = []
            data = cursor.fetchall()
            for row in data:
                results.append(dict(zip(columns, row)))
            cursor.close()
            conn.close()
            
            if not results:
                # Jeśli nie znaleziono wyników, spróbuj alternatywnych nazw
                alternative_codes = ["Z_USL", "ZUSL", "Z USL"]
                for alt_code in alternative_codes:
                    condition = f"[Blocked] != 1 AND [Dimension Code] = '{alt_code}'"
                    alt_results = fetch_dict_data(
                        company=company, 
                        fields='[Dimension Code],[Code],[Name],[Dimension Value Type] AS [Dimension_Value_Type],[Totaling],[Blocked]', 
                        table='Dimension Value$437dbf0e-84ff-417a-965d-ed2bb9650972', 
                        condition=condition
                    )
                    if alt_results:
                        # Zmień kod wymiaru na Z.USL dla spójności
                        for r in alt_results:
                            r['Dimension Code'] = 'Z.USL'
                        return alt_results
            
            return results
        except Exception as e:
            st.error(f"Błąd podczas pobierania wymiarów Z.USL: {str(e)}")
            return []

    elif dimension_code =="NR POZ.BUDŻ.INWEST.":
        try:
            # Dla NR POZ.BUDŻ.INWEST. używamy specjalnego zapytania
            SQL_QUERY = f"""
                SELECT 
                    'NR POZ.BUDŻ.INWEST.' AS [Dimension Code],
                    [Code],
                    [Name],
                    [Dimension Value Type] AS [Dimension_Value_Type],
                    [Totaling],
                    [Blocked]
                FROM [dbo].[{company}$Dimension Value$437dbf0e-84ff-417a-965d-ed2bb9650972]
                WHERE [Dimension Code] LIKE '%NR POZ.BUD%' AND [Blocked] != 1
            """
            
            conn = get_connection()
            if not conn:
                return []
                
            cursor = conn.cursor()
            cursor.execute(SQL_QUERY)
            columns = [column[0] for column in cursor.description]
            results = []
            data = cursor.fetchall()
            for row in data:
                results.append(dict(zip(columns, row)))
            cursor.close()
            conn.close()
            
            
            return results
        except Exception as e:
            st.error(f"Błąd podczas pobierania wymiarów NR POZ.BUDŻ.INWEST.: {str(e)}")
            return []
        
    
    # Specjalne traktowanie dla wymiaru 1REJON
    elif dimension_code == "1REJON":
        try:
            # Dla 1REJON używamy specjalnego zapytania
            SQL_QUERY = f"""
                SELECT 
                    '1REJON' AS [Dimension Code],
                    [Code],
                    [Name],
                    [Dimension Value Type] AS [Dimension_Value_Type],
                    [Totaling],
                    [Blocked]
                FROM [dbo].[{company}$Dimension Value$437dbf0e-84ff-417a-965d-ed2bb9650972]
                WHERE [Dimension Code] = '1REJON' AND [Blocked] != 1
            """
            
            conn = get_connection()
            if not conn:
                return []
                
            cursor = conn.cursor()
            cursor.execute(SQL_QUERY)
            columns = [column[0] for column in cursor.description]
            results = []
            data = cursor.fetchall()
            for row in data:
                results.append(dict(zip(columns, row)))
            cursor.close()
            conn.close()
            
            if not results:
                # Jeśli nie znaleziono wyników, spróbuj alternatywnych nazw
                alternative_codes = ["1_REJON", "1 REJON", "REJON1", "REJON_1", "REJON 1"]
                for alt_code in alternative_codes:
                    condition = f"[Blocked] != 1 AND [Dimension Code] = '{alt_code}'"
                    alt_results = fetch_dict_data(
                        company=company, 
                        fields='[Dimension Code],[Code],[Name],[Dimension Value Type] AS [Dimension_Value_Type],[Totaling],[Blocked]', 
                        table='Dimension Value$437dbf0e-84ff-417a-965d-ed2bb9650972', 
                        condition=condition
                    )
                    if alt_results:
                        # Zmień kod wymiaru na 1REJON dla spójności
                        for r in alt_results:
                            r['Dimension Code'] = '1REJON'
                        return alt_results
            
            return results
        except Exception as e:
            st.error(f"Błąd podczas pobierania wymiarów 1REJON: {str(e)}")
            return []
    
    # Specjalne traktowanie dla wymiaru inwestycyjne
    elif dimension_code == "inwestycyjne":
        try:
            # Dla inwestycyjne używamy specjalnego zapytania
            SQL_QUERY = f"""
                SELECT 
                    'inwestycyjne' AS [Dimension Code],
                    [Code],
                    [Name],
                    [Dimension Value Type] AS [Dimension_Value_Type],
                    [Totaling],
                    [Blocked]
                FROM [dbo].[{company}$Dimension Value$437dbf0e-84ff-417a-965d-ed2bb9650972]
                WHERE [Dimension Code] = 'inwestycyjne' AND [Blocked] != 1
            """
            
            conn = get_connection()
            if not conn:
                return []
                
            cursor = conn.cursor()
            cursor.execute(SQL_QUERY)
            columns = [column[0] for column in cursor.description]
            results = []
            data = cursor.fetchall()
            for row in data:
                results.append(dict(zip(columns, row)))
            cursor.close()
            conn.close()
            
            if not results:
                # Jeśli nie znaleziono wyników, spróbuj alternatywnych nazw
                alternative_codes = ["INWESTYCYJNE", "Inwestycyjne", "INW", "INWEST", "INW_", "INWESTYCJE"]
                for alt_code in alternative_codes:
                    condition = f"[Blocked] != 1 AND [Dimension Code] = '{alt_code}'"
                    alt_results = fetch_dict_data(
                        company=company, 
                        fields='[Dimension Code],[Code],[Name],[Dimension Value Type] AS [Dimension_Value_Type],[Totaling],[Blocked]', 
                        table='Dimension Value$437dbf0e-84ff-417a-965d-ed2bb9650972', 
                        condition=condition
                    )
                    if alt_results:
                        # Zmień kod wymiaru na inwestycyjne dla spójności
                        for r in alt_results:
                            r['Dimension Code'] = 'inwestycyjne'
                        return alt_results
            
            return results
        except Exception as e:
            st.error(f"Błąd podczas pobierania wymiarów inwestycyjne: {str(e)}")
            return []
    
    # Standardowe zapytanie dla innych wymiarów
    condition = '[Blocked] != 1'
    if dimension_code:
        condition += f" AND [Dimension Code] = '{dimension_code}'"
    
    try:
        results = fetch_dict_data(
            company=company, 
            fields='[Dimension Code],[Code],[Name],[Dimension Value Type] AS [Dimension_Value_Type],[Totaling],[Blocked]', 
            table='Dimension Value$437dbf0e-84ff-417a-965d-ed2bb9650972', 
            condition=condition
        )
        return results
    except Exception as e:
        st.error(f"Błąd podczas pobierania wymiarów: {str(e)}")
        return []

def get_job_tasks(company: str, zusl_code: str) -> List[Dict[str, Any]]:
    """
    Pobiera listę zadań dla danego kodu ZUSL.
    
    Args:
        company: Nazwa firmy
        zusl_code: Kod ZUSL
        
    Returns:
        Lista zadań
    """
    company = company.upper()
    condition = f'[Job No_] = \'{zusl_code}\''
    fields = '''
        [Job Task No_],
        [Description]
        '''
    results = fetch_dict_data(
        company=company, 
        fields=fields, 
        table='Job Task$437dbf0e-84ff-417a-965d-ed2bb9650972', 
        condition=condition
    )
    return results

def get_budget_positions(company: str) -> List[Dict[str, Any]]:
    """
    Pobiera listę pozycji budżetowych.
    
    Args:
        company: Nazwa firmy
        
    Returns:
        Lista pozycji budżetowych
    """
    company = company.upper()
    results = fetch_dict_data(
        company=company, 
        fields='[Code],[Account No_]', 
        table='DictionaryIncomDoc2$b64d2b42-739a-4647-b44a-fd892d64fff6', 
        condition="[Account No_] <> ''"
    )
    return results 