import re
import json
from PIL import Image
import pytesseract
from pathlib import Path
from typing import Optional

# Ruta de tesseract (ajustar si estás en Linux o si ya está en el PATH)
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def PerformOCR(image: Image.Image, save_base_path: Optional[Path] = None) -> dict:
    """
    Extrae texto y códigos desde una imagen usando OCR.
    
    Parámetros:
    - image: objeto PIL.Image con la imagen recortada.
    - save_base_path: si se provee, se usa para guardar los resultados (sin extensión).

    Retorna:
    - dict con el texto extraído y los códigos detectados.
    """

    texto = pytesseract.image_to_string(image, lang="spa").strip()
    codigos = re.findall(r'[A-Z]*\d+(?:/\d+)?', texto.upper())

    # Guardar resultados solo si se especifica un path
    if save_base_path:
        try:
            text_file = save_base_path.with_suffix(".txt")
            json_file = save_base_path.with_suffix(".json")

            with open(text_file, "w", encoding="utf-8", errors="ignore") as f:
                f.write(texto or "[No se encontró texto]")

            with open(json_file, "w", encoding="utf-8") as f:
                json.dump(codigos or [], f, indent=4, ensure_ascii=False)

        except Exception as e:
            print(f"[PerformOCR] ⚠️ Error al guardar archivos: {e}")

    return {
        "text": texto,
        "codes": codigos or []
    }
