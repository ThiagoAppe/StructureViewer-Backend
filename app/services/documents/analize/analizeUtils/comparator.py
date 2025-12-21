from typing import Dict, List, Any
from fastapi import HTTPException
from collections import Counter

from app.services.SIMReader.estructura import get_all_hijos

from ___loggin___.config import LogArea, LogCategory
from ___loggin___.logger import get_logger

logger = get_logger(LogArea.SIM, LogCategory.SIMPLANOCOMPARATOR)


def FlattenStructure(structure: list) -> List[str]:
    """
    Recibe la estructura de un artículo (lista de nodos con hijos)
    y devuelve una lista con todos los códigos (repetidos según cantidad).
    """
    codes = []

    for node in structure:
        code = node.get("codigo")
        qty = node.get("cantidad")

        try:
            qty_int = int(float(qty)) if qty not in ("", None) else 1
        except ValueError:
            logger.warning(
                f"Cantidad inválida para código {code}, usando 1 por defecto"
            )
            qty_int = 1

        codes.extend([code] * qty_int)

        if node.get("hijos"):
            codes.extend(FlattenStructure(node["hijos"]))

    logger.debug(f"Códigos aplanados con cantidades aplicadas: {codes}")
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
    logger.info(
        f"Iniciando comparación de estructura vs OCR para código principal={MainCode}"
    )

    try:
        structure_data = get_all_hijos(MainCode)

        if not structure_data:
            logger.warning(
                f"No se encontró estructura para código principal={MainCode}"
            )

        structure_list = FlattenStructure(structure_data)

        structure_counts = Counter(structure_list)
        extracted_counts = Counter(ExtractedCodes)

        logger.debug(
            f"Estructura ({len(structure_counts)} códigos): {structure_counts}"
        )
        logger.debug(
            f"OCR ({len(extracted_counts)} códigos): {extracted_counts}"
        )

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

        for code, qty in extracted_counts.items():
            if code not in structure_counts:
                extra_in_pdf[code] = qty

        report = {
            "main_code": MainCode,
            "total_in_structure": sum(structure_counts.values()),
            "total_in_pdf": sum(extracted_counts.values()),
            "matched": matched,
            "missing_in_pdf": missing_in_pdf,
            "extra_in_pdf": extra_in_pdf,
            "success": True
        }

        logger.info(
            f"Comparación finalizada para {MainCode} | "
            f"matched={len(matched)} | "
            f"missing={len(missing_in_pdf)} | "
            f"extra={len(extra_in_pdf)}"
        )

        return report

    except HTTPException:
        logger.warning(
            f"HTTPException durante comparación para código={MainCode}"
        )
        raise

    except Exception as exc:
        logger.exception(
            f"Error inesperado comparando códigos para {MainCode}"
        )
        raise HTTPException(status_code=500, detail=str(exc))
