"""
Modulo CRM - Gestione Contatti

Questo modulo fornisce funzionalità complete per la gestione dei contatti in un CRM:
- CRUD completo dei contatti
- Gestione liste di contatti
- Soft delete e hard delete
- Ricerca contatti
- Stati e consensi privacy/marketing
"""

from .routes import router

__all__ = ["router"]
