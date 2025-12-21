import re
import json
from PIL import Image
import pytesseract
from pathlib import Path
from typing import Optional

from ___loggin___.config import LogArea, LogCategory
from ___loggin___.logger import get_logger

logger = get_logger(LogArea.SIM, LogCategory.SIMOCRSCANNER)

# Ruta de tesseract (ajustar si estás en Linux o si ya está en el PATH)
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"


def PerformOCR(image: Image.Image, save_base_path: Optional[Path] = None) -> dict:
    """
    Extrae texto y códigos desde una imagen usando OCR.

    Parámetros:
    - image: objeto PIL.Image con la imagen recortada.
    - save_base_path: si se provee, se usa para guardar los resultados (sin extensión).

    Retorna:
    - dict con el texto extraído y los códigos detectados.
    """
    logger.info("Iniciando OCR sobre imagen")

    try:
        texto = pytesseract.image_to_string(image, lang="spa").strip()
        codigos = re.findall(r"[A-Z]*\d+(?:/\d+)?", texto.upper())

        if not texto:
            logger.warning("OCR no detectó texto en la imagen")

        if not codigos:
            logger.warning("OCR no detectó códigos en el texto")

        logger.debug(
            f"OCR finalizado | caracteres={len(texto)} | códigos_detectados={len(codigos)}"
        )

        if save_base_path:
            try:
                text_file = save_base_path.with_suffix(".txt")
                json_file = save_base_path.with_suffix(".json")

                with open(text_file, "w", encoding="utf-8", errors="ignore") as f:
                    f.write(texto or "[No se encontró texto]")

                with open(json_file, "w", encoding="utf-8") as f:
                    json.dump(codigos or [], f, indent=4, ensure_ascii=False)

                logger.info(
                    f"Resultados OCR guardados en {save_base_path.parent}"
                )

            except Exception as exc:
                logger.exception(
                    f"Error guardando resultados OCR en {save_base_path}"
                )

        return {
            "text": texto,
            "codes": codigos or []
        }

    except Exception as exc:
        logger.exception("Error inesperado durante OCR")
        raise
