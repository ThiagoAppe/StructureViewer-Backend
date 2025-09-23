from typing import Dict, List, Any
from fastapi import HTTPException
from app.services.SIMReader.estructura import GetAllHijos

def FlattenStructure(structure: list) -> set:
    """
    Recibe la estructura de un artículo (lista de nodos con hijos)
    y devuelve un set con todos los códigos de todos los niveles.
    """
    codes = set()
    for node in structure:
        codes.add(node["codigo"])
        if node.get("hijos"):
            codes.update(FlattenStructure(node["hijos"]))
    return codes

async def CompareExtractedCodesWithStructure(
    MainCode: str,
    ExtractedCodes: List[str],
    DbSession
) -> Dict[str, Any]:
    """
    Compara los códigos extraídos del OCR con la estructura real del artículo.
    """
    try:
        # Obtener estructura real desde la base
        structure_data = GetAllHijos(MainCode)

        # Aplanar la estructura para incluir todos los hijos
        structure_codes = FlattenStructure(structure_data)

        # Normalizar lista OCR
        extracted_set = set(ExtractedCodes)

        # Comparar estructuras
        missing_in_pdf = structure_codes - extracted_set  # Faltan en OCR
        extra_in_pdf = extracted_set - structure_codes    # Sobran en OCR
        matched = extracted_set & structure_codes         # Coinciden

        # Informe detallado
        report = {
            "main_code": MainCode,
            "total_in_structure": len(structure_codes),
            "total_in_pdf": len(extracted_set),
            "matched": sorted(list(matched)),
            "missing_in_pdf": sorted(list(missing_in_pdf)),
            "extra_in_pdf": sorted(list(extra_in_pdf)),
            "success": True
        }

        return report

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))