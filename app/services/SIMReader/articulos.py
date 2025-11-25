from app.database import get_sim_db

# Campos permitidos para buscar
ORDERED_FIELDS = [
    "art_articu",
    "art_descr1",
    "art_cambio",
    "art_famil1",
    "art_famil2",
    "art_famil3",
    "art_famil4",
    "art_tipoar",
]


def search_articles(field: str, value: str, similar: bool = True, limit: int = 50, offset: int = 0):
    """
    Ejecuta una búsqueda de artículos en la tabla 'manufact.art' filtrando por un campo específico.
    
    Permite búsquedas parciales (similar=True) o exactas.  
    Devuelve únicamente el código del artículo y la descripción.  
    Retorna una lista de diccionarios:  
    [
        {"art_articu": "...", "art_descr1": "..."},
        ...
    ]
    """
    debug = False

    if field not in ORDERED_FIELDS:
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
        print("🔹 Query a ejecutar:")
        print(query)
        print("🔹 Valor de búsqueda:", param_value)

    with get_sim_db() as conn:
        cursor = conn.cursor()
        cursor.execute(query)
        columns = [col[0] for col in cursor.description]
        results = [dict(zip(columns, row)) for row in cursor.fetchall()]

    if debug:
        print("🔹 Resultados encontrados:", len(results))
        for r in results[:5]:
            print(r)

    return results


def get_articles_data(art_codes: list[str]) -> dict:
    """
    Obtiene datos completos de artículos especificados por código.
    
    Retorna un diccionario indexado por código de artículo:
    {
        "02429-01": { campo: valor, ... },
        "11624": { campo: valor, ... },
        ...
    }
    
    Realiza la consulta en chunks para evitar límites de IN (...)
    """
    debug = True

    if not art_codes:
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

            if debug:
                print(f"🔹 Ejecutando chunk {i // chunk_size + 1}: {len(chunk)} códigos")
                print(query)

            cursor.execute(query, chunk)
            columns = [col[0] for col in cursor.description]

            for row in cursor.fetchall():
                result = {}
                for field in ORDERED_FIELDS:
                    value = row[columns.index(field)]
                    result[field] = value

                art_code = result["art_articu"]
                results[art_code] = result

    return results
