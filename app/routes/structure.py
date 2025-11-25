from fastapi import APIRouter, Query, HTTPException, Depends
from app.services.SIMReader.estructura import get_hijos, get_padres, get_last_level_padres, get_all_hijos
from app.validation import auth_required

import logging

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/GetHijos", dependencies=[Depends(auth_required)])
def get_structure_hijos(
    padre_code: str = Query(..., description="Código del artículo padre (est_padre)"),
):
    """
    Devuelve los artículos hijos y sus cantidades donde est_fechas es NULL
    para un artículo padre dado.
    """
    try:
        results = get_hijos(padre_code)
        return {
            "total": len(results),
            "results": results
        }
    except Exception:
        raise HTTPException(status_code=500, detail="Error interno al obtener los artículos hijos.")
    
@router.get("/GetPadres", dependencies=[Depends(auth_required)])
def get_structure_padres(
    hijo_code: str = Query(..., description="Código del artículo hijo (est_hijo)"),
):
    """
    Devuelve los artículos padres donde est_fechas es NULL
    para un artículo hijo dado.
    """
    try:
        results = get_padres(hijo_code)
        return {
            "total": len(results),
            "results": results
        }
    except Exception:
        raise HTTPException(status_code=500, detail="Error interno al obtener los artículos padres.")
    
@router.get("/GetLastLevelPadres", dependencies=[Depends(auth_required)])
def get_structure_last_level_padres(
    hijo_code: str = Query(..., description="Código del artículo hijo")
):
    """
    Devuelve únicamente los padres de último nivel (sin padres por encima)
    para un artículo hijo dado.
    """
    try:
        results = get_last_level_padres(hijo_code)
        return {"total": len(results), "results": results}
    except Exception:
        raise HTTPException(status_code=500, detail="Error interno al obtener los padres de último nivel.")

@router.get("/estructura", dependencies=[Depends(auth_required)])
def get_structure_all_hijos(
    codigo: str = Query(..., description="Código del artículo padre")
):
    try:
        logger.debug(f"/estructura llamado con codigo={codigo}")

        results = get_all_hijos(codigo)

        if results:
            logger.debug(f"get_all_hijos devolvió {len(results)} nodo(s) raíz")
        else:
            logger.debug(f"get_all_hijos devolvió None o lista vacía")

        return results

    except Exception as e:
        logger.exception(f"ERROR en get_structure_all_hijos: {e}")
        raise HTTPException(status_code=500, detail=f"Error interno al obtener todos los hijos: {str(e)}")
