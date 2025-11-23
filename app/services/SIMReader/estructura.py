import time
from typing import List, Dict, Any
from concurrent.futures import ThreadPoolExecutor, as_completed

from app.database import GetSIMDb
from app.services.SIMReader.articulos import GetArticlesData


# Configuración: máximo de hilos
MAX_THREADS = 5


def get_hijos(padre_code: str):
    """
    Ejecuta una consulta sobre manufact.est para obtener los artículos hijos
    asociados a un artículo padre específico, filtrando por est_fechas IS NULL.

    Retorna una lista de diccionarios conteniendo est_hijo, est_cantid y est_numord.
    """
    debug = False

    padre_code_upper = padre_code.upper().strip()

    query = f"""
    SELECT est_hijo, est_cantid, est_numord
    FROM manufact.est
    WHERE UPPER(TRIM(est_padre)) = '{padre_code_upper}'
      AND est_fechas IS NULL
    ORDER BY est_numord ASC
    """

    if debug:
        print("🔹 Query a ejecutar:")
        print(query)

    results = []
    with GetSIMDb() as conn:
        cursor = conn.cursor()
        cursor.execute(query)
        columns = [col[0] for col in cursor.description]
        for row in cursor.fetchall():
            result = dict(zip(columns, row))
            results.append(result)

    if debug:
        print("🔹 Resultados obtenidos:", len(results))
        for r in results[:5]:
            print(r)

    return results


def get_padres(hijo_code: str):
    """
    Ejecuta una consulta sobre manufact.est para obtener los artículos padres
    asociados a un artículo hijo específico, filtrando por est_fechas IS NULL.

    Retorna una lista de diccionarios que contienen est_padre.
    """
    debug = False

    hijo_code_upper = hijo_code.upper().strip()

    query = f"""
    SELECT est_padre
    FROM manufact.est
    WHERE UPPER(TRIM(est_hijo)) = '{hijo_code_upper}'
      AND est_fechas IS NULL
    """

    if debug:
        print("🔹 Query a ejecutar:")
        print(query)

    results = []
    with GetSIMDb() as conn:
        cursor = conn.cursor()
        cursor.execute(query)
        columns = [col[0] for col in cursor.description]
        for row in cursor.fetchall():
            result = {columns[0]: row[0].strip() if row[0] else None}
            results.append(result)

    if debug:
        print("🔹 Resultados obtenidos:", len(results))
        for r in results[:5]:
            print(r)

    return results


def get_last_level_padres(hijo_code: str):
    """
    Obtiene de forma optimizada los padres de último nivel de un artículo hijo,
    evitando traer toda la tabla est en memoria y resolviendo mediante
    navegación controlada en profundidad.
    """
    debug = False
    hijo_code = hijo_code.strip()

    relaciones = []
    stack_fetch = [hijo_code]
    fetched = set()

    with GetSIMDb() as conn:
        cursor = conn.cursor()

        while stack_fetch:
            current = stack_fetch.pop()
            if current in fetched:
                continue

            fetched.add(current)

            query = f"""
            SELECT est_padre
            FROM manufact.est
            WHERE UPPER(TRIM(est_hijo)) = '{current.upper()}'
              AND est_fechas IS NULL
            """

            if debug:
                print("🔹 Query a ejecutar:")
                print(query)

            cursor.execute(query)
            rows = cursor.fetchall()

            if rows:
                for row in rows:
                    padre = row[0].strip() if row[0] else None
                    if padre:
                        relaciones.append({"hijo": current, "padre": padre})
                        stack_fetch.append(padre)

    return relaciones
