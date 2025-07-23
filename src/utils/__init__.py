from .constants import INV_STATUS, COMPANIES as COMPANIES_TUPLES

# Konwersja listy krotek na listę kodów firm
COMPANIES = [company_code for company_code, _ in COMPANIES_TUPLES]

__all__ = ['INV_STATUS', 'COMPANIES', 'session_manager']

# Plik inicjalizacyjny dla pakietu utils 