import json
from pathlib import Path
from typing import List
from fastapi import APIRouter, Depends, UploadFile, File, Form
from sqlalchemy.orm import Session

from app.schemas.documents import DocumentosSchema
from ___loggin___.loggerConfig import GetLogger
from app.database import GetDb
from app.validation import AuthRequired

from app.services.documents.analize import AnalyzeDocument
from app.services.documents.documentHandler.documentHandler import SaveUploadedFile, ProcessDocumentFromCache

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
    Uuid: str = Form(...),
    Coords: str = Form(...),
    db: Session = Depends(GetDb),
):
    """
    Analiza un archivo en ___cache___ usando su UUID.
    Borra el archivo solo si el análisis fue exitoso.
    """
    try:
        CoordsDict = json.loads(Coords)
    except json.JSONDecodeError:
        return {"success": False, "detail": "Invalid coordinates format"}

    async def ProcessCallback(FileBytes):
        return await AnalyzeDocument(FileBytes, CoordsDict, db)

    def DeleteCondition(Result):
        return Result.get("success", False)

    return await ProcessDocumentFromCache(
        Uuid=Uuid,
        DbSession=db,
        ProcessCallback=ProcessCallback,
        DeleteCondition=DeleteCondition
    )

@router.post("/DocumentHandler", dependencies=[Depends(AuthRequired)])
async def HandleDocument(
    file: UploadFile = File(...),
    db: Session = Depends(GetDb),
    payload: dict = Depends(AuthRequired),
):
    user_id = payload["id"]
    file_info = await SaveUploadedFile(file, db, user_id)

    filtered_info = {
        "FileName": file_info.FileName,
        "UUID": file_info.FileUuid,
        #"Status": file_info.Status,
    }

    return {"status": "ok", "fileinfo": filtered_info}