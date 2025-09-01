import time
from typing import List, Dict, Any
from concurrent.futures import ThreadPoolExecutor, as_completed

from app.database import GetSIMDb
from app.services.SIMReader.articulos import GetArticlesData



# Configuración: máximo de hilos
MAX_THREADS = 5



def GetHijos(padre_code: str):
    """
    Obtiene los artículos hijos de la tabla 'est' para un artículo padre específico
    donde est_fechas sea NULL.

    :param padre_code: Código del artículo padre (est_padre)
    :return: Lista de diccionarios con est_hijo, est_cantid y est_numord
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

def GetPadres(hijo_code: str):
    """
    Obtiene los artículos padres de la tabla 'est' para un artículo hijo específico
    donde est_fechas sea NULL.

    :param hijo_code: Código del artículo hijo (est_hijo)
    :return: Lista de diccionarios con est_padre
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

def GetLastLevelPadres(hijo_code: str):
    """
    Obtiene únicamente los padres de último nivel para un artículo hijo dado,
    optimizado para no traer toda la tabla en memoria.
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
                SELECT est_padre, est_hijo
                FROM manufact.est
                WHERE est_fechas IS NULL
                  AND est_hijo = '{current}'
            """
            if debug:
                print("🔹 Query a ejecutar para:", current)
                print(query)
            
            cursor.execute(query)
            rows = cursor.fetchall()
            relaciones.extend(rows)
            
            for padre, hijo in rows:
                if padre:
                    stack_fetch.append(padre.strip())
    
    if debug:
        print(f"🔹 Total relaciones obtenidas conectadas a {hijo_code}: {len(relaciones)}")
    
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
    
    if debug:
        print(f"🔹 Padres de último nivel encontrados: {last_level_parents}")
    
    return list(last_level_parents)

def GetAllHijos(padre_code: str) -> List[Dict[str, Any]]:
    """
    Devuelve todos los hijos de un artículo en forma de árbol, compatible con GetStructure.

    Cada nodo tiene:
    - codigo
    - cantidad (desde manufact.est)
    - descripcion (desde manufact.art)
    - letra_cambio (desde manufact.art)
    - level
    - hijos (lista de nodos)

    """

    debug = True
    visited = set()
    all_codes = set()
    query_count = 0
    start_global = time.time()

    def _fmt_qty(val):
        # Normaliza cantidad a str para no romper el front si viene Decimal/None
        if val is None:
            return ""
        try:
            num = float(val)
            # Si es entero (ej. 1.000 → 1), se devuelve sin decimales
            if num.is_integer():
                return str(int(num))
            # Si no es entero (ej. 1.5 → 1.5), se mantiene el decimal
            return str(num)
        except (ValueError, TypeError):
            return str(val)

    def _get_hijos_tree(code: str, level: int, cursor):
        nonlocal query_count

        # Evitar ciclos
        if code in visited:
            if debug:
                print(f"[DEBUG] ⚠️ Ciclo detectado en {code}, se omite.")
            return None

        visited.add(code)
        all_codes.add(code)

        node = {
            "codigo": code,
            "cantidad": "",  # la cantidad se asigna en el vínculo padre->hijo
            "descripcion": "",
            "letra_cambio": "",
            "level": level,
            "hijos": []
        }

        # Medir tiempo por nodo
        start_time = time.time()

        # Traer hijos + cantidad desde manufact.est (usar columna correcta est_cantid)
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

        if debug:
            print(f"[DEBUG] Nodo {code} → {len(hijos_rows)} hijos encontrados")

        for row in hijos_rows:
            hijo_code = row[0].strip() if row[0] else None
            hijo_cant = _fmt_qty(row[1]) if len(row) > 1 else ""

            if hijo_code:
                child_node = _get_hijos_tree(hijo_code, level + 1, cursor)
                if child_node:
                    # Asignar la cantidad al hijo desde la relación en EST
                    child_node["cantidad"] = hijo_cant
                    node["hijos"].append(child_node)

                if debug:
                    print(f"[DEBUG] Padre: {code} → Hijo: {hijo_code} (cantidad={hijo_cant})")

        if debug:
            elapsed = time.time() - start_time
            print(f"[DEBUG] Tiempo nodo {code}: {elapsed:.4f} s")

        return node

    # Construcción del árbol
    with GetSIMDb() as conn:
        cursor = conn.cursor()
        tree = _get_hijos_tree(padre_code.strip(), 0, cursor)

    if not tree:
        if debug:
            print("[DEBUG] No se encontró ningún árbol para el código.")
        return []

    # Obtener datos extra (descr/letra) para todos los códigos únicos
    start_articles = time.time()
    articles_info = GetArticlesData(list(all_codes))

    # Normalizar a dict indexado por art_articu si viniera como lista
    if isinstance(articles_info, list):
        articles_dict = {
            a.get("art_articu"): a
            for a in articles_info
            if a and a.get("art_articu")
        }
    else:
        articles_dict = articles_info  # ya es dict {codigo: {...}}

    elapsed_articles = time.time() - start_articles

    # Enriquecer el árbol (NO tocar 'cantidad' acá: viene de EST)
    def _enrich_tree(node):
        info = articles_dict.get(node["codigo"])
        if info:
            node["descripcion"] = info.get("art_descr1", "") or info.get("descripcion", "")
            node["letra_cambio"] = info.get("art_cambio", "") or info.get("letra_cambio", "")

        for hijo in node["hijos"]:
            _enrich_tree(hijo)

    _enrich_tree(tree)

    elapsed_global = time.time() - start_global

    if debug:
        print("\n========== [DEBUG - RESUMEN FINAL] ==========")
        print(f"⏱️ Tiempo total: {elapsed_global:.4f} s")
        print(f"📌 Total de queries a manufact.est: {query_count}")
        print(f"📦 Total de artículos únicos encontrados: {len(all_codes)}")
        print(f"📚 Tiempo de consulta de artículos: {elapsed_articles:.4f} s")
        faltantes_descr = sum(1 for c in all_codes if not articles_dict.get(c))
        print(f"ℹ️ Artículos sin info adicional: {faltantes_descr}")
        print("============================================\n")

    return [tree]