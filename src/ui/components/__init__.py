"""
Pakiet zawierający komponenty UI aplikacji.
"""
from .page import setup_page
from .boxes import (
    success_box,
    info_box,
    warning_box,
    error_box,
    display_footer
)

__all__ = [
    'setup_page',
    'success_box',
    'info_box',
    'warning_box',
    'error_box',
    'display_footer'
] 