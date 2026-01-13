from typing import Dict, Any
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
from ..repositories.contatti_repository import (
    repository_create_contatto,
    repository_get_contatto_by_id,
    repository_get_all_contatti,
    repository_update_contatto,
    repository_soft_delete_contatto,
    repository_restore_contatto,
    repository_hard_delete_contatto,
    repository_search_contatti,
    repository_create_lista,
    repository_get_all_liste,
    repository_get_lista_by_id,
    repository_delete_lista
)


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
        contatto_id = repository_create_contatto(contatto)
        contatto_data = repository_get_contatto_by_id(contatto_id)
        contatto_response = ContattoResponse(**contatto_data)
        result.update(contatto_response.model_dump())
        retv = True

    except ValueError as e:
        error = str(e)
    except Exception as e:
        error = f"Unexpected error: {str(e)}"

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
        contatto_data = repository_get_contatto_by_id(contatto_id)
        contatto_response = ContattoResponse(**contatto_data)
        result.update(contatto_response.model_dump())
        retv = True

    except ValueError as e:
        Err.not_found = True
        error = str(e)
    except Exception as e:
        error = f"Unexpected error: {str(e)}"

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
        contatti_data, total = repository_get_all_contatti(page, page_size, include_deleted)
        contatti = [ContattoResponse.model_validate(c) for c in contatti_data]
        contatti_list = ContattoList(
            total=total,
            page=page,
            page_size=page_size,
            contatti=contatti
        )
        result.update(contatti_list.model_dump(mode='json'))
        retv = True

    except ValueError as e:
        error = str(e)
    except Exception as e:
        error = f"Unexpected error: {str(e)}"

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
        repository_update_contatto(contatto_id, contatto)
        contatto_data = repository_get_contatto_by_id(contatto_id)
        contatto_response = ContattoResponse(**contatto_data)
        result.update(contatto_response.model_dump())
        retv = True

    except ValueError as e:
        error = str(e)
    except Exception as e:
        error = f"Unexpected error: {str(e)}"

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
        repository_soft_delete_contatto(contatto_id)
        delete_result = DeleteResult(deleted=True)
        result.update(delete_result.model_dump())
        retv = True

    except ValueError as e:
        Err.repository_delete = True
        error = str(e)
    except Exception as e:
        error = f"Unexpected error: {str(e)}"

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
        repository_restore_contatto(contatto_id)
        restore_result = RestoreResult(restored=True)
        result.update(restore_result.model_dump())
        retv = True

    except ValueError as e:
        Err.repository_restore = True
        error = str(e)
    except Exception as e:
        error = f"Unexpected error: {str(e)}"

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
        repository_hard_delete_contatto(contatto_id)
        delete_result = DeleteResult(deleted=True)
        result.update(delete_result.model_dump())
        retv = True

    except ValueError as e:
        Err.repository_delete = True
        error = str(e)
    except Exception as e:
        error = f"Unexpected error: {str(e)}"

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
        contatti_data, total = repository_search_contatti(query, page, page_size)
        contatti = [ContattoResponse(**c) for c in contatti_data]
        contatti_list = ContattoList(
            total=total,
            page=page,
            page_size=page_size,
            contatti=contatti
        )
        result.update(contatti_list.model_dump())
        retv = True

    except ValueError as e:
        Err.repository_search = True
        error = str(e)
    except Exception as e:
        error = f"Unexpected error: {str(e)}"

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
        lista_id = repository_create_lista(lista.nome, lista.descrizione)
        lista_data = repository_get_lista_by_id(lista_id)
        lista_response = ListaContattiResponse(**lista_data)
        result.update(lista_response.model_dump())
        retv = True

    except ValueError as e:
        error = str(e)
    except Exception as e:
        error = f"Unexpected error: {str(e)}"

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
        liste_data = repository_get_all_liste()
        liste = [ListaContattiResponse(**l) for l in liste_data]
        liste_result = ListeResult(liste=liste)
        result.update(liste_result.model_dump())
        retv = True

    except ValueError as e:
        error = str(e)
    except Exception as e:
        error = f"Unexpected error: {str(e)}"

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
        lista_data = repository_get_lista_by_id(lista_id)
        lista_response = ListaContattiResponse(**lista_data)
        result.update(lista_response.model_dump())
        retv = True

    except ValueError as e:
        Err.not_found = True
        error = str(e)
    except Exception as e:
        error = f"Unexpected error: {str(e)}"

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
        repository_delete_lista(lista_id)
        delete_result = DeleteResult(deleted=True)
        result.update(delete_result.model_dump())
        retv = True

    except ValueError as e:
        Err.repository_delete = True
        error = str(e)
    except Exception as e:
        error = f"Unexpected error: {str(e)}"

    if retv:
        output.update(result)
    else:
        output["error"] = error

    return retv
