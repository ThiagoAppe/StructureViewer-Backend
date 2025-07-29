from enum import Enum

class NodoEstado(str, Enum):
    Normal = "Normal"
    Nuevo = "Nuevo"
    Eliminado = "Eliminado"

def CrearMapaDiferencias(differences, codigosPrincipales):
    mapa = {}

    # Inicializar todos los códigos con Normal
    for diff in differences:
        codigo = diff["codigo"]
        mapa[codigo] = NodoEstado.Normal

    # Reemplazar lo que sigue con el código que asigna presentIn y missingIn
    for diff in differences:
        codigo = diff["codigo"]
        presentIn = diff.get("presentIn", [])
        missingIn = diff.get("missingIn", [])

        mapa[codigo] = {
            "presentIn": presentIn,
            "missingIn": missingIn,
        }

    return mapa


def MarcarEstados(nodos, mapaEstado, codigoPrincipal):
    """
    Recursivamente marca el campo 'estado' en cada nodo según mapaEstado.
    - nodos: lista de nodos con estructura {codigo, hijos, ...}
    - mapaEstado: dict[codigo] -> dict con presentIn y missingIn
    - codigoPrincipal: código de la estructura actual para decidir estado
    """
    resultado = []
    for nodo in nodos:
        codigo = nodo['codigo']

        estado = "Normal"  # Por defecto

        if codigo in mapaEstado:
            entry = mapaEstado[codigo]
            if codigoPrincipal in entry["presentIn"] and codigoPrincipal not in entry["missingIn"]:
                if len(entry["missingIn"]) > 0:
                    estado = NodoEstado.Nuevo
                else:
                    estado = NodoEstado.Normal
            elif codigoPrincipal in entry["missingIn"]:
                estado = NodoEstado.Eliminado
            else:
                estado = NodoEstado.Normal
        else:
            estado = NodoEstado.Normal

        hijos = nodo.get("hijos", [])
        hijos_marcados = MarcarEstados(hijos, mapaEstado, codigoPrincipal) if hijos else []

        nodo_marcado = dict(nodo)
        nodo_marcado["estado"] = estado
        nodo_marcado["hijos"] = hijos_marcados

        resultado.append(nodo_marcado)

    return resultado

def CompareStructures(structureList: list):
    codigosPrincipales = [e["code"] for e in structureList]
    estructuras = [e["structure"] for e in structureList]

    diferencias = []

    sets = []
    for estructura in estructuras:
        codesInStructure = set()

        def CollectCodes(nodes):
            for node in nodes:
                codesInStructure.add(node["codigo"])
                hijos = node.get("hijos")
                if hijos:
                    CollectCodes(hijos)

        CollectCodes(estructura)
        sets.append(codesInStructure)

    allCodes = set.union(*sets)

    for codigo in allCodes:
        presentIn = [codigosPrincipales[i] for i, s in enumerate(sets) if codigo in s]
        missingIn = [codigosPrincipales[i] for i in range(len(codigosPrincipales)) if codigosPrincipales[i] not in presentIn]
        if len(presentIn) != len(estructuras):
            diferencias.append({
                "codigo": codigo,
                "presentIn": presentIn,
                "missingIn": missingIn
            })

    mapaEstado = CrearMapaDiferencias(diferencias, codigosPrincipales)

    estructurasMarcadas = []
    for i, estructura in enumerate(estructuras):
        codigoPrincipal = codigosPrincipales[i]
        marcada = MarcarEstados(estructura, mapaEstado, codigoPrincipal)
        estructurasMarcadas.append(marcada)

    return {
        "compared": codigosPrincipales,
        "differences": diferencias,
        "structures": estructurasMarcadas
    }
