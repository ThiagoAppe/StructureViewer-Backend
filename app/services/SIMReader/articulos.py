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

def search_articles(field: str, value: str, similar: bool = True, limit: int = 50, offset: int = 0):
    debug = False

    logger.info(f"search_articles iniciado con field='{field}', value='{value}', similar={similar}, limit={limit}, offset={offset}")

    if field not in ORDERED_FIELDS:
        logger.error(f"Campo inválido recibido en search_articles: {field}")
        raise ValueError(f"Campo '{field}' no está permitido para la búsqueda.")

    param_value = value.upper()

    if similar:
        query = f"""
            SELECT SKIP {offset} FIRST {limit}
                art_articu,
                art_descr1
            FROM manufact.art
            WHERE UPPER(TRIM({field})) LIKE '%{param_value}%'
        """
    else:
        query = f"""
            SELECT SKIP {offset} FIRST {limit}
                art_articu,
                art_descr1
            FROM manufact.art
            WHERE UPPER(TRIM({field})) = '{param_value}'
        """

    if debug:
        logger.debug("Query a ejecutar:")
        logger.debug(query)
        logger.debug(f"Valor de búsqueda: {param_value}")

    with get_sim_db() as conn:
        cursor = conn.cursor()
        cursor.execute(query)
        columns = [col[0] for col in cursor.description]
        rows = cursor.fetchall()
        results = [dict(zip(columns, row)) for row in rows]

    logger.info(f"search_articles encontró {len(results)} resultados para value='{value}' en field='{field}'")

    if results:
        logger.info("Primeros resultados obtenidos:")
        for r in results[:10]:
            logger.info(str(r))

    if debug:
        logger.debug(f"Resultados encontrados: {len(results)}")
        for r in results[:5]:
            logger.debug(str(r))

    return results

def get_articles_data(art_codes: list[str]) -> dict:
    logger.info(f"get_articles_data iniciado con {len(art_codes)} códigos recibidos")

    if not art_codes:
        logger.warning("get_articles_data llamado con lista vacía")
        return {}

    codes_upper = [code.upper().strip() for code in art_codes]
    fields_str = ", ".join(ORDERED_FIELDS)

    results = {}
    chunk_size = 1000

    with get_sim_db() as conn:
        cursor = conn.cursor()

        for i in range(0, len(codes_upper), chunk_size):
            chunk = codes_upper[i:i + chunk_size]
            placeholders = ", ".join("?" for _ in chunk)
            query = f"""
                SELECT {fields_str}
                FROM manufact.art
                WHERE UPPER(TRIM(art_articu)) IN ({placeholders})
            """

            logger.debug(f"Ejecutando chunk {i // chunk_size + 1}: {len(chunk)} códigos")
            logger.debug(query)

            cursor.execute(query, chunk)
            columns = [col[0] for col in cursor.description]
            rows = cursor.fetchall()

            if rows:
                logger.info(f"Chunk {i // chunk_size + 1} devolvió {len(rows)} filas")
                for r in rows[:10]:
                    logger.debug(str(dict(zip(columns, r))))

            for row in rows:
                result = {}
                for field in ORDERED_FIELDS:
                    value = row[columns.index(field)]
                    result[field] = value

                art_code = result["art_articu"]
                results[art_code] = result

    logger.info(f"get_articles_data finalizado. Total artículos procesados: {len(results)}")

    for k in list(results.keys())[:10]:
        logger.debug(f"{k}: {results[k]}")

    return results
