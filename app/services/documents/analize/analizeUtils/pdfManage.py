import shutil
import json
from pathlib import Path
from fastapi import UploadFile

async def SaveUploadedPDF(file: UploadFile, destination_path: Path) -> Path:
    """
    Guarda un archivo PDF subido en la carpeta 'cache' y devuelve la ruta completa.
    
    :param file: Archivo subido (UploadFile de FastAPI)
    :param destination_path: Ruta final donde se guardará el PDF (Path)
    :return: Path del PDF guardado
    """
    # Asegurarse de que la carpeta 'cache' exista
    cache_dir = destination_path.parent / "cache"
    cache_dir.mkdir(exist_ok=True)

    # Ruta final dentro de cache
    pdf_path = cache_dir / destination_path.name

    # Guardar el archivo subido
    with pdf_path.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Cerrar el archivo subido
    await file.close()

    return pdf_path


def SaveCoordsJSON(coords_data: dict, destination_path: Path) -> Path:
    """
    Guarda los datos de coordenadas en un archivo JSON en la carpeta 'cache'.
    
    :param coords_data: Diccionario con los datos de coordenadas
    :param destination_path: Ruta final donde se guardará el JSON (Path)
    :return: Path del JSON guardado
    """
    cache_dir = destination_path.parent / "cache"
    cache_dir.mkdir(exist_ok=True)

    json_path = cache_dir / destination_path.name

    with json_path.open("w", encoding="utf-8") as f:
        json.dump(coords_data, f, ensure_ascii=False, indent=4)

    return json_path
