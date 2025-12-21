import json
from pathlib import Path
from typing import List

from fastapi import APIRouter, Depends, UploadFile, File, Form
from sqlalchemy.orm import Session

from app.schemas.documents import DocumentosSchema
from ___loggin___.logger import get_logger, LogArea, LogCategory
from app.database import get_db
from app.validation import auth_required

from app.services.documents.analize.analize import AnalyzeDocument
from app.services.documents.document_handler.document_handler import (
    SaveUploadedFile,
    ProcessDocumentFromCache as process_document_from_cache,
)

logger = get_logger(LogArea.SERVICES, LogCategory.FILES)

router = APIRouter(prefix="/documents", tags=["Documents"])


@router.get("/", response_model=List[DocumentosSchema], dependencies=[Depends(auth_required)])
def get_documentos(db: Session = Depends(get_db)):
    """
    Devuelve la lista de documentos configurados desde el JSON local.
    """
    json_path = (
        Path(__file__).resolve().parent.parent / "src" / "json" / "Documentos.json"
    )

    if not json_path.exists():
        logger.warning("Archivo Documentos.json no encontrado")
        return []

    try:
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            logger.info(f"{len(data)} registros cargados desde Documentos.json")
            return data
    except Exception as exc:
        logger.error(f"Error al leer el JSON: {str(exc)}")
        return []


@router.post("/analyze", dependencies=[Depends(auth_required)])
async def analyze_pdf(
    uuid: str = Form(...),
    coords: str = Form(...),
    codigo: str = Form(...),
    db: Session = Depends(get_db),
):
    """
    Analiza un archivo desde cache utilizando su UUID.
    Elimina el archivo solo si el análisis es exitoso.
    """
    logger.info(f"Inicio de análisis de documento uuid={uuid}, codigo={codigo}")

    try:
        coords_dict = json.loads(coords)
        logger.debug(f"Coordenadas parseadas correctamente para uuid={uuid}")
    except json.JSONDecodeError as exc:
        logger.warning(
            f"Formato inválido de coordenadas para uuid={uuid}: {coords}"
        )
        return {"success": False, "detail": "Invalid coordinates format"}

    async def process_callback(file_bytes):
        logger.info(f"Ejecutando análisis para uuid={uuid}")
        result = await AnalyzeDocument(file_bytes, coords_dict, codigo, db)
        logger.info(
            f"Resultado del análisis para uuid={uuid}: success={result.get('success')}"
        )
        return result

    def delete_condition(result):
        should_delete = result.get("success", False)
        if should_delete:
            logger.info(f"El archivo uuid={uuid} será eliminado del cache")
        else:
            logger.warning(
                f"El archivo uuid={uuid} NO será eliminado del cache (análisis fallido)"
            )
        return should_delete

    try:
        response = await process_document_from_cache(
            uuid=uuid,
            db_session=db,
            process_callback=process_callback,
            delete_condition=delete_condition,
        )
        logger.info(f"Proceso completo para uuid={uuid}")
        return response
    except Exception as exc:
        logger.exception(f"Error inesperado durante el análisis de uuid={uuid}")
        raise



@router.post("/document-handler", dependencies=[Depends(auth_required)])
async def handle_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    payload: dict = Depends(auth_required),
):
    """
    Guarda un archivo subido y registra la metadata.
    """
    user_id = payload["id"]
    file_info = await SaveUploadedFile(file, db, user_id)

    filtered_info = {
        "file_name": file_info.file_name,
        "uuid": file_info.file_uuid,
    }

    return {"status": "ok", "fileinfo": filtered_info}
