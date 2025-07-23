from dataclasses import dataclass
from typing import Optional, Dict, Any
from datetime import datetime

@dataclass
class Comment:
    """
    Model reprezentujący komentarz do faktury.
    """
    document_no: str
    company: str
    comment: str
    nr_poz_budz: str = ""
    nr_konta: str = ""
    kwota_netto: str = ""
    dzialalnosc: str = ""
    rejon: str = ""
    zusl: Optional[str] = None
    zasoby: Optional[str] = None
    nr_poz_budz_inwest: Optional[str] = None
    zespol5: Optional[str] = None
    grupa_kapit: Optional[str] = None
    rodzaj_inwestycji: Optional[str] = None
    inform_kw: Optional[str] = None
    zadanie_task: Optional[str] = None
    nowy_wymiar: Optional[str] = None
    created_at: Optional[datetime] = None
    id: Optional[str] = None
    
    def __post_init__(self):
        """
        Inicjalizuje pola, które nie zostały podane przy tworzeniu obiektu.
        """
        if self.created_at is None:
            self.created_at = datetime.now()
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Comment':
        """
        Tworzy obiekt Comment z słownika danych.
        
        Args:
            data: Słownik z danymi komentarza
            
        Returns:
            Obiekt Comment
        """
        return cls(
            document_no=data.get('No_', ''),
            company=data.get('company', ''),
            comment=data.get('Comment', ''),
            nr_poz_budz=data.get('Pozycja budżetowa', ''),
            nr_konta=data.get('Account No_', ''),
            kwota_netto=data.get('Amount', ''),
            dzialalnosc=data.get('Wymiar1', ''),
            rejon=data.get('Wymiar2', ''),
            zusl=data.get('Wymiar3', ''),
            zasoby=data.get('Wymiar4', ''),
            nr_poz_budz_inwest=data.get('Wymiar5', ''),
            zespol5=data.get('Wymiar6', ''),
            grupa_kapit=data.get('Wymiar7', ''),
            rodzaj_inwestycji=data.get('Wymiar8', ''),
            inform_kw=data.get('Wymiar9', ''),
            zadanie_task=data.get('Wymiar10', ''),
            nowy_wymiar=data.get('Wymiar11', ''),
            created_at=data.get('Date', datetime.now()),
            id=data.get('Line No_', None)
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Konwertuje obiekt Comment na słownik.
        
        Returns:
            Słownik z danymi komentarza
        """
        return {
            'document_no': self.document_no,
            'company': self.company,
            'comment': self.comment,
            'nr_poz_budz': self.nr_poz_budz,
            'nr_konta': self.nr_konta,
            'kwota_netto': self.kwota_netto,
            'dzialalnosc': self.dzialalnosc,
            'rejon': self.rejon,
            'zusl': self.zusl,
            'zasoby': self.zasoby,
            'nr_poz_budz_inwest': self.nr_poz_budz_inwest,
            'zespol5': self.zespol5,
            'grupa_kapit': self.grupa_kapit,
            'rodzaj_inwestycji': self.rodzaj_inwestycji,
            'inform_kw': self.inform_kw,
            'zadanie_task': self.zadanie_task,
            'nowy_wymiar': self.nowy_wymiar
        }
    
    def to_memory_dict(self) -> Dict[str, Any]:
        """
        Konwertuje obiekt Comment na słownik do przechowywania w pamięci.
        
        Returns:
            Słownik z danymi komentarza
        """
        # Format dla pamięci
        return {
            'id': self.id,
            'document_no': self.document_no,
            'company': self.company,
            'comment': self.comment,
            'nr_poz_budz': self.nr_poz_budz,
            'nr_konta': self.nr_konta,
            'kwota_netto': self.kwota_netto,
            'dzialalnosc': self.dzialalnosc,
            'rejon': self.rejon,
            'zusl': self.zusl,
            'zasoby': self.zasoby,
            'nr_poz_budz_inwest': self.nr_poz_budz_inwest,
            'zespol5': self.zespol5,
            'grupa_kapit': self.grupa_kapit,
            'rodzaj_inwestycji': self.rodzaj_inwestycji,
            'inform_kw': self.inform_kw,
            'zadanie_task': self.zadanie_task,
            'nowy_wymiar': self.nowy_wymiar,
            'created_at': self.created_at.isoformat() if self.created_at else datetime.now().isoformat()
        } 