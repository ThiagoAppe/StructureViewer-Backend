from pathlib import Path
from typing import Dict
from pdf2image import convert_from_path
from PIL import Image

def CropPDFRegion(pdf_path: Path, coords_data: Dict[str, int], page_number: int = 0) -> Image.Image:
    """
    Convierte un PDF en imagen, recorta la región indicada y devuelve la imagen recortada.
    
    :param pdf_path: Path del PDF
    :param coords_data: Diccionario con las coordenadas {'x': float, 'y': float, 'width': float, 'height': float} normalizadas 0-1
    :param page_number: Número de página a convertir (1-index)
    :return: Imagen recortada (PIL.Image)
    """
    if not pdf_path.exists():
        raise FileNotFoundError(f"No se encontró el archivo PDF en: {pdf_path}")

    poppler_bin_path = r"C:\Tools\poppler-24.08.0\Library\bin"

    # Convertir PDF a imagen (página específica)
    pages = convert_from_path(str(pdf_path), poppler_path=poppler_bin_path)
    zero_based_page_number = page_number - 1
    if zero_based_page_number < 0 or zero_based_page_number >= len(pages):
        raise ValueError(f"El PDF tiene {len(pages)} páginas, pero se pidió la página {page_number}")

    page_image = pages[zero_based_page_number]

    # Extraer coordenadas normalizadas y convertir a pixeles
    x = int(coords_data.get("x", 0) * page_image.width)
    y = int(coords_data.get("y", 0) * page_image.height)
    width = int(coords_data.get("width", 1) * page_image.width)
    height = int(coords_data.get("height", 1) * page_image.height)

    # Ajustar para que el recorte no exceda los límites de la imagen
    right = min(page_image.width, x + width)
    bottom = min(page_image.height, y + height)

    # Recortar la imagen
    cropped_image = page_image.crop((x, y, right, bottom))

    return cropped_image
