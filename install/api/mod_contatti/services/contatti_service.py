from typing import Dict, Any
import os
from ..models.contatto_models import (
    ContattoCreate,
    ContattoUpdate,
    ContattoResponse,
    ContattoList,
    ListaContattiCreate,
    ListaContattiResponse,
    DeleteResult,
    RestoreResult,
    ListeResult
)
from ..repositories.contatti_repository import ContattiRepository, ListeContattiRepository

db_dsn = os.getenv("DB_DSN", "DSN=hello").replace("DSN=", "")
contatti_repo = ContattiRepository(db_dsn)
liste_repo = ListeContattiRepository(db_dsn)


def create_contatto(contatto: ContattoCreate, output: Dict[str, Any]) -> bool:
    """Create a new contatto, populating output dict and returning success status.

    Args:
        contatto: Contact data to create
        output: Dictionary to populate with validated results

    Returns:
        bool: True if successful, False otherwise (error in output['error'])
    """
    class Err:
        repository_create: bool = False
        repository_get: bool = False

    retv: bool = False
    result: Dict[str, Any] = {}
    error: str | None = None

    try:
        contatto_id = contatti_repo.create(contatto)
        if not contatto_id:
            Err.repository_create = True
            raise ValueError()
        contatto_data = contatti_repo.get_by_id(contatto_id)
        if not contatto_data:
            Err.repository_get = True
            raise ValueError()
        contatto_response = ContattoResponse(**contatto_data)
        result.update(contatto_response.model_dump())
        retv = True

    except Exception as e:
        if Err.repository_create:
            error = "Failed to create contact in repository"
        elif Err.repository_get:
            error = "Failed to retrieve created contact"
        else:
            error = str(e) or "Unknown error"

    if retv:
        output.update(result)
    else:
        output["error"] = error

    return retv


def get_contatto(contatto_id: int, output: Dict[str, Any]) -> bool:
    """Get a contatto by ID, populating output dict and returning success status.

    Args:
        contatto_id: ID of the contact to retrieve
        output: Dictionary to populate with validated results

    Returns:
        bool: True if successful, False otherwise (error in output['error'])
    """
    class Err:
        not_found: bool = False

    retv: bool = False
    result: Dict[str, Any] = {}
    error: str | None = None

    try:
        contatto_data = contatti_repo.get_by_id(contatto_id)
        if not contatto_data:
            Err.not_found = True
            raise ValueError()
        contatto_response = ContattoResponse(**contatto_data)
        result.update(contatto_response.model_dump())
        retv = True

    except Exception as e:
        if Err.not_found:
            error = "Contact not found"
        else:
            error = str(e) or "Unknown error"

    if retv:
        output.update(result)
    else:
        output["error"] = error

    return retv


def get_all_contatti(page: int, page_size: int, include_deleted: bool, output: Dict[str, Any]) -> bool:
    """Get all contatti with pagination, populating output dict and returning success status.

    Args:
        page: Page number (starting from 1)
        page_size: Number of items per page
        include_deleted: Whether to include soft-deleted contacts
        output: Dictionary to populate with validated results

    Returns:
        bool: True if successful, False otherwise (error in output['error'])
    """
    class Err:
        repository_get: bool = False

    retv: bool = False
    result: Dict[str, Any] = {}
    error: str | None = None

    try:
        contatti_data, total = contatti_repo.get_all(page, page_size, include_deleted)
        contatti = [ContattoResponse.model_validate(c) for c in contatti_data]
        contatti_list = ContattoList(
            total=total,
            page=page,
            page_size=page_size,
            contatti=contatti
        )
        result.update(contatti_list.model_dump(mode='json'))
        retv = True

    except Exception as e:
        if Err.repository_get:
            error = "Repository error during retrieval"
        else:
            error = str(e) or "Unknown error"

    if retv:
        output.update(result)
    else:
        output["error"] = error

    return retv


