import json
import uuid
from pathlib import Path
from fastapi import HTTPException
from typing import Annotated
from sqlalchemy.orm import Session
from PIL import Image

from app.services.documents.analize.analizeUtils.ocr import PerformOCR
from app.services.documents.analize.analizeUtils.preProcessor import PreProcessExtractedCodes
from app.services.documents.analize.analizeUtils.pdfManage import SaveUploadedPDF, SaveCoordsJSON
from app.services.documents.analize.analizeUtils.prepOCR import CropPDFRegion
from app.services.documents.analize.analizeUtils.comparator import CompareExtractedCodesWithStructure

CACHE_DIR = Path(__file__).resolve().parents[2] / "___cache___"
CACHE_DIR.mkdir(parents=True, exist_ok=True)


async def AnalyzeDocument(PdfBytes: bytes, CoordsData: dict, Codigo: str, DbSession):
    """
    Orquesta el análisis de un PDF basado en coordenadas.
    """

    try:
        if not isinstance(CoordsData, list):
            raise HTTPException(
                status_code=400,
                detail="CoordsData debe ser una lista de coordenadas"
            )

        AnalysisId = uuid.uuid4().hex
        DebugDir = CACHE_DIR / "debug_crops" / AnalysisId
        DebugDir.mkdir(parents=True, exist_ok=True)

        TempPdfPath = CACHE_DIR / "__temp_analysis__.pdf"

        with open(TempPdfPath, "wb") as f:
            f.write(PdfBytes)

        all_text = []
        all_raw_codes = []

        for idx, coord in enumerate(CoordsData):

            if not isinstance(coord, dict):
                continue

            page_number = coord.get("page", 0)

            cropped_image: Image.Image = CropPDFRegion(
                TempPdfPath,
                coord,
                page_number=page_number
            )

            # -------- DEBUG: guardar recorte --------
            DebugImagePath = DebugDir / f"crop_page_{page_number}_idx_{idx}.png"
            cropped_image.save(DebugImagePath)
            # ----------------------------------------

            ocr_result = PerformOCR(cropped_image, TempPdfPath)

            # -------- DEBUG: guardar resultado OCR --------
            DebugTextPath = DebugDir / f"crop_page_{page_number}_idx_{idx}.txt"
            with open(DebugTextPath, "w", encoding="utf-8") as txt_file:
                txt_file.write(ocr_result.get("text", ""))
            # ----------------------------------------------

            all_text.append(ocr_result.get("text", ""))
            all_raw_codes.extend(ocr_result.get("codes", []))

        codigos_normalizados = PreProcessExtractedCodes(all_raw_codes)

        report = await CompareExtractedCodesWithStructure(
            MainCode=Codigo,
            ExtractedCodes=codigos_normalizados,
            DbSession=DbSession
        )

        return {
            "success": True,
            "analysis_id": AnalysisId,
            "debug_path": str(DebugDir),
            "ocr_text": "\n".join(all_text),
            "raw_codes": all_raw_codes,
            "normalized_codes": codigos_normalizados,
            "coords": CoordsData,
            "comparison_report": report
        }

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        try:
            if TempPdfPath.exists():
                TempPdfPath.unlink()
        except Exception as cleanup_error:
            print(f"[⚠️] No se pudo eliminar temporal {TempPdfPath}: {cleanup_error}")
