import time
from typing import List, Dict, Any

from app.database import get_sim_db
from app.services.SIMReader.articulos import get_articles_data

from ___loggin___.logger import get_logger, LogArea, LogCategory

logger = get_logger(LogArea.SIM, LogCategory.SIMREADER)

# Máximo de hilos
MAX_THREADS = 5

def get_hijos(padre_code: str):
    padre_code_upper = padre_code.upper().strip()

    logger.debug(f"get_hijos llamado para padre_code={padre_code_upper}")

    query = f"""
    SELECT est_hijo, est_cantid, est_numord
    FROM manufact.est
    WHERE UPPER(TRIM(est_padre)) = '{padre_code_upper}'
        AND est_fechas IS NULL
    ORDER BY est_numord ASC
    """

    logger.debug(query)

    results = []
    with get_sim_db() as conn:
        cursor = conn.cursor()
        cursor.execute(query)
        columns = [col[0] for col in cursor.description]

        for row in cursor.fetchall():
            results.append(dict(zip(columns, row)))

    logger.debug(f"get_hijos devolvió {len(results)} hijos para {padre_code_upper}")

    return results

def get_padres(hijo_code: str):
    hijo_code_upper = hijo_code.upper().strip()

    logger.debug(f"get_padres llamado para hijo_code={hijo_code_upper}")

    query = f"""
    SELECT est_padre
    FROM manufact.est
    WHERE UPPER(TRIM(est_hijo)) = '{hijo_code_upper}'
        AND est_fechas IS NULL
    """

    logger.debug(query)

    results = []
    with get_sim_db() as conn:
        cursor = conn.cursor()
        cursor.execute(query)
        columns = [col[0] for col in cursor.description]

        for row in cursor.fetchall():
            results.append({columns[0]: row[0].strip() if row[0] else None})

    logger.debug(f"get_padres devolvió {len(results)} padres para {hijo_code_upper}")

    return results

def get_last_level_padres(hijo_code: str):
    hijo_code = hijo_code.strip()

    logger.debug(f"get_last_level_padres iniciado para hijo_code={hijo_code}")

    relaciones = []
    stack_fetch = [hijo_code]
    fetched = set()

    with get_sim_db() as conn:
        cursor = conn.cursor()

        while stack_fetch:
            current = stack_fetch.pop()

            if current in fetched:
                continue
            fetched.add(current)

            query = f"""
                SELECT est_padre, est_hijo
                FROM manufact.est
                WHERE est_fechas IS NULL
                    AND est_hijo = '{current}'
            """

            logger.debug(f"Buscando padres de hijo={current}")
            logger.debug(query)

            cursor.execute(query)
            rows = cursor.fetchall()
            relaciones.extend(rows)

            for padre, hijo in rows:
                if padre:
                    stack_fetch.append(padre.strip())

    logger.debug(f"Total relaciones encontradas: {len(relaciones)}")

    hijo_to_padres = {}
    for padre, hijo in relaciones:
        hijo_to_padres.setdefault(hijo.strip(), []).append(padre.strip())

    stack = [hijo_code]
    visited = set()
    last_level_parents = set()

    while stack:
        codigo = stack.pop()
        if codigo in visited:
            continue
        visited.add(codigo)

        padres = hijo_to_padres.get(codigo)
        if not padres:
            last_level_parents.add(codigo)
        else:
            stack.extend(padres)

    logger.debug(
        f"get_last_level_padres finalizado para {hijo_code}. "
        f"Niveles finales encontrados: {len(last_level_parents)}"
    )

    return list(last_level_parents)


def get_all_hijos(padre_code: str) -> List[Dict[str, Any]]:
    visited = set()
    all_codes = set()
    query_count = 0
    start_global = time.time()

    logger.debug(f"get_all_hijos iniciado para padre_code={padre_code}")

    def normalize_code(val):
        return val.strip().upper() if isinstance(val, str) else val

    def fmt_qty(val):
        if val is None:
            return ""
        try:
            num = float(val)
            return str(int(num)) if num.is_integer() else str(num)
        except (ValueError, TypeError):
            return str(val)

    def get_hijos_tree(code: str, level: int, cursor):
        nonlocal query_count

        code = normalize_code(code)

        if code in visited:
            return None

        visited.add(code)
        all_codes.add(code)

        logger.debug(f"Procesando nodo codigo={code}, level={level}")

        node = {
            "codigo": code,
            "cantidad": "",
            "descripcion": "",
            "letra_cambio": "",
            "level": level,
            "hijos": []
        }

        cursor.execute(
            """
            SELECT TRIM(est_hijo), est_cantid
            FROM manufact.est
            WHERE est_padre = ? AND est_fechas IS NULL
            """,
            (code,)
        )
        query_count += 1
        hijos_rows = cursor.fetchall()

        logger.debug(f"Encontrados {len(hijos_rows)} hijos para codigo={code}")

        for row in hijos_rows:
            hijo_code = normalize_code(row[0]) if row[0] else None
            hijo_cant = fmt_qty(row[1]) if len(row) > 1 else ""

            if hijo_code:
                child_node = get_hijos_tree(hijo_code, level + 1, cursor)
                if child_node:
                    child_node["cantidad"] = hijo_cant
                    node["hijos"].append(child_node)

        return node

    with get_sim_db() as conn:
        cursor = conn.cursor()
        tree = get_hijos_tree(padre_code, 0, cursor)

    if not tree:
        logger.debug("get_all_hijos finalizado sin resultados")
        return []

    logger.debug(
        f"Árbol generado. Códigos únicos encontrados: {len(all_codes)}, "
        f"queries ejecutadas: {query_count}"
    )

    articles_info = get_articles_data(list(all_codes))

    if isinstance(articles_info, list):
        articles_dict = {
            normalize_code(a.get("art_articu")): a
            for a in articles_info
            if a and a.get("art_articu")
        }
    else:
        articles_dict = {
            normalize_code(k): v for k, v in articles_info.items()
        }

    def enrich_tree(node):
        info = articles_dict.get(node["codigo"])
        if info:
            node["descripcion"] = (info.get("art_descr1") or "").strip()
            node["letra_cambio"] = (info.get("art_cambio") or "").strip()

        for hijo in node["hijos"]:
            enrich_tree(hijo)

    enrich_tree(tree)

    logger.debug(
        f"get_all_hijos finalizado para padre_code={padre_code}. "
        f"Tiempo total: {round(time.time() - start_global, 3)}s"
    )

    return [tree]

