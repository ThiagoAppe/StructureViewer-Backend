def normalizar_codigo(codigo: str) -> str:
    """Normaliza códigos numéricos de 4 a 5 dígitos, preserva otros formatos."""
    if codigo.isdigit() and len(codigo) == 4:
        return codigo.zfill(5)
    if "/" in codigo:
        base, sufijo = codigo.split("/", 1)
        if base.isdigit() and len(base) == 4:
            base = base.zfill(5)
        return f"{base}/{sufijo}"
    return codigo

def PreProcessExtractedCodes(raw_codes: list[str]) -> list[str]:
    """
    Aplica normalización a la lista de códigos crudos.
    Retorna una nueva lista con los códigos formateados.
    """
    return [normalizar_codigo(c) for c in raw_codes]