def update_contatto(contatto_id: int, contatto: ContattoUpdate, output: Dict[str, Any]) -> bool:
    """Update an existing contatto, populating output dict and returning success status.

    Args:
        contatto_id: ID of the contact to update
        contatto: Contact data to update
        output: Dictionary to populate with validated results

    Returns:
        bool: True if successful, False otherwise (error in output['error'])
    """
    class Err:
        repository_update: bool = False
        repository_get: bool = False

    retv: bool = False
    result: Dict[str, Any] = {}
    error: str | None = None

    try:
        success = contatti_repo.update(contatto_id, contatto)
        if not success:
            Err.repository_update = True
            raise ValueError()
        contatto_data = contatti_repo.get_by_id(contatto_id)
        if not contatto_data:
            Err.repository_get = True
            raise ValueError()
        contatto_response = ContattoResponse(**contatto_data)
        result.update(contatto_response.model_dump())
        retv = True

    except Exception as e:
        if Err.repository_update:
            error = "Contact not found or update failed"
        elif Err.repository_get:
            error = "Failed to retrieve updated contact"
        else:
            error = str(e) or "Unknown error"

    if retv:
        output.update(result)
    else:
        output["error"] = error

    return retv


def soft_delete_contatto(contatto_id: int, output: Dict[str, Any]) -> bool:
    """Soft delete a contatto, populating output dict and returning success status.

    Args:
        contatto_id: ID of the contact to soft delete
        output: Dictionary to populate with validated results

    Returns:
        bool: True if successful, False otherwise (error in output['error'])
    """
    class Err:
        repository_delete: bool = False

    retv: bool = False
    result: Dict[str, Any] = {}
    error: str | None = None

    try:
        success = contatti_repo.soft_delete(contatto_id)
        if not success:
            Err.repository_delete = True
            raise ValueError()
        delete_result = DeleteResult(deleted=True)
        result.update(delete_result.model_dump())
        retv = True

    except Exception as e:
        if Err.repository_delete:
            error = "Contact not found or already deleted"
        else:
            error = str(e) or "Unknown error"

    if retv:
        output.update(result)
    else:
        output["error"] = error

    return retv


def restore_contatto(contatto_id: int, output: Dict[str, Any]) -> bool:
    """Restore a soft-deleted contatto, populating output dict and returning success status.

    Args:
        contatto_id: ID of the contact to restore
        output: Dictionary to populate with validated results

    Returns:
        bool: True if successful, False otherwise (error in output['error'])
    """
    class Err:
        repository_restore: bool = False

    retv: bool = False
    result: Dict[str, Any] = {}
    error: str | None = None

    try:
        success = contatti_repo.restore(contatto_id)
        if not success:
            Err.repository_restore = True
            raise ValueError()
        restore_result = RestoreResult(restored=True)
        result.update(restore_result.model_dump())
        retv = True

    except Exception as e:
        if Err.repository_restore:
            error = "Contact not found or not deleted"
        else:
            error = str(e) or "Unknown error"

    if retv:
        output.update(result)
    else:
        output["error"] = error

    return retv


def hard_delete_contatto(contatto_id: int, output: Dict[str, Any]) -> bool:
    """Hard delete a contatto, populating output dict and returning success status.

    Args:
        contatto_id: ID of the contact to permanently delete
        output: Dictionary to populate with validated results

    Returns:
        bool: True if successful, False otherwise (error in output['error'])
    """
    class Err:
        repository_delete: bool = False

    retv: bool = False
    result: Dict[str, Any] = {}
    error: str | None = None

    try:
        success = contatti_repo.hard_delete(contatto_id)
        if not success:
            Err.repository_delete = True
            raise ValueError()
        delete_result = DeleteResult(deleted=True)
        result.update(delete_result.model_dump())
        retv = True

    except Exception as e:
        if Err.repository_delete:
            error = "Contact not found"
        else:
            error = str(e) or "Unknown error"

    if retv:
        output.update(result)
    else:
        output["error"] = error

    return retv


def search_contatti(query: str, page: int, page_size: int, output: Dict[str, Any]) -> bool:
    """Search contatti by query, populating output dict and returning success status.

    Args:
        query: Search query string
        page: Page number (starting from 1)
        page_size: Number of items per page
        output: Dictionary to populate with validated results

    Returns:
        bool: True if successful, False otherwise (error in output['error'])
    """
    class Err:
        repository_search: bool = False

    retv: bool = False
    result: Dict[str, Any] = {}
    error: str | None = None

    try:
        contatti_data, total = contatti_repo.search(query, page, page_size)
        contatti = [ContattoResponse(**c) for c in contatti_data]
        contatti_list = ContattoList(
            total=total,
            page=page,
            page_size=page_size,
            contatti=contatti
        )
        result.update(contatti_list.model_dump())
        retv = True

    except Exception as e:
        if Err.repository_search:
            error = "Repository error during search"
        else:
            error = str(e) or "Unknown error"

    if retv:
        output.update(result)
    else:
        output["error"] = error

    return retv


