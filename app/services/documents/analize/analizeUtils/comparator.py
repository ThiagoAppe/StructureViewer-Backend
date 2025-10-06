from typing import Dict, List, Any
from fastapi import HTTPException
from collections import Counter
from app.services.SIMReader.estructura import GetAllHijos


def FlattenStructure(structure: list) -> List[str]:
    """
    Recibe la estructura de un artículo (lista de nodos con hijos)
    y devuelve una lista con todos los códigos (repetidos según cantidad).
    """
    codes = []
    for node in structure:
        code = node["codigo"]
        qty = node.get("cantidad")

        # Repetir el código según cantidad (si es numérica)
        try:
            qty_int = int(float(qty)) if qty not in ("", None) else 1
        except ValueError:
            qty_int = 1

        codes.extend([code] * qty_int)

        if node.get("hijos"):
            codes.extend(FlattenStructure(node["hijos"]))

    print(f"[DEBUG] Códigos con cantidades aplicadas: {codes}")
    return codes



async def CompareExtractedCodesWithStructure(
    MainCode: str,
    ExtractedCodes: List[str],
    DbSession
) -> Dict[str, Any]:
    """
    Compara los códigos y sus cantidades entre la estructura real del artículo
    y los códigos extraídos del OCR.
    """
    try:
        # Obtener estructura real desde la base
        structure_data = GetAllHijos(MainCode)

        # Aplanar la estructura para incluir todos los hijos
        structure_list = FlattenStructure(structure_data)

        # Contar ocurrencias (cantidades) de cada código
        structure_counts = Counter(structure_list)
        extracted_counts = Counter(ExtractedCodes)

        # Determinar diferencias
        missing_in_pdf = {}
        extra_in_pdf = {}
        matched = {}

        for code, qty in structure_counts.items():
            extracted_qty = extracted_counts.get(code, 0)
            if extracted_qty < qty:
                missing_in_pdf[code] = qty - extracted_qty
            elif extracted_qty > qty:
                extra_in_pdf[code] = extracted_qty - qty
            else:
                matched[code] = qty

        # También revisar códigos que solo aparecen en OCR
        for code, qty in extracted_counts.items():
            if code not in structure_counts:
                extra_in_pdf[code] = qty

        # Informe detallado
        report = {
            "main_code": MainCode,
            "total_in_structure": sum(structure_counts.values()),
            "total_in_pdf": sum(extracted_counts.values()),
            "matched": matched,
            "missing_in_pdf": missing_in_pdf,
            "extra_in_pdf": extra_in_pdf,
            "success": True
        }

        return report

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
