from fastapi import APIRouter, Query, HTTPException, Depends
from typing import List
from app.services.SIMReader.articulos import (
    ORDERED_FIELDS,
    search_articles,
    get_articles_data
)
from app.services.SIMReader.estructura import (
    get_hijos,
    get_padres,
    get_last_level_padres,
    get_all_hijos
)
from app.validation import auth_required

router = APIRouter(prefix="/articulos", tags=["Artículos"])

@router.get("/search-articulo", dependencies=[Depends(auth_required)])
def search_articulo(
    field: str = Query(..., description="Campo por el que filtrar"),
    value: str = Query(..., description="Valor a buscar"),
    limit: int = Query(50, ge=1, le=200, description="Cantidad máxima de registros"),
    offset: int = Query(0, ge=0, description="Desde qué registro comenzar")
):
    """
    Busca artículos por un campo permitido y retorna código, descripción,
    letra de cambio y stock actual.
    """
    try:
        if field not in ORDERED_FIELDS:
            raise HTTPException(status_code=400, detail="Campo de búsqueda no permitido.")

        results = search_articles(
            field,
            value,
            limit=limit,
            offset=offset
        )

        return {
            "total": len(results),
            "limit": limit,
            "offset": offset,
            "results": [
                {
                    "codigo": r["art_articu"].strip(),
                    "descripcion": r["art_descr1"].strip(),
                    "cambio": r.get("art_cambio", "").strip() if r.get("art_cambio") else "-",
                    "stock": r.get("art_stoalm", 0)
                }
                for r in results
            ]
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception:
        raise HTTPException(status_code=500, detail="Error interno en la búsqueda de artículos.")

@router.get("/get-article-data", dependencies=[Depends(auth_required)])
def get_articles(
    codes: str = Query(..., description="Lista de códigos separados por coma, ej: 02350-01,02351-02")
):
    """
    Obtiene los campos permitidos de varios artículos por sus códigos.
    """
    art_codes = [c.strip() for c in codes.split(",") if c.strip()]
    if not art_codes:
        raise HTTPException(status_code=400, detail="No se proporcionaron códigos de artículos.")

    try:
        results = get_articles_data(art_codes)
        return {
            "total": len(results),
            "results": results
        }
    except Exception:
        raise HTTPException(status_code=500, detail="Error interno al obtener los artículos.")
