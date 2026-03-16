from app.database import get_sim_db
from ___loggin___.logger import get_logger, LogArea, LogCategory

logger = get_logger(LogArea.SIM, LogCategory.SIMREADER)

ORDERED_FIELDS = [
    "art_articu",
    "art_descr1",
    "art_cambio",
    # "art_famil1",
    # "art_famil2",
    # "art_famil3",
    # "art_famil4",
    # "art_tipoar",
]


def _query_articles(query: str, params: list, cursor=None) -> list[dict]:
    """
    Ejecuta la query y devuelve una lista de diccionarios.
    Si no recibe cursor, crea su propia conexión.
    """
    own_connection = False
    results = []

    if cursor is None:
        conn_ctx = get_sim_db()
        conn = conn_ctx.__enter__()
        cursor = conn.cursor()
        own_connection = True

    try:
        cursor.execute(query, params)
        columns = [col[0] for col in cursor.description]
        rows = cursor.fetchall()
        results = [dict(zip(columns, row)) for row in rows]

    finally:
        if own_connection:
            conn_ctx.__exit__(None, None, None)

    return results


def search_articles(field: str, value: str, limit: int = 50, offset: int = 0) -> list[dict]:
    logger.info(
        f"search_articles iniciado con field='{field}', value='{value}', limit={limit}, offset={offset}"
    )

    if field not in ORDERED_FIELDS:
        raise ValueError(f"Campo '{field}' no está permitido para la búsqueda.")

    normalized = value.strip().upper()
    tokens = [t for t in normalized.split(" ") if t]

    where_clauses = []
    params = []

    for token in tokens:
        where_clauses.append(f"UPPER(TRIM({field})) LIKE ?")
        params.append(f"%{token}%")

    where_sql = " AND ".join(where_clauses)

    query = f"""
        SELECT SKIP {offset} FIRST {limit}
            art_articu,
            art_descr1,
            art_cambio,
            art_stoalm
        FROM manufact.art
        WHERE {where_sql}
        ORDER BY
            CASE
                WHEN UPPER(TRIM({field})) = ? THEN 1
                WHEN UPPER(TRIM({field})) LIKE ? THEN 2
                ELSE 3
            END,
            art_descr1
    """

    params.extend([normalized, f"{normalized}%"])

    return _query_articles(query, params)


def get_articles_data(art_codes: list[str], cursor=None) -> dict:
    logger.info(f"get_articles_data iniciado con {len(art_codes)} códigos recibidos")

    if not art_codes:
        logger.warning("get_articles_data llamado con lista vacía")
        return {}

    codes_upper = [code.strip().upper() for code in art_codes]
    fields_str = ", ".join(ORDERED_FIELDS)
    results = {}
    chunk_size = 1000

    for i in range(0, len(codes_upper), chunk_size):
        chunk = codes_upper[i:i + chunk_size]
        placeholders = ", ".join("?" for _ in chunk)

        query = f"""
            SELECT {fields_str}
            FROM manufact.art
            WHERE art_articu IN ({placeholders})
        """

        logger.debug(f"Ejecutando chunk {i // chunk_size + 1}: {len(chunk)} códigos")
        chunk_results = _query_articles(query, chunk, cursor)

        for row in chunk_results:
            results[row["art_articu"]] = row

    logger.info(f"get_articles_data finalizado. Total artículos procesados: {len(results)}")
    return results