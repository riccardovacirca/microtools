from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


class StatoContatto(str, Enum):
    """Stati possibili di un contatto"""
    ATTIVO = "attivo"
    INATTIVO = "inattivo"
    PROSPECT = "prospect"
    CLIENTE = "cliente"
    LEAD = "lead"
    ARCHIVIATO = "archiviato"


class ContattoBase(BaseModel):
    """Base model per i contatti"""
    nome: str = Field(..., min_length=1, max_length=100)
    cognome: str = Field(..., min_length=1, max_length=100)
    email: Optional[EmailStr] = None
    telefono: Optional[str] = Field(None, max_length=50)
    cellulare: Optional[str] = Field(None, max_length=50)
    azienda: Optional[str] = Field(None, max_length=200)
    ruolo: Optional[str] = Field(None, max_length=100)
    indirizzo: Optional[str] = Field(None, max_length=500)
    citta: Optional[str] = Field(None, max_length=100)
    provincia: Optional[str] = Field(None, max_length=2)
    cap: Optional[str] = Field(None, max_length=10)
    paese: Optional[str] = Field(None, max_length=100, description="Default: Italia")
    stato: StatoContatto = Field(default=StatoContatto.PROSPECT)
    consenso_privacy: bool = Field(default=False)
    consenso_marketing: bool = Field(default=False)
    note: Optional[str] = None


class ContattoCreate(ContattoBase):
    """Model per la creazione di un nuovo contatto"""
    liste_ids: Optional[List[int]] = Field(default_factory=list, description="IDs delle liste a cui appartiene")


class ContattoUpdate(BaseModel):
    """Model per l'aggiornamento di un contatto (tutti i campi opzionali)"""
    nome: Optional[str] = Field(None, min_length=1, max_length=100)
    cognome: Optional[str] = Field(None, min_length=1, max_length=100)
    email: Optional[EmailStr] = None
    telefono: Optional[str] = Field(None, max_length=50)
    cellulare: Optional[str] = Field(None, max_length=50)
    azienda: Optional[str] = Field(None, max_length=200)
    ruolo: Optional[str] = Field(None, max_length=100)
    indirizzo: Optional[str] = Field(None, max_length=500)
    citta: Optional[str] = Field(None, max_length=100)
    provincia: Optional[str] = Field(None, max_length=2)
    cap: Optional[str] = Field(None, max_length=10)
    paese: Optional[str] = Field(None, max_length=100)
    stato: Optional[StatoContatto] = None
    consenso_privacy: Optional[bool] = None
    consenso_marketing: Optional[bool] = None
    note: Optional[str] = None
    liste_ids: Optional[List[int]] = None


class ContattoResponse(ContattoBase):
    """Model per la risposta con i dati del contatto"""
    id: int
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None
    liste: Optional[List['ListaContattiResponse']] = Field(default_factory=list)

    class Config:
        from_attributes = True


class ContattoList(BaseModel):
    """Model per la lista paginata di contatti"""
    total: int
    page: int
    page_size: int
    contatti: List[ContattoResponse]


class ListaContattiBase(BaseModel):
    """Base model per le liste di contatti"""
    nome: str = Field(..., min_length=1, max_length=100)
    descrizione: Optional[str] = None


class ListaContattiCreate(ListaContattiBase):
    """Model per la creazione di una nuova lista"""
    pass


class ListaContattiUpdate(BaseModel):
    """Model per l'aggiornamento di una lista"""
    nome: Optional[str] = Field(None, min_length=1, max_length=100)
    descrizione: Optional[str] = None


class ListaContattiResponse(ListaContattiBase):
    """Model per la risposta con i dati della lista"""
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class DeleteResult(BaseModel):
    """Output model for delete operations"""
    deleted: bool = Field(..., description="Deletion success flag")


class RestoreResult(BaseModel):
    """Output model for restore operations"""
    restored: bool = Field(..., description="Restore success flag")


class ListeResult(BaseModel):
    """Output model for get all liste operation"""
    liste: List[ListaContattiResponse] = Field(..., description="List of all contact lists")


# Update forward references
ContattoResponse.model_rebuild()
