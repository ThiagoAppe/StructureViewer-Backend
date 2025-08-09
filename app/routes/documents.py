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
from app.services.documents.documentHandler.documentHandler import SaveUploadedFile

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
    Ruta para analizar un PDF con coordenadas dadas. Guarda los datos en cache, 
    ejecuta el análisis en memoria, y elimina los archivos temporales al finalizar.
    """
    cache_dir = Path(__file__).resolve().parent.parent.parent / "___cache___"
    cache_dir.mkdir(parents=True, exist_ok=True)

    pdf_path = cache_dir / file.filename
    json_path = cache_dir / f"{file.filename}.json"

    try:
        pdf_bytes = await file.read()
        coords_dict = json.loads(coords)

        with open(pdf_path, "wb") as f:
            f.write(pdf_bytes)

        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(coords_dict, f, indent=4)

        result = await AnalyzeDocument(pdf_bytes, coords_dict, db)

        return {"success": True, "data": result}

    except Exception as e:
        logger.error(f"Error analyzing document: {str(e)}")
        return {"success": False, "detail": str(e)}

    finally:
        try:
            if pdf_path.exists():
                pdf_path.unlink()
            if json_path.exists():
                json_path.unlink()
        except Exception as cleanup_error:
            logger.warning(f"No se pudieron borrar archivos temporales: {str(cleanup_error)}")


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