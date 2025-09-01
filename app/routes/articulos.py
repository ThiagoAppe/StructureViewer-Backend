from fastapi import APIRouter, Query, HTTPException,Depends
from typing import List
from app.services.SIMReader.articulos import ORDERED_FIELDS, SearchArticles, GetArticlesData 
from app.services.SIMReader.estructura import GetHijos, GetPadres, GetLastLevelPadres, GetAllHijos
from app.validation import AuthRequired

router = APIRouter(prefix="/articulos", tags=["Artículos"])

@router.get("/SearchArticulo", dependencies=[Depends(AuthRequired)])
def SearchArticulo(
    field: str = Query(..., description="Campo por el que filtrar"),
    value: str = Query(..., description="Valor a buscar"),
    similar: bool = Query(False, description="Si True, busca coincidencias parciales"),
    limit: int = Query(50, ge=1, le=200, description="Cantidad máxima de registros"),
    offset: int = Query(0, ge=0, description="Desde qué registro comenzar")
):
    """
    Endpoint para buscar artículos por cualquier campo y devolver
    solo código y descripción.
    """
    try:
        if field not in ORDERED_FIELDS:
            raise HTTPException(status_code=400, detail="Campo de búsqueda no permitido.")

        results = SearchArticles(field, value, similar=similar, limit=limit, offset=offset)

        return {
            "total": len(results),
            "limit": limit,
            "offset": offset,
            "results": results
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error interno en la búsqueda de artículos.")

@router.get("/GetArticleData", dependencies=[Depends(AuthRequired)])
def GetArticles(
    codes: str = Query(..., description="Lista de códigos separados por coma, ej: 02350-01,02351-02")
):
    """
    Endpoint para obtener los campos permitidos de varios artículos por sus códigos.
    """
    art_codes = [c.strip() for c in codes.split(",") if c.strip()]
    if not art_codes:
        raise HTTPException(status_code=400, detail="No se proporcionaron códigos de artículos.")

    try:
        results = GetArticlesData(art_codes)
        return {
            "total": len(results),
            "results": results
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error interno al obtener los artículos.")