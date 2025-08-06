import json
from pathlib import Path
from typing import List
from fastapi import APIRouter, Depends, UploadFile, File, Form
from sqlalchemy.orm import Session

from app.schemas.Documents import DocumentosSchema
from ___loggin___.loggerConfig import GetLogger
from app.database import GetDb
from app.validation import AuthRequired

from app.services.documents.analize import AnalyzeDocument

logger = GetLogger("Documents")

router = APIRouter(prefix="/Documents", tags=["Documents"])

@router.get("/", response_model=List[DocumentosSchema], dependencies=[Depends(AuthRequired)])
def GetDocumentos(db: Session = Depends(GetDb)):
    json_path = Path(__file__).resolve().parent.parent / "src" / "json" / "Documentos.json"

    if not json_path.exists():
        logger.warning("Archivo Documentos.json no encontrado")
        return []

    try:
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            logger.info(f"{len(data)} registros cargados desde Documentos.json")
            return data
    except Exception as e:
        logger.error(f"Error al leer el JSON: {str(e)}")
        return []

@router.post("/Analyze", dependencies=[Depends(AuthRequired)])
async def AnalyzePDF(
    file: UploadFile = File(...),
    coords: str = Form(...),
    db: Session = Depends(GetDb),
):
    """
    Route to analyze a PDF based on coordinates sent from the frontend.
    """
    try:
        result = await AnalyzeDocument(file, coords, db)
        return {"success": True, "data": result}
    except Exception as e:
        logger.error(f"Error analyzing document: {str(e)}")
        return {"success": False, "detail": str(e)}