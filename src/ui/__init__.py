"""
Inicjalizacja pakietu UI
"""
from src.ui.components import (
    setup_page,
    info_box,
    warning_box,
    error_box,
    success_box,
    display_footer
)
from src.ui.components.invoice import (
    display_invoice_details,
    display_invoice_form,
    display_invoice_list,
    display_all_pending_invoices
)
from src.ui.components.user import display_login_form, display_user_management
from src.ui.components.dictionary import display_dictionaries

__all__ = [
    'setup_page',
    'info_box',
    'warning_box',
    'error_box',
    'success_box',
    'display_footer',
    'display_invoice_details',
    'display_invoice_form',
    'display_invoice_list',
    'display_login_form',
    'display_user_management',
    'display_all_pending_invoices',
    'display_dictionaries'
] 