# prepOcr.py
from pathlib import Path
from typing import Dict
from pdf2image import convert_from_path
from PIL import Image

def CropPDFRegion(pdf_path: Path, coords_data: Dict[str, int], page_number: int = 0) -> Image.Image:
    """
    Convierte un PDF en imagen, recorta la región indicada y devuelve la imagen recortada.
    
    :param pdf_path: Path del PDF
    :param coords_data: Diccionario con las coordenadas {'x': int, 'y': int, 'width': int, 'height': int}
    :param page_number: Número de página a convertir (0-index)
    :return: Imagen recortada (PIL.Image)
    """
    if not pdf_path.exists():
        raise FileNotFoundError(f"No se encontró el archivo PDF en: {pdf_path}")

    # Convertir PDF a imagen (página específica)
    pages = convert_from_path(str(pdf_path))
    if page_number >= len(pages):
        raise ValueError(f"El PDF tiene {len(pages)} páginas, pero se pidió la página {page_number}")
    
    page_image = pages[page_number]

    # Extraer coordenadas
    x = coords_data.get("x", 0)
    y = coords_data.get("y", 0)
    width = coords_data.get("width", page_image.width - x)
    height = coords_data.get("height", page_image.height - y)

    # Recortar la imagen
    cropped_image = page_image.crop((x, y, x + width, y + height))

    return cropped_image
