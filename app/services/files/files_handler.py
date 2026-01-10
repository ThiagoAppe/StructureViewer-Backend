import os
import uuid
import glob
from datetime import datetime, timedelta, timezone
from pathlib import Path

from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

from app.crud.userFile import create_user_file, delete_user_file
from app.models.userFile import UserFile
from app.database import SessionLocal

from ___loggin___.config import LogArea, LogCategory
from ___loggin___.logger import get_logger

from dotenv import load_dotenv

load_dotenv()

logger = get_logger(LogArea.SERVICES, LogCategory.FILES)

EXPIRATION_HOURS = float(os.getenv("FILE_EXPIRATION_HOURS"))
CLEANING_INTERVAL = float(os.getenv("CLEANING_INTERVAL"))
CACHE_FOLDER_NAME = "___cache___"


def _get_cache_dir() -> str:
    base_dir = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "../../../../")
    )
    cache_dir = os.path.join(base_dir, CACHE_FOLDER_NAME)
    os.makedirs(cache_dir, exist_ok=True)
    return cache_dir


async def save_uploaded_file(file, db: Session, user_id: int) -> UserFile:
    """
    Guarda cualquier archivo en cache usando UUID como nombre físico.
    No asume tipo, extensión ni contenido.
    """

    cache_dir = _get_cache_dir()

    file_uuid = uuid.uuid4().hex
    original_ext = Path(file.filename).suffix or ""
    physical_name = f"{file_uuid}{original_ext}"

    save_path = os.path.join(cache_dir, physical_name)

    content = await file.read()
    with open(save_path, "wb") as f:
        f.write(content)

    user_file = create_user_file(
        db,
        user_id=user_id,
        file_name=file.filename,
        file_uuid=file_uuid,
    )

    logger.info(
        f"Archivo guardado en cache uuid={file_uuid}, ext={original_ext}"
    )

    return user_file


def read_file_from_cache(file_uuid: str, db_session: Session) -> bytes:
    """
    Lee un archivo desde cache por UUID y actualiza last_access.
    """

    cache_dir = _get_cache_dir()
    matches = glob.glob(os.path.join(cache_dir, f"{file_uuid}.*"))

    if not matches:
        raise FileNotFoundError("File not found for given UUID")

    file_path = matches[0]

    file_record = (
        db_session.query(UserFile)
        .filter(UserFile.file_uuid == file_uuid)
        .first()
    )

    if file_record:
        file_record.last_access = datetime.now(timezone.utc)
        db_session.commit()

    with open(file_path, "rb") as f:
        return f.read()


def delete_file_from_cache(file_uuid: str):
    """
    Elimina archivo físico del cache.
    """

    cache_dir = _get_cache_dir()
    matches = glob.glob(os.path.join(cache_dir, f"{file_uuid}.*"))

    for file_path in matches:
        try:
            os.remove(file_path)
            logger.info(f"Archivo eliminado del cache uuid={file_uuid}")
        except Exception as exc:
            logger.warning(
                f"No se pudo eliminar archivo uuid={file_uuid}: {exc}"
            )


def clean_expired_files():
    """
    Limpia archivos expirados y sus registros DB.
    """

    db = SessionLocal()
    try:
        expiration_threshold = (
            datetime.now(timezone.utc)
            - timedelta(hours=EXPIRATION_HOURS)
        )

        expired_files = (
            db.query(UserFile)
            .filter(
                UserFile.last_access < expiration_threshold,
                UserFile.is_deleted == False,
            )
            .all()
        )

        logger.info(
            f"Iniciando limpieza de {len(expired_files)} archivos expirados"
        )

        for user_file in expired_files:
            delete_file_from_cache(user_file.file_uuid)

            try:
                delete_user_file(db, user_file.id)
            except SQLAlchemyError as exc:
                logger.error(
                    f"Error DB eliminando file_id={user_file.id}: {exc}"
                )

    finally:
        db.close()



def start_watchdog_scheduler():
    """
    Scheduler de limpieza periódica de archivos expirados.
    """

    scheduler = AsyncIOScheduler()
    scheduler.add_job(
        clean_expired_files,
        IntervalTrigger(CLEANING_INTERVAL),
        id="file_cleanup_job",
    )
    scheduler.start()

    logger.info("Watchdog scheduler iniciado")
    return scheduler
