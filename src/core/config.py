"""
Moduł konfiguracyjny aplikacji ESV Toolbox
"""
import os
from dotenv import load_dotenv

# Ładowanie zmiennych środowiskowych z pliku .env
load_dotenv()

# Konfiguracja aplikacji
CONFIG = {
    "VERSION": "1.0.0",
    "APP_NAME": "ESV Toolbox",
    "DEBUG": os.getenv("DEBUG", "False").lower() in ("true", "1", "t"),
    "DATABASE_PATH": os.getenv("DATABASE_PATH", "data/users.db"),
    "LOG_LEVEL": os.getenv("LOG_LEVEL", "INFO"),
    "TIMEZONE": os.getenv("TZ", "Europe/Warsaw"),
    "MSSQL_SERVER": os.getenv("MSSQL_SERVER", "localhost"),
    "MSSQL_PORT": os.getenv("MSSQL_PORT", "1434"),
    "MSSQL_DATABASE": os.getenv("MSSQL_DATABASE", "master"),
    "MSSQL_USERNAME": os.getenv("MSSQL_USERNAME", "sa"),
    "MSSQL_PASSWORD": os.getenv("MSSQL_PASSWORD", ""),
}

def get_config():
    """
    Zwraca konfigurację aplikacji
    
    Returns:
        dict: Konfiguracja aplikacji
    """
    return CONFIG

def get_config_value(key, default=None):
    """
    Zwraca wartość konfiguracyjną dla podanego klucza
    
    Args:
        key (str): Klucz konfiguracyjny
        default: Wartość domyślna, jeśli klucz nie istnieje
        
    Returns:
        Wartość konfiguracyjna
    """
    return CONFIG.get(key, default) 