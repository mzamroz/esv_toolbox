from dataclasses import dataclass
from typing import Dict, Any
from datetime import datetime

@dataclass
class Invoice:
    """
    Model reprezentujący fakturę.
    """
    id: str
    vendor_no: str
    vendor_name: str
    posting_date: datetime
    due_date: datetime
    document_date: datetime
    currency_code: str
    vendor_invoice_no: str
    amount: float
    status: str
    company: str
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Invoice':
        """
        Tworzy obiekt Invoice z słownika danych.
        
        Args:
            data: Słownik z danymi faktury
            
        Returns:
            Obiekt Invoice
        """
        return cls(
            id=data.get('No_', ''),
            vendor_no=data.get('Buy-from Vendor No_', ''),
            vendor_name=data.get('Buy-from Vendor Name', ''),
            posting_date=data.get('Posting Date', datetime.now()),
            due_date=data.get('Due Date', datetime.now()),
            document_date=data.get('Document Date', datetime.now()),
            currency_code=data.get('Currency Code', 'PLN'),
            vendor_invoice_no=data.get('Vendor Invoice No_', ''),
            amount=0.0,  # To pole należałoby uzupełnić na podstawie linii faktury
            status=data.get('Status', '0'),
            company=data.get('Company', 'ESV_WZORCOWA')
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Konwertuje obiekt Invoice na słownik.
        
        Returns:
            Słownik z danymi faktury
        """
        return {
            'No_': self.id,
            'Buy-from Vendor No_': self.vendor_no,
            'Buy-from Vendor Name': self.vendor_name,
            'Posting Date': self.posting_date,
            'Due Date': self.due_date,
            'Document Date': self.document_date,
            'Currency Code': self.currency_code,
            'Vendor Invoice No_': self.vendor_invoice_no,
            'Amount': self.amount,
            'Status': self.status,
            'Company': self.company
        } 