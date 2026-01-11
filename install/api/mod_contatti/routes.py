from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from .models import (
    ContattoCreate,
    ContattoUpdate,
    ContattoResponse,
    ContattoList,
    ListaContattiCreate,
    ListaContattiResponse
)
from .services import contatti_service

router = APIRouter(prefix="/api/contatti", tags=["Contatti"])


@router.post("/", response_model=ContattoResponse, status_code=201)
async def create_contatto(contatto: ContattoCreate):
    output = {}
    success = contatti_service.create_contatto(contatto=contatto, output=output)
    if success:
        return ContattoResponse(**output)
    else:
        raise HTTPException(status_code=500, detail=output.get("error", "Failed to create contact"))


@router.get("/", response_model=ContattoList)
async def get_all_contatti(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    include_deleted: bool = Query(False)
):
    output = {}
    success = contatti_service.get_all_contatti(page=page, page_size=page_size, include_deleted=include_deleted, output=output)
    if success:
        return ContattoList(**output)
    else:
        raise HTTPException(status_code=500, detail=output.get("error", "Failed to retrieve contacts"))


@router.get("/search", response_model=ContattoList)
async def search_contatti(
    q: str = Query(..., min_length=1),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100)
):
    output = {}
    success = contatti_service.search_contatti(query=q, page=page, page_size=page_size, output=output)
    if success:
        return ContattoList(**output)
    else:
        raise HTTPException(status_code=500, detail=output.get("error", "Failed to search contacts"))


@router.get("/{contatto_id}", response_model=ContattoResponse)
async def get_contatto(contatto_id: int):
    output = {}
    success = contatti_service.get_contatto(contatto_id=contatto_id, output=output)
    if success:
        return ContattoResponse(**output)
    else:
        raise HTTPException(status_code=404, detail=output.get("error", "Contact not found"))


@router.put("/{contatto_id}", response_model=ContattoResponse)
async def update_contatto(contatto_id: int, contatto: ContattoUpdate):
    output = {}
    success = contatti_service.update_contatto(contatto_id=contatto_id, contatto=contatto, output=output)
    if success:
        return ContattoResponse(**output)
    else:
        raise HTTPException(status_code=404, detail=output.get("error", "Contact not found"))


@router.delete("/{contatto_id}/soft", status_code=204)
async def soft_delete_contatto(contatto_id: int):
    output = {}
    success = contatti_service.soft_delete_contatto(contatto_id=contatto_id, output=output)
    if not success:
        raise HTTPException(status_code=404, detail=output.get("error", "Contact not found"))


@router.post("/{contatto_id}/restore", response_model=ContattoResponse)
async def restore_contatto(contatto_id: int):
    output_restore = {}
    success_restore = contatti_service.restore_contatto(contatto_id=contatto_id, output=output_restore)
    if not success_restore:
        raise HTTPException(status_code=404, detail=output_restore.get("error", "Contact not found"))

    output_get = {}
    success_get = contatti_service.get_contatto(contatto_id=contatto_id, output=output_get)
    if not success_get:
        raise HTTPException(status_code=404, detail=output_get.get("error", "Contact not found"))

    return ContattoResponse(**output_get)


@router.delete("/{contatto_id}/hard", status_code=204)
async def hard_delete_contatto(contatto_id: int):
    output = {}
    success = contatti_service.hard_delete_contatto(contatto_id=contatto_id, output=output)
    if not success:
        raise HTTPException(status_code=404, detail=output.get("error", "Contact not found"))


@router.post("/liste", response_model=ListaContattiResponse, status_code=201)
async def create_lista(lista: ListaContattiCreate):
    output = {}
    success = contatti_service.create_lista(lista=lista, output=output)
    if success:
        return ListaContattiResponse(**output)
    else:
        raise HTTPException(status_code=500, detail=output.get("error", "Failed to create list"))


@router.get("/liste", response_model=list[ListaContattiResponse])
async def get_all_liste():
    output = {}
    success = contatti_service.get_all_liste(output=output)
    if success:
        liste = output.get("liste", [])
        return [ListaContattiResponse(**l) for l in liste]
    else:
        raise HTTPException(status_code=500, detail=output.get("error", "Failed to retrieve lists"))


@router.get("/liste/{lista_id}", response_model=ListaContattiResponse)
async def get_lista(lista_id: int):
    output = {}
    success = contatti_service.get_lista(lista_id=lista_id, output=output)
    if success:
        return ListaContattiResponse(**output)
    else:
        raise HTTPException(status_code=404, detail=output.get("error", "List not found"))


@router.delete("/liste/{lista_id}", status_code=204)
async def delete_lista(lista_id: int):
    output = {}
    success = contatti_service.delete_lista(lista_id=lista_id, output=output)
    if not success:
        raise HTTPException(status_code=404, detail=output.get("error", "List not found"))