def create_lista(lista: ListaContattiCreate, output: Dict[str, Any]) -> bool:
    """Create a new lista contatti, populating output dict and returning success status.

    Args:
        lista: List data to create
        output: Dictionary to populate with validated results

    Returns:
        bool: True if successful, False otherwise (error in output['error'])
    """
    class Err:
        repository_create: bool = False
        repository_get: bool = False

    retv: bool = False
    result: Dict[str, Any] = {}
    error: str | None = None

    try:
        lista_id = liste_repo.create(lista.nome, lista.descrizione)
        if not lista_id:
            Err.repository_create = True
            raise ValueError()
        lista_data = liste_repo.get_by_id(lista_id)
        if not lista_data:
            Err.repository_get = True
            raise ValueError()
        lista_response = ListaContattiResponse(**lista_data)
        result.update(lista_response.model_dump())
        retv = True

    except Exception as e:
        if Err.repository_create:
            error = "Failed to create list in repository"
        elif Err.repository_get:
            error = "Failed to retrieve created list"
        else:
            error = str(e) or "Unknown error"

    if retv:
        output.update(result)
    else:
        output["error"] = error

    return retv


def get_all_liste(output: Dict[str, Any]) -> bool:
    """Get all liste contatti, populating output dict and returning success status.

    Args:
        output: Dictionary to populate with validated results

    Returns:
        bool: True if successful, False otherwise (error in output['error'])
    """
    class Err:
        repository_get: bool = False

    retv: bool = False
    result: Dict[str, Any] = {}
    error: str | None = None

    try:
        liste_data = liste_repo.get_all()
        liste = [ListaContattiResponse(**l) for l in liste_data]
        liste_result = ListeResult(liste=liste)
        result.update(liste_result.model_dump())
        retv = True

    except Exception as e:
        if Err.repository_get:
            error = "Repository error during retrieval"
        else:
            error = str(e) or "Unknown error"

    if retv:
        output.update(result)
    else:
        output["error"] = error

    return retv


def get_lista(lista_id: int, output: Dict[str, Any]) -> bool:
    """Get a lista contatti by ID, populating output dict and returning success status.

    Args:
        lista_id: ID of the list to retrieve
        output: Dictionary to populate with validated results

    Returns:
        bool: True if successful, False otherwise (error in output['error'])
    """
    class Err:
        not_found: bool = False

    retv: bool = False
    result: Dict[str, Any] = {}
    error: str | None = None

    try:
        lista_data = liste_repo.get_by_id(lista_id)
        if not lista_data:
            Err.not_found = True
            raise ValueError()
        lista_response = ListaContattiResponse(**lista_data)
        result.update(lista_response.model_dump())
        retv = True

    except Exception as e:
        if Err.not_found:
            error = "List not found"
        else:
            error = str(e) or "Unknown error"

    if retv:
        output.update(result)
    else:
        output["error"] = error

    return retv


def delete_lista(lista_id: int, output: Dict[str, Any]) -> bool:
    """Delete a lista contatti, populating output dict and returning success status.

    Args:
        lista_id: ID of the list to delete
        output: Dictionary to populate with validated results

    Returns:
        bool: True if successful, False otherwise (error in output['error'])
    """
    class Err:
        repository_delete: bool = False

    retv: bool = False
    result: Dict[str, Any] = {}
    error: str | None = None

    try:
        success = liste_repo.delete(lista_id)
        if not success:
            Err.repository_delete = True
            raise ValueError()
        delete_result = DeleteResult(deleted=True)
        result.update(delete_result.model_dump())
        retv = True

    except Exception as e:
        if Err.repository_delete:
            error = "List not found"
        else:
            error = str(e) or "Unknown error"

    if retv:
        output.update(result)
    else:
        output["error"] = error

    return retv
