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

# analyze_service.py (o donde tengas esta lógica)
from PIL import Image
from fastapi import HTTPException
import json

async def AnalyzeDocument(PdfBytes: bytes, CoordsData: dict, DbSession):
    """
    Orquesta el análisis de un PDF basado en coordenadas.
    Este método asume que el PDF ya está en memoria (bytes) y no se encarga
    de leerlo desde disco ni de borrarlo. Eso lo maneja documentHandler.
    
    Flujo:
    1. Guardar el PDF temporalmente para operaciones internas.
    2. Guardar las coordenadas como JSON temporal.
    3. Recortar la región de interés.
    4. Aplicar OCR sobre la imagen recortada.
    5. Procesar y normalizar los códigos extraídos.
    6. Retornar los resultados.
    """

    try:
        # Generar rutas temporales únicas (pero no en ___cache___)
        TempPdfPath = CACHE_DIR / "__temp_analysis__.pdf"
        TempJsonPath = CACHE_DIR / "__temp_analysis__.json"

        # Guardar PDF temporal
        with open(TempPdfPath, "wb") as f:
            f.write(PdfBytes)

        # Guardar JSON de coordenadas
        with open(TempJsonPath, "w", encoding="utf-8") as f:
            json.dump(CoordsData, f, indent=4)

        # Recortar región del PDF como imagen
        cropped_image: Image.Image = CropPDFRegion(
            TempPdfPath, CoordsData, page_number=CoordsData.get("page", 0)
        )

        # Ejecutar OCR
        ocr_result = PerformOCR(cropped_image, TempPdfPath)

        # Normalizar códigos
        codigos_normalizados = PreProcessExtractedCodes(ocr_result["codes"])

        return {
            "success": True,
            "ocr_text": ocr_result["text"],
            "raw_codes": ocr_result["codes"],
            "normalized_codes": codigos_normalizados,
            "coords": CoordsData
        }

    except HTTPException as he:
        raise he

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        for path in [TempPdfPath, TempJsonPath]:
            try:
                if path.exists():
                    path.unlink()
            except Exception as cleanup_error:
                print(f"[⚠️] No se pudo eliminar temporal {path}: {cleanup_error}")
