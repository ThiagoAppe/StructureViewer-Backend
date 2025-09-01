from fastapi import APIRouter, Query, HTTPException, Depends
from app.services.SIMReader.estructura import GetHijos, GetPadres, GetLastLevelPadres, GetAllHijos
from app.validation import AuthRequired

import logging

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/GetHijos", dependencies=[Depends(AuthRequired)])
def GetStructureHijos(
    padre_code: str = Query(..., description="Código del artículo padre (est_padre)"),
):
    """
    Devuelve los artículos hijos y sus cantidades donde est_fechas es NULL
    para un artículo padre dado.
    """
    try:
        results = GetHijos(padre_code)
        return {
            "total": len(results),
            "results": results
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error interno al obtener los artículos hijos.")
    
@router.get("/GetPadres", dependencies=[Depends(AuthRequired)])
def GetStructurePadres(
    hijo_code: str = Query(..., description="Código del artículo hijo (est_hijo)"),
):
    """
    Devuelve los artículos padres donde est_fechas es NULL
    para un artículo hijo dado.
    """
    try:
        results = GetPadres(hijo_code)
        return {
            "total": len(results),
            "results": results
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error interno al obtener los artículos padres.")
    
@router.get("/GetLastLevelPadres", dependencies=[Depends(AuthRequired)])
def GetStructureLastLevelPadres(
    hijo_code: str = Query(..., description="Código del artículo hijo")
):
    """
    Devuelve únicamente los padres de último nivel (sin padres por encima)
    para un artículo hijo dado.
    """
    try:
        results = GetLastLevelPadres(hijo_code)
        return {"total": len(results), "results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error interno al obtener los padres de último nivel.")


@router.get("/estructura", dependencies=[Depends(AuthRequired)])
def GetStructureAllHijos(
    codigo: str = Query(..., description="Código del artículo padre")
):
    try:
        logger.debug(f"/estructura llamado con codigo={codigo}")

        results = GetAllHijos(codigo)

        if results:
            logger.debug(f"GetAllHijos devolvió {len(results)} nodo(s) raíz")
        else:
            logger.debug(f"GetAllHijos devolvió None o lista vacía")

        return results

    except Exception as e:
        logger.exception(f"ERROR en GetStructureAllHijos: {e}")
        raise HTTPException(status_code=500, detail=f"Error interno al obtener todos los hijos: {str(e)}")