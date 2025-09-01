from app.database import GetSIMDb

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

def SearchArticles(field: str, value: str, similar: bool = True, limit: int = 50, offset: int = 0):
    """
    Busca artículos en la tabla 'art' filtrando por un campo específico.
    Devuelve solo el código y la descripción.
    debug=True imprimirá la query y los parámetros.
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

    with GetSIMDb() as conn:
        cursor = conn.cursor()
        cursor.execute(query)
        columns = [col[0] for col in cursor.description]
        results = [dict(zip(columns, row)) for row in cursor.fetchall()]

    if debug:
        print("🔹 Resultados encontrados:", len(results))
        for r in results[:5]:
            print(r)

    return results


def GetArticlesData(art_codes: list[str]) -> dict:
    """
    Devuelve un diccionario con info de artículos, indexado por código.
    {
        "02429-01": { ...datos... },
        "11624": { ...datos... },
        ...
    }
    """
    debug = True

    if not art_codes:
        return {}

    codes_upper = [code.upper().strip() for code in art_codes]
    fields_str = ", ".join(ORDERED_FIELDS)

    results = {}
    chunk_size = 1000

    with GetSIMDb() as conn:
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
                    if value is not None and field in ("art_articu", "art_descr1"):
                        value = value.strip()
                    result[field] = value

                # Indexamos por código para fácil acceso
                results[result["art_articu"]] = result

    if debug:
        print(f"🔹 Total artículos obtenidos: {len(results)}")
        for k, v in list(results.items())[:5]:
            print(f"{k}: {v}")

    return results
