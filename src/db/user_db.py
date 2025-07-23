import sqlite3
import os
import hashlib
import secrets
from typing import Dict, List, Optional, Tuple

# Ścieżka do bazy danych SQLite
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'users.db')

# Upewnij się, że katalog data istnieje
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

def get_db_connection():
    """Tworzy i zwraca połączenie do bazy danych SQLite."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Inicjalizuje bazę danych, tworząc tabelę użytkowników jeśli nie istnieje."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Tworzenie tabeli użytkowników
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        login TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        salt TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        is_admin BOOLEAN NOT NULL DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # Sprawdzenie, czy istnieje użytkownik admin
    cursor.execute("SELECT COUNT(*) FROM users WHERE login = 'admin'")
    if cursor.fetchone()[0] == 0:
        # Tworzenie domyślnego użytkownika admin
        salt = secrets.token_hex(16)
        password_hash = hashlib.sha256(f"admin{salt}".encode()).hexdigest()
        cursor.execute(
            "INSERT INTO users (login, password_hash, salt, email, is_admin) VALUES (?, ?, ?, ?, ?)",
            ("admin", password_hash, salt, "admin@example.com", True)
        )
    
    conn.commit()
    conn.close()

def hash_password(password: str, salt: str = None) -> Tuple[str, str]:
    """
    Haszuje hasło z użyciem soli.
    
    Args:
        password: Hasło do zahaszowania
        salt: Sól do użycia (jeśli None, generuje nową)
        
    Returns:
        Tuple zawierający (hash_hasła, sól)
    """
    if salt is None:
        salt = secrets.token_hex(16)
    
    password_hash = hashlib.sha256(f"{password}{salt}".encode()).hexdigest()
    return password_hash, salt

def verify_user(login: str, password: str) -> Optional[Dict]:
    """
    Weryfikuje dane logowania użytkownika.
    
    Args:
        login: Login użytkownika
        password: Hasło użytkownika
        
    Returns:
        Słownik z danymi użytkownika lub None, jeśli weryfikacja nie powiodła się
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM users WHERE login = ?", (login,))
    user = cursor.fetchone()
    conn.close()
    
    if user is None:
        return None
    
    password_hash, salt = hash_password(password, user['salt'])
    
    if password_hash == user['password_hash']:
        return dict(user)
    
    return None

def add_user(login: str, password: str, email: str, is_admin: bool = False) -> bool:
    """
    Dodaje nowego użytkownika do bazy danych.
    
    Args:
        login: Login użytkownika
        password: Hasło użytkownika
        email: Adres email użytkownika
        is_admin: Czy użytkownik jest administratorem
        
    Returns:
        True jeśli dodanie powiodło się, False w przeciwnym razie
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Sprawdzenie, czy użytkownik już istnieje
        cursor.execute("SELECT COUNT(*) FROM users WHERE login = ? OR email = ?", (login, email))
        if cursor.fetchone()[0] > 0:
            conn.close()
            return False
        
        # Haszowanie hasła
        password_hash, salt = hash_password(password)
        
        # Dodanie użytkownika
        cursor.execute(
            "INSERT INTO users (login, password_hash, salt, email, is_admin) VALUES (?, ?, ?, ?, ?)",
            (login, password_hash, salt, email, is_admin)
        )
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Błąd podczas dodawania użytkownika: {str(e)}")
        return False

def get_all_users() -> List[Dict]:
    """
    Pobiera listę wszystkich użytkowników.
    
    Returns:
        Lista słowników z danymi użytkowników
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT id, login, email, is_admin, created_at FROM users")
    users = [dict(user) for user in cursor.fetchall()]
    
    conn.close()
    return users

def delete_user(user_id: int) -> bool:
    """
    Usuwa użytkownika o podanym ID.
    
    Args:
        user_id: ID użytkownika do usunięcia
        
    Returns:
        True jeśli usunięcie powiodło się, False w przeciwnym razie
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Błąd podczas usuwania użytkownika: {str(e)}")
        return False

def update_user(user_id: int, email: str = None, is_admin: bool = None, password: str = None) -> bool:
    """
    Aktualizuje dane użytkownika.
    
    Args:
        user_id: ID użytkownika do aktualizacji
        email: Nowy adres email (opcjonalnie)
        is_admin: Nowa wartość flagi administratora (opcjonalnie)
        password: Nowe hasło (opcjonalnie)
        
    Returns:
        True jeśli aktualizacja powiodła się, False w przeciwnym razie
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        updates = []
        params = []
        
        if email is not None:
            updates.append("email = ?")
            params.append(email)
        
        if is_admin is not None:
            updates.append("is_admin = ?")
            params.append(is_admin)
        
        if password is not None:
            password_hash, salt = hash_password(password)
            updates.append("password_hash = ?")
            params.append(password_hash)
            updates.append("salt = ?")
            params.append(salt)
        
        if not updates:
            conn.close()
            return False
        
        query = f"UPDATE users SET {', '.join(updates)} WHERE id = ?"
        params.append(user_id)
        
        cursor.execute(query, params)
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Błąd podczas aktualizacji użytkownika: {str(e)}")
        return False

# Inicjalizacja bazy danych przy importowaniu modułu
init_db() 