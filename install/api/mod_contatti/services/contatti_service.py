from typing import Dict, Any
import os
from ..models.contatto_models import (
    ContattoCreate,
    ContattoUpdate,
    ContattoResponse,
    ContattoList,
    ListaContattiCreate,
    ListaContattiResponse
)
from ..repositories.contatti_repository import ContattiRepository, ListeContattiRepository

db_dsn = os.getenv("DB_DSN", "DSN=hello").replace("DSN=", "")
contatti_repo = ContattiRepository(db_dsn)
liste_repo = ListeContattiRepository(db_dsn)


# @validate_arguments removed - not compatible with Pydantic v2
def create_contatto(contatto: ContattoCreate, output: Dict[str, Any]) -> bool:
    class Err:
        repository_create: bool = False
        repository_get: bool = False
        validation: bool = False

    retv: bool = False
    result: Dict[str, Any] = {}
    error: str | None = None

    try:
        contatto_id = contatti_repo.create(contatto)
        if not contatto_id:
            if Err.repository_create:
                error = "Failed to create contact in repository"
        else:
            contatto_data = contatti_repo.get_by_id(contatto_id)
            if not contatto_data:
                if Err.repository_get:
                    error = "Failed to retrieve created contact"
            else:
                try:
                    contatto_response = ContattoResponse(**contatto_data)
                    result.update(contatto_response.model_dump())
                    retv = True
                except Exception as e:
                    if Err.validation:
                        error = f"Validation error: {str(e)}"
    except Exception as e:
        error = str(e)

    if retv:
        output.update(result)
    else:
        output["error"] = error

    return retv


# @validate_arguments removed - not compatible with Pydantic v2
def get_contatto(contatto_id: int, output: Dict[str, Any]) -> bool:
    class Err:
        repository_get: bool = False
        validation: bool = False
        not_found: bool = False

    retv: bool = False
    result: Dict[str, Any] = {}
    error: str | None = None

    try:
        contatto_data = contatti_repo.get_by_id(contatto_id)
        if not contatto_data:
            if Err.not_found:
                error = "Contact not found"
        else:
            try:
                contatto_response = ContattoResponse(**contatto_data)
                result.update(contatto_response.model_dump())
                retv = True
            except Exception as e:
                if Err.validation:
                    error = f"Validation error: {str(e)}"
    except Exception as e:
        if Err.repository_get:
            error = f"Repository error: {str(e)}"

    if retv:
        output.update(result)
    else:
        output["error"] = error

    return retv


# @validate_arguments removed - not compatible with Pydantic v2
def get_all_contatti(page: int, page_size: int, include_deleted: bool, output: Dict[str, Any]) -> bool:
    class Err:
        repository_get: bool = False
        validation: bool = False

    retv: bool = False
    result: Dict[str, Any] = {}
    error: str | None = None

    try:
        contatti_data, total = contatti_repo.get_all(page, page_size, include_deleted)
        try:
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
            error = f"Validation error: {str(e)}"
    except Exception as e:
        error = f"Repository error: {str(e)}"

    if retv:
        output.update(result)
    else:
        output["error"] = error if error else "Unknown error"

    return retv


# @validate_arguments removed - not compatible with Pydantic v2
def update_contatto(contatto_id: int, contatto: ContattoUpdate, output: Dict[str, Any]) -> bool:
    class Err:
        repository_update: bool = False
        repository_get: bool = False
        validation: bool = False
        not_found: bool = False

    retv: bool = False
    result: Dict[str, Any] = {}
    error: str | None = None

    try:
        success = contatti_repo.update(contatto_id, contatto)
        if not success:
            if Err.not_found:
                error = "Contact not found or update failed"
        else:
            contatto_data = contatti_repo.get_by_id(contatto_id)
            if not contatto_data:
                if Err.repository_get:
                    error = "Failed to retrieve updated contact"
            else:
                try:
                    contatto_response = ContattoResponse(**contatto_data)
                    result.update(contatto_response.model_dump())
                    retv = True
                except Exception as e:
                    if Err.validation:
                        error = f"Validation error: {str(e)}"
    except Exception as e:
        if Err.repository_update:
            error = f"Repository error: {str(e)}"

    if retv:
        output.update(result)
    else:
        output["error"] = error

    return retv


# @validate_arguments removed - not compatible with Pydantic v2
def soft_delete_contatto(contatto_id: int, output: Dict[str, Any]) -> bool:
    class Err:
        repository_delete: bool = False
        not_found: bool = False

    retv: bool = False
    result: Dict[str, Any] = {}
    error: str | None = None

    try:
        success = contatti_repo.soft_delete(contatto_id)
        if not success:
            if Err.not_found:
                error = "Contact not found or already deleted"
        else:
            result["deleted"] = True
            retv = True
    except Exception as e:
        if Err.repository_delete:
            error = f"Repository error: {str(e)}"

    if retv:
        output.update(result)
    else:
        output["error"] = error

    return retv


# @validate_arguments removed - not compatible with Pydantic v2
def restore_contatto(contatto_id: int, output: Dict[str, Any]) -> bool:
    class Err:
        repository_restore: bool = False
        not_found: bool = False

    retv: bool = False
    result: Dict[str, Any] = {}
    error: str | None = None

    try:
        success = contatti_repo.restore(contatto_id)
        if not success:
            if Err.not_found:
                error = "Contact not found or not deleted"
        else:
            result["restored"] = True
            retv = True
    except Exception as e:
        if Err.repository_restore:
            error = f"Repository error: {str(e)}"

    if retv:
        output.update(result)
    else:
        output["error"] = error

    return retv


# @validate_arguments removed - not compatible with Pydantic v2
def hard_delete_contatto(contatto_id: int, output: Dict[str, Any]) -> bool:
    class Err:
        repository_delete: bool = False
        not_found: bool = False

    retv: bool = False
    result: Dict[str, Any] = {}
    error: str | None = None

    try:
        success = contatti_repo.hard_delete(contatto_id)
        if not success:
            if Err.not_found:
                error = "Contact not found"
        else:
            result["deleted"] = True
            retv = True
    except Exception as e:
        if Err.repository_delete:
            error = f"Repository error: {str(e)}"

    if retv:
        output.update(result)
    else:
        output["error"] = error

    return retv


# @validate_arguments removed - not compatible with Pydantic v2
def search_contatti(query: str, page: int, page_size: int, output: Dict[str, Any]) -> bool:
    class Err:
        repository_search: bool = False
        validation: bool = False

    retv: bool = False
    result: Dict[str, Any] = {}
    error: str | None = None

    try:
        contatti_data, total = contatti_repo.search(query, page, page_size)
        try:
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
            if Err.validation:
                error = f"Validation error: {str(e)}"
    except Exception as e:
        if Err.repository_search:
            error = f"Repository error: {str(e)}"

    if retv:
        output.update(result)
    else:
        output["error"] = error

    return retv


# @validate_arguments removed - not compatible with Pydantic v2
def create_lista(lista: ListaContattiCreate, output: Dict[str, Any]) -> bool:
    class Err:
        repository_create: bool = False
        repository_get: bool = False
        validation: bool = False

    retv: bool = False
    result: Dict[str, Any] = {}
    error: str | None = None

    try:
        lista_id = liste_repo.create(lista.nome, lista.descrizione)
        if not lista_id:
            if Err.repository_create:
                error = "Failed to create list in repository"
        else:
            lista_data = liste_repo.get_by_id(lista_id)
            if not lista_data:
                if Err.repository_get:
                    error = "Failed to retrieve created list"
            else:
                try:
                    lista_response = ListaContattiResponse(**lista_data)
                    result.update(lista_response.model_dump())
                    retv = True
                except Exception as e:
                    if Err.validation:
                        error = f"Validation error: {str(e)}"
    except Exception as e:
        error = str(e)

    if retv:
        output.update(result)
    else:
        output["error"] = error

    return retv


# @validate_arguments removed - not compatible with Pydantic v2
def get_all_liste(output: Dict[str, Any]) -> bool:
    class Err:
        repository_get: bool = False
        validation: bool = False

    retv: bool = False
    result: Dict[str, Any] = {}
    error: str | None = None

    try:
        liste_data = liste_repo.get_all()
        try:
            liste = [ListaContattiResponse(**l) for l in liste_data]
            result["liste"] = [l.model_dump() for l in liste]
            retv = True
        except Exception as e:
            if Err.validation:
                error = f"Validation error: {str(e)}"
    except Exception as e:
        if Err.repository_get:
            error = f"Repository error: {str(e)}"

    if retv:
        output.update(result)
    else:
        output["error"] = error

    return retv


# @validate_arguments removed - not compatible with Pydantic v2
def get_lista(lista_id: int, output: Dict[str, Any]) -> bool:
    class Err:
        repository_get: bool = False
        validation: bool = False
        not_found: bool = False

    retv: bool = False
    result: Dict[str, Any] = {}
    error: str | None = None

    try:
        lista_data = liste_repo.get_by_id(lista_id)
        if not lista_data:
            if Err.not_found:
                error = "List not found"
        else:
            try:
                lista_response = ListaContattiResponse(**lista_data)
                result.update(lista_response.model_dump())
                retv = True
            except Exception as e:
                if Err.validation:
                    error = f"Validation error: {str(e)}"
    except Exception as e:
        if Err.repository_get:
            error = f"Repository error: {str(e)}"

    if retv:
        output.update(result)
    else:
        output["error"] = error

    return retv


# @validate_arguments removed - not compatible with Pydantic v2
def delete_lista(lista_id: int, output: Dict[str, Any]) -> bool:
    class Err:
        repository_delete: bool = False
        not_found: bool = False

    retv: bool = False
    result: Dict[str, Any] = {}
    error: str | None = None

    try:
        success = liste_repo.delete(lista_id)
        if not success:
            if Err.not_found:
                error = "List not found"
        else:
            result["deleted"] = True
            retv = True
    except Exception as e:
        if Err.repository_delete:
            error = f"Repository error: {str(e)}"

    if retv:
        output.update(result)
    else:
        output["error"] = error

    return retv
