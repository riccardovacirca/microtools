"""Repository functions for contatti management.

This module implements database operations for contacts using procedural
helper functions following the DSL pattern.
"""
from typing import List
from ...common.db import db_cursor, db_transaction
from ..models.contatto_models import ContattoCreate, ContattoUpdate


def repository_create_contatto(contatto: ContattoCreate) -> int:
    """Create a new contatto in database.

    Args:
        contatto: Contact data to create

    Returns:
        Created contact ID

    Raises:
        ValueError: If creation fails
        RuntimeError: If database operation fails
    """
    with db_transaction() as (conn, cursor):
        cursor.execute("""
            INSERT INTO contatti (
                nome, cognome, email, telefono, cellulare, azienda, ruolo,
                indirizzo, citta, provincia, cap, paese, stato,
                consenso_privacy, consenso_marketing, note
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            contatto.nome, contatto.cognome, contatto.email, contatto.telefono,
            contatto.cellulare, contatto.azienda, contatto.ruolo, contatto.indirizzo,
            contatto.citta, contatto.provincia, contatto.cap, contatto.paese or 'Italia',
            contatto.stato.value, contatto.consenso_privacy, contatto.consenso_marketing,
            contatto.note
        ))
        cursor.execute("SELECT last_insert_rowid()")
        contatto_id = cursor.fetchone()[0]
        if not contatto_id:
            raise ValueError("Failed to create contatto")
        if contatto.liste_ids:
            for lista_id in contatto.liste_ids:
                cursor.execute(
                    "INSERT INTO contatto_lista (contatto_id, lista_id) VALUES (?, ?)",
                    (contatto_id, lista_id)
                )
    return contatto_id


def repository_get_contatto_by_id(contatto_id: int, include_deleted: bool = False) -> dict:
    """Retrieve contatto by ID.

    Args:
        contatto_id: Contact ID
        include_deleted: Include soft-deleted contacts

    Returns:
        Contact data dictionary

    Raises:
        ValueError: If contatto_id invalid or not found
    """
    if contatto_id <= 0:
        raise ValueError("contatto_id must be positive")
    with db_cursor(autocommit=False) as cursor:
        query = "SELECT * FROM contatti WHERE id = ?"
        params = [contatto_id]
        if not include_deleted:
            query += " AND deleted_at IS NULL"
        cursor.execute(query, params)
        row = cursor.fetchone()
        if not row:
            raise ValueError(f"Contact {contatto_id} not found")
        contatto = dict(zip([column[0] for column in cursor.description], row))
        cursor.execute("""
            SELECT l.* FROM liste_contatti l
            JOIN contatto_lista cl ON l.id = cl.lista_id
            WHERE cl.contatto_id = ?
        """, (contatto_id,))
        liste = []
        for list_row in cursor.fetchall():
            liste.append(dict(zip([column[0] for column in cursor.description], list_row)))
        contatto['liste'] = liste
    return contatto


def repository_get_all_contatti(
    page: int = 1,
    page_size: int = 50,
    include_deleted: bool = False
) -> tuple[List[dict], int]:
    """Retrieve paginated list of contatti.

    Args:
        page: Page number (1-indexed)
        page_size: Items per page
        include_deleted: Include soft-deleted contacts

    Returns:
        Tuple of (contacts list, total count)

    Raises:
        ValueError: If pagination parameters invalid
    """
    if page <= 0:
        raise ValueError("page must be >= 1")
    if page_size <= 0:
        raise ValueError("page_size must be positive")
    with db_cursor(autocommit=False) as cursor:
        count_query = "SELECT COUNT(*) FROM contatti"
        if not include_deleted:
            count_query += " WHERE deleted_at IS NULL"
        cursor.execute(count_query)
        total = cursor.fetchone()[0]
        query = "SELECT * FROM contatti"
        if not include_deleted:
            query += " WHERE deleted_at IS NULL"
        query += " ORDER BY created_at DESC LIMIT ? OFFSET ?"
        offset = (page - 1) * page_size
        cursor.execute(query, (page_size, offset))
        contatti = []
        for row in cursor.fetchall():
            contatto = dict(zip([column[0] for column in cursor.description], row))
            cursor.execute("""
                SELECT l.* FROM liste_contatti l
                JOIN contatto_lista cl ON l.id = cl.lista_id
                WHERE cl.contatto_id = ?
            """, (contatto['id'],))
            liste = []
            for list_row in cursor.fetchall():
                liste.append(dict(zip([column[0] for column in cursor.description], list_row)))
            contatto['liste'] = liste
            contatti.append(contatto)
    return contatti, total


def repository_update_contatto(contatto_id: int, contatto: ContattoUpdate) -> bool:
    """Update existing contatto.

    Args:
        contatto_id: Contact ID to update
        contatto: Updated contact data

    Returns:
        True if updated successfully

    Raises:
        ValueError: If contatto_id invalid or not found
    """
    if contatto_id <= 0:
        raise ValueError("contatto_id must be positive")
    with db_transaction() as (conn, cursor):
        updates = []
        params = []
        if contatto.nome is not None:
            updates.append("nome = ?")
            params.append(contatto.nome)
        if contatto.cognome is not None:
            updates.append("cognome = ?")
            params.append(contatto.cognome)
        if contatto.email is not None:
            updates.append("email = ?")
            params.append(contatto.email)
        if contatto.telefono is not None:
            updates.append("telefono = ?")
            params.append(contatto.telefono)
        if contatto.cellulare is not None:
            updates.append("cellulare = ?")
            params.append(contatto.cellulare)
        if contatto.azienda is not None:
            updates.append("azienda = ?")
            params.append(contatto.azienda)
        if contatto.ruolo is not None:
            updates.append("ruolo = ?")
            params.append(contatto.ruolo)
        if contatto.indirizzo is not None:
            updates.append("indirizzo = ?")
            params.append(contatto.indirizzo)
        if contatto.citta is not None:
            updates.append("citta = ?")
            params.append(contatto.citta)
        if contatto.provincia is not None:
            updates.append("provincia = ?")
            params.append(contatto.provincia)
        if contatto.cap is not None:
            updates.append("cap = ?")
            params.append(contatto.cap)
        if contatto.paese is not None:
            updates.append("paese = ?")
            params.append(contatto.paese)
        if contatto.stato is not None:
            updates.append("stato = ?")
            params.append(contatto.stato.value)
        if contatto.consenso_privacy is not None:
            updates.append("consenso_privacy = ?")
            params.append(contatto.consenso_privacy)
        if contatto.consenso_marketing is not None:
            updates.append("consenso_marketing = ?")
            params.append(contatto.consenso_marketing)
        if contatto.note is not None:
            updates.append("note = ?")
            params.append(contatto.note)
        if not updates:
            return True
        updates.append("updated_at = CURRENT_TIMESTAMP")
        params.append(contatto_id)
        query = f"UPDATE contatti SET {', '.join(updates)} WHERE id = ? AND deleted_at IS NULL"
        cursor.execute(query, params)
        if cursor.rowcount == 0:
            raise ValueError(f"Contact {contatto_id} not found or already deleted")
        if contatto.liste_ids is not None:
            cursor.execute("DELETE FROM contatto_lista WHERE contatto_id = ?", (contatto_id,))
            for lista_id in contatto.liste_ids:
                cursor.execute(
                    "INSERT INTO contatto_lista (contatto_id, lista_id) VALUES (?, ?)",
                    (contatto_id, lista_id)
                )
    return True


def repository_soft_delete_contatto(contatto_id: int) -> bool:
    """Soft delete contatto (set deleted_at timestamp).

    Args:
        contatto_id: Contact ID to delete

    Returns:
        True if deleted successfully

    Raises:
        ValueError: If contatto_id invalid or not found
    """
    if contatto_id <= 0:
        raise ValueError("contatto_id must be positive")
    with db_cursor() as cursor:
        cursor.execute(
            "UPDATE contatti SET deleted_at = CURRENT_TIMESTAMP WHERE id = ? AND deleted_at IS NULL",
            (contatto_id,)
        )
        if cursor.rowcount == 0:
            raise ValueError(f"Contact {contatto_id} not found or already deleted")
    return True


def repository_restore_contatto(contatto_id: int) -> bool:
    """Restore soft-deleted contatto.

    Args:
        contatto_id: Contact ID to restore

    Returns:
        True if restored successfully

    Raises:
        ValueError: If contatto_id invalid or not found
    """
    if contatto_id <= 0:
        raise ValueError("contatto_id must be positive")
    with db_cursor() as cursor:
        cursor.execute(
            "UPDATE contatti SET deleted_at = NULL WHERE id = ?",
            (contatto_id,)
        )
        if cursor.rowcount == 0:
            raise ValueError(f"Contact {contatto_id} not found")
    return True


def repository_hard_delete_contatto(contatto_id: int) -> bool:
    """Permanently delete contatto from database.

    Args:
        contatto_id: Contact ID to delete

    Returns:
        True if deleted successfully

    Raises:
        ValueError: If contatto_id invalid or not found
    """
    if contatto_id <= 0:
        raise ValueError("contatto_id must be positive")
    with db_transaction() as (conn, cursor):
        cursor.execute("DELETE FROM contatto_lista WHERE contatto_id = ?", (contatto_id,))
        cursor.execute("DELETE FROM contatti WHERE id = ?", (contatto_id,))
        if cursor.rowcount == 0:
            raise ValueError(f"Contact {contatto_id} not found")
    return True


def repository_search_contatti(query: str, page: int = 1, page_size: int = 50) -> tuple[List[dict], int]:
    """Search contatti by query string.

    Args:
        query: Search query string
        page: Page number (1-indexed)
        page_size: Items per page

    Returns:
        Tuple of (matching contacts, total count)

    Raises:
        ValueError: If parameters invalid
    """
    if not query:
        raise ValueError("query cannot be empty")
    if page <= 0:
        raise ValueError("page must be >= 1")
    if page_size <= 0:
        raise ValueError("page_size must be positive")
    search_pattern = f"%{query}%"
    with db_cursor(autocommit=False) as cursor:
        cursor.execute("""
            SELECT COUNT(*) FROM contatti
            WHERE deleted_at IS NULL AND (
                nome LIKE ? OR cognome LIKE ? OR email LIKE ? OR azienda LIKE ?
            )
        """, (search_pattern, search_pattern, search_pattern, search_pattern))
        total = cursor.fetchone()[0]
        offset = (page - 1) * page_size
        cursor.execute("""
            SELECT * FROM contatti
            WHERE deleted_at IS NULL AND (
                nome LIKE ? OR cognome LIKE ? OR email LIKE ? OR azienda LIKE ?
            )
            ORDER BY created_at DESC LIMIT ? OFFSET ?
        """, (search_pattern, search_pattern, search_pattern, search_pattern, page_size, offset))
        contatti = []
        for row in cursor.fetchall():
            contatto = dict(zip([column[0] for column in cursor.description], row))
            contatto['liste'] = []
            contatti.append(contatto)
    return contatti, total


def repository_create_lista(nome: str, descrizione: str | None = None) -> int:
    """Create a new lista contatti.

    Args:
        nome: List name
        descrizione: Optional description

    Returns:
        Created list ID

    Raises:
        ValueError: If nome empty or creation fails
    """
    if not nome or not nome.strip():
        raise ValueError("nome cannot be empty")
    with db_cursor() as cursor:
        cursor.execute(
            "INSERT INTO liste_contatti (nome, descrizione) VALUES (?, ?)",
            (nome, descrizione)
        )
        cursor.execute("SELECT last_insert_rowid()")
        lista_id = cursor.fetchone()[0]
        if not lista_id:
            raise ValueError("Failed to create lista")
    return lista_id


def repository_get_all_liste() -> List[dict]:
    """Retrieve all liste contatti.

    Returns:
        List of all contact lists
    """
    with db_cursor(autocommit=False) as cursor:
        cursor.execute("SELECT * FROM liste_contatti ORDER BY nome")
        liste = []
        for row in cursor.fetchall():
            liste.append(dict(zip([column[0] for column in cursor.description], row)))
    return liste


def repository_get_lista_by_id(lista_id: int) -> dict:
    """Retrieve lista by ID.

    Args:
        lista_id: List ID

    Returns:
        List data dictionary

    Raises:
        ValueError: If lista_id invalid or not found
    """
    if lista_id <= 0:
        raise ValueError("lista_id must be positive")
    with db_cursor(autocommit=False) as cursor:
        cursor.execute("SELECT * FROM liste_contatti WHERE id = ?", (lista_id,))
        row = cursor.fetchone()
        if not row:
            raise ValueError(f"List {lista_id} not found")
        result = dict(zip([column[0] for column in cursor.description], row))
    return result


def repository_delete_lista(lista_id: int) -> bool:
    """Delete lista contatti.

    Args:
        lista_id: List ID to delete

    Returns:
        True if deleted successfully

    Raises:
        ValueError: If lista_id invalid or not found
    """
    if lista_id <= 0:
        raise ValueError("lista_id must be positive")
    with db_transaction() as (conn, cursor):
        cursor.execute("DELETE FROM contatto_lista WHERE lista_id = ?", (lista_id,))
        cursor.execute("DELETE FROM liste_contatti WHERE id = ?", (lista_id,))
        if cursor.rowcount == 0:
            raise ValueError(f"List {lista_id} not found")
    return True
