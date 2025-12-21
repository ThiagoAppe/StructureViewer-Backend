from fastapi import APIRouter, Query, HTTPException, Depends
from app.services.SIMReader.estructura import (
    get_hijos,
    get_padres,
    get_last_level_padres,
    get_all_hijos
)
from app.validation import auth_required

from ___loggin___.logger import get_logger, LogArea, LogCategory

logger = get_logger(LogArea.SERVICES, LogCategory.SIMSTRUCTURE)

router = APIRouter()


@router.get("/GetHijos", dependencies=[Depends(auth_required)])
def get_structure_hijos(
    padre_code: str = Query(..., description="Código del artículo padre (est_padre)"),
):
    """
    Devuelve los artículos hijos y sus cantidades donde est_fechas es NULL
    para un artículo padre dado.
    """
    logger.debug(f"GetHijos llamado | padre_code={padre_code}")

    try:
        results = get_hijos(padre_code)

        if results:
            logger.debug(f"GetHijos OK | padre_code={padre_code} | total={len(results)}")
            logger.debug(results)
        else:
            logger.warning(f"GetHijos sin resultados | padre_code={padre_code}")

        return {
            "total": len(results),
            "results": results
        }

    except Exception as e:
        logger.exception(f"ERROR GetHijos | padre_code={padre_code}")
        raise HTTPException(
            status_code=500,
            detail="Error interno al obtener los artículos hijos."
        )


@router.get("/GetPadres", dependencies=[Depends(auth_required)])
def get_structure_padres(
    hijo_code: str = Query(..., description="Código del artículo hijo (est_hijo)"),
):
    """
    Devuelve los artículos padres donde est_fechas es NULL
    para un artículo hijo dado.
    """
    logger.debug(f"GetPadres llamado | hijo_code={hijo_code}")

    try:
        results = get_padres(hijo_code)

        if results:
            logger.debug(f"GetPadres OK | hijo_code={hijo_code} | total={len(results)}")
        else:
            logger.warning(f"GetPadres sin resultados | hijo_code={hijo_code}")

        return {
            "total": len(results),
            "results": results
        }

    except Exception as e:
        logger.exception(f"ERROR GetPadres | hijo_code={hijo_code}")
        raise HTTPException(
            status_code=500,
            detail="Error interno al obtener los artículos padres."
        )


@router.get("/GetLastLevelPadres", dependencies=[Depends(auth_required)])
def get_structure_last_level_padres(
    hijo_code: str = Query(..., description="Código del artículo hijo")
):
    """
    Devuelve únicamente los padres de último nivel (sin padres por encima)
    para un artículo hijo dado.
    """
    logger.debug(f"GetLastLevelPadres llamado | hijo_code={hijo_code}")

    try:
        results = get_last_level_padres(hijo_code)

        if results:
            logger.debug(
                f"GetLastLevelPadres OK | hijo_code={hijo_code} | total={len(results)}"
            )
        else:
            logger.warning(
                f"GetLastLevelPadres sin resultados | hijo_code={hijo_code}"
            )

        return {
            "total": len(results),
            "results": results
        }

    except Exception as e:
        logger.exception(f"ERROR GetLastLevelPadres | hijo_code={hijo_code}")
        raise HTTPException(
            status_code=500,
            detail="Error interno al obtener los padres de último nivel."
        )


@router.get("/estructura", dependencies=[Depends(auth_required)])
def get_structure_all_hijos(
    codigo: str = Query(..., description="Código del artículo padre")
):
    logger.debug(f"/estructura llamado | codigo={codigo}")

    try:
        results = get_all_hijos(codigo)

        if results:
            logger.debug(
                f"/estructura OK | codigo={codigo} | nodos_raiz={len(results)}"
            )
            logger.debug(results)
        else:
            logger.warning(
                f"/estructura sin resultados | codigo={codigo}"
            )

        return results

    except Exception as e:
        logger.exception(f"ERROR /estructura | codigo={codigo}")
        raise HTTPException(
            status_code=500,
            detail="Error interno al obtener todos los hijos."
        )
