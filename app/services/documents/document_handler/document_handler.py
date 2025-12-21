import os
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path
import glob

from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

from app.crud.userFile import create_user_file, delete_user_file
from app.models.userFile import UserFile
from app.database import SessionLocal

from ___loggin___.config import LogArea, LogCategory
from ___loggin___.logger import get_logger

logger = get_logger(LogArea.SERVICES, LogCategory.FILES)

EXPIRATION_HOURS = 24
CACHE_FOLDER_NAME = "___cache___"


async def SaveUploadedFile(file, db: Session, user_id: int) -> UserFile:
    """
    Guarda el archivo en ___cache___ con un UUID como nombre físico.
    Luego crea un registro en DB con el nombre original y el UUID.
    Devuelve el objeto UserFile creado.
    """

    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../../"))
    cache_dir = os.path.join(base_dir, CACHE_FOLDER_NAME)
    os.makedirs(cache_dir, exist_ok=True)

    file_uuid = uuid.uuid4().hex
    filename = f"{file_uuid}.pdf"
    save_path = os.path.join(cache_dir, filename)

    content = await file.read()
    with open(save_path, "wb") as f:
        f.write(content)

    user_file = create_user_file(
        db,
        user_id=user_id,
        file_name=file.filename,
        file_uuid=file_uuid,
    )

    logger.info(f"Archivo guardado en cache con uuid={file_uuid}")

    return user_file


def cleanExpiredFiles():
    """
    Elimina archivos y registros DB de archivos expirados.
    """
    db = SessionLocal()
    try:
        expiration_threshold = datetime.now(timezone.utc) - timedelta(hours=EXPIRATION_HOURS)

        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../../"))
        cache_dir = os.path.join(base_dir, CACHE_FOLDER_NAME)

        expired_files = (
            db.query(UserFile)
            .filter(UserFile.last_access < expiration_threshold)
            .all()
        )

        logger.info(f"Iniciando limpieza de {len(expired_files)} archivos expirados")

        for user_file in expired_files:
            pattern = os.path.join(cache_dir, f"{user_file.file_uuid}.*")
            files_to_delete = glob.glob(pattern)

            if not files_to_delete:
                logger.warning(f"No se encontró archivo físico para uuid={user_file.file_uuid}")
            else:
                for physical_file_path in files_to_delete:
                    try:
                        os.remove(physical_file_path)
                        logger.info(f"Archivo físico eliminado: {physical_file_path}")
                    except Exception as exc:
                        logger.error(
                            f"Error eliminando archivo físico {physical_file_path}: {exc}"
                        )

            try:
                success = delete_user_file(db, user_file.id)
                if success:
                    logger.info(f"Registro DB eliminado para file_id={user_file.id}")
                else:
                    logger.warning(f"No se pudo eliminar registro DB file_id={user_file.id}")
            except SQLAlchemyError as exc:
                logger.error(f"Error DB eliminando file_id={user_file.id}: {exc}")

        logger.info("Limpieza de archivos expirados finalizada")

    finally:
        db.close()


async def ProcessDocumentFromCache(
    uuid: str,
    db_session: Session,
    process_callback,
    delete_condition,
):
    """
    Lee un documento desde ___cache___ usando el UUID.
    - Soporta cualquier extensión.
    - Actualiza en DB la última vez que fue utilizado.
    - Ejecuta el proceso y decide si eliminar el archivo.
    """

    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../../"))
    cache_dir = os.path.join(base_dir, CACHE_FOLDER_NAME)

    matches = glob.glob(os.path.join(cache_dir, f"{uuid}.*"))

    if not matches:
        logger.warning(f"No se encontró archivo para uuid={uuid}")
        return {"success": False, "detail": "File not found for given UUID"}

    file_path = matches[0]

    try:
        file_record = (
            db_session.query(UserFile)
            .filter(UserFile.file_uuid == uuid)
            .first()
        )

        if file_record:
            file_record.last_access = datetime.now(timezone.utc)
            db_session.commit()
            logger.info(f"last_access actualizado para uuid={uuid}")

        with open(file_path, "rb") as f:
            file_bytes = f.read()

        result = await process_callback(file_bytes)

        if delete_condition(result):
            try:
                os.remove(file_path)
                logger.info(f"Archivo eliminado del cache uuid={uuid}")
            except Exception as exc:
                logger.warning(
                    f"No se pudo eliminar archivo físico uuid={uuid}: {exc}"
                )
        else:
            logger.info(f"Archivo retenido en cache uuid={uuid}")

        return result

    except Exception as exc:
        logger.exception(f"Error procesando archivo uuid={uuid}")
        return {"success": False, "detail": str(exc)}


# ---------- WATCHDOG ----------
def StartWatchdogScheduler():
    """
    Inicializa el scheduler de limpieza periódica.
    """
    scheduler = AsyncIOScheduler()
    trigger = IntervalTrigger(hours=1)
    scheduler.add_job(cleanExpiredFiles, trigger, id="file_cleanup_job")
    scheduler.start()

    logger.info("Watchdog scheduler iniciado")
    return scheduler
