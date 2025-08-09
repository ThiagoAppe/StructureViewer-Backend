import json
import uuid
from pathlib import Path
from fastapi import UploadFile, Form, File, HTTPException
from typing import Annotated
from sqlalchemy.orm import Session
from PIL import Image

from app.services.documents.analizeUtils.ocr import PerformOCR
from app.services.documents.analizeUtils.preProcessor import PreProcessExtractedCodes
from app.services.documents.analizeUtils.pdfManage import SaveUploadedPDF, SaveCoordsJSON
from app.services.documents.analizeUtils.prepOCR import CropPDFRegion

CACHE_DIR = Path(__file__).resolve().parents[2] / "___cache___"
CACHE_DIR.mkdir(parents=True, exist_ok=True)

async def AnalyzeDocument(
    coords: Annotated[bytes, Form()],
    db: Session,
    file: UploadFile = File(...)
):
    """
    Orquesta el análisis de un PDF basado en coordenadas.
    1. Guarda el PDF subido.
    2. Guarda las coordenadas como JSON.
    3. Recorta la región de interés.
    4. Aplica OCR sobre la imagen recortada.
    5. Procesa y normaliza los códigos extraídos.
    6. Limpia archivos temporales.
    7. Devuelve los resultados.
    """

    unique_id = str(uuid.uuid4())
    base_path = CACHE_DIR / unique_id

    try:
        # Decodificar coords de bytes a str
        try:
            coords_str = coords.decode("utf-8")
        except UnicodeDecodeError:
            raise HTTPException(
                status_code=400,
                detail="Error de codificación en 'coords' (no es UTF-8 válido)."
            )

        # Parsear JSON
        try:
            coords_data = json.loads(coords_str)
        except json.JSONDecodeError:
            raise HTTPException(
                status_code=400,
                detail="Formato de coordenadas no soportado. Debe ser JSON válido."
            )

        # Guardar PDF en cache
        pdf_path = await SaveUploadedPDF(file, base_path.with_suffix(".pdf"))

        # Guardar JSON de coordenadas
        SaveCoordsJSON(coords_data, base_path.with_suffix(".json"))

        # Recortar región del PDF como imagen
        cropped_image: Image.Image = CropPDFRegion(
            pdf_path, coords_data, page_number=coords_data.get("page", 0)
        )

        # Ejecutar OCR
        ocr_result = PerformOCR(cropped_image, base_path)

        # Normalizar códigos
        codigos_normalizados = PreProcessExtractedCodes(ocr_result["codes"])

        return {
            "success": True,
            "ocr_text": ocr_result["text"],
            "raw_codes": ocr_result["codes"],
            "normalized_codes": codigos_normalizados,
            "coords": coords_data,
            "filename": pdf_path.name
        }

    except HTTPException as he:
        raise he

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        # Eliminar todos los archivos relacionados
        for ext in [".pdf", ".json", ".png", ".txt"]:
            try:
                temp_file = base_path.with_suffix(ext)
                if temp_file.exists():
                    temp_file.unlink()
            except Exception as e:
                print(f"[⚠️] No se pudo eliminar archivo temporal {temp_file}: {e}")
