from dataclasses import dataclass
from typing import Optional, Dict, Any
from datetime import datetime

@dataclass
class Approval:
    """
    Model reprezentujący zatwierdzenie faktury.
    """
    invoice_id: str
    user_id: str
    approval_date: datetime
    status: str
    comment: Optional[str] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Approval':
        """
        Tworzy obiekt Approval z słownika danych.
        
        Args:
            data: Słownik z danymi zatwierdzenia
            
        Returns:
            Obiekt Approval
        """
        return cls(
            invoice_id=data.get('invoice_id', ''),
            user_id=data.get('user_id', ''),
            approval_date=data.get('approval_date', datetime.now()),
            status=data.get('status', '0'),
            comment=data.get('comment', None)
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Konwertuje obiekt Approval na słownik.
        
        Returns:
            Słownik z danymi zatwierdzenia
        """
        return {
            'invoice_id': self.invoice_id,
            'user_id': self.user_id,
            'approval_date': self.approval_date,
            'status': self.status,
            'comment': self.comment
        } 