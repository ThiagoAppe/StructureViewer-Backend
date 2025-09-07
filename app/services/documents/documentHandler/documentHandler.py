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
from app.models.userFile import userfile
from app.database import SessionLocal
from ___loggin___.loggerConfig import GetLogger

logger = GetLogger(name="watchdog", area="file_cleanup")

EXPIRATION_HOURS = 24
CACHE_FOLDER_NAME = "___cache___"


async def SaveUploadedFile(file, db: Session, user_id: int) -> userfile:
    """
    Guarda el archivo en ___cache___ con un UUID como nombre físico.
    Luego crea un registro en DB con el nombre original y el UUID.
    Devuelve el objeto userfile creado.
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

    return user_file


def cleanExpiredFiles():
    """
    Función que elimina archivos y registros DB de archivos expirados.
    Esta función crea su propia sesión DB.
    """
    db = SessionLocal()
    try:
        expiration_threshold = datetime.now(timezone.utc) - timedelta(hours=EXPIRATION_HOURS)

        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../../"))
        cache_dir = os.path.join(base_dir, CACHE_FOLDER_NAME)

        expired_files = (
            db.query(userfile)
            .filter(userfile.last_access < expiration_threshold)
            .all()
        )

        logger.info(f"Iniciando limpieza de {len(expired_files)} archivos expirados.")

        for user_file in expired_files:
            pattern = os.path.join(cache_dir, f"{user_file.file_uuid}.*")
            files_to_delete = glob.glob(pattern)

            if not files_to_delete:
                logger.warning(f"No physical file found to delete for UUID: {user_file.file_uuid}")
            else:
                for physical_file_path in files_to_delete:
                    try:
                        os.remove(physical_file_path)
                        logger.info(f"Archivo físico eliminado: {physical_file_path}")
                    except Exception as e:
                        logger.error(f"Error eliminando archivo físico {physical_file_path}: {e}")

            try:
                success = delete_user_file(db, user_file.Id)
                if success:
                    logger.info(f"Registro DB eliminado para archivo ID {user_file.Id}")
                else:
                    logger.warning(f"No se pudo eliminar registro DB para archivo ID {user_file.Id}")
            except SQLAlchemyError as e:
                logger.error(f"Error eliminando registro DB archivo ID {user_file.Id}: {e}")

        logger.info("Limpieza de archivos expirados finalizada.")

    finally:
        db.close()


async def ProcessDocumentFromCache(Uuid: str, DbSession, ProcessCallback, DeleteCondition):
    """
    Lee un documento desde ___cache___ usando el UUID.
    - Soporta cualquier extensión.
    - Actualiza en DB la última vez que fue utilizado.
    - Ejecuta el proceso y decide si eliminar el archivo según DeleteCondition.
    """

    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../../"))
    cache_dir = os.path.join(base_dir, CACHE_FOLDER_NAME)

    Matches = glob.glob(os.path.join(cache_dir, f"{Uuid}.*"))
    print("Uuid:", Uuid)
    if not Matches:
        logger.warning(f"No file found for UUID: {Uuid}")
        return {"success": False, "detail": "File not found for given UUID"}

    FilePath = Matches[0]

    try:
        file_record = DbSession.query(userfile).filter(userfile.file_uuid == Uuid).first()
        if file_record:
            file_record.last_access = datetime.now(timezone.utc)
            DbSession.commit()
            logger.info(f"Updated last_access for UUID {Uuid}")

        with open(FilePath, "rb") as f:
            FileBytes = f.read()

        Result = await ProcessCallback(FileBytes)

        if DeleteCondition(Result):
            try:
                os.remove(FilePath)
                logger.info(f"File deleted for UUID {Uuid}: {os.path.basename(FilePath)}")
            except Exception as e:
                logger.warning(f"Could not delete file {os.path.basename(FilePath)}: {str(e)}")
        else:
            logger.info(f"File retained for UUID {Uuid}")

        return Result

    except Exception as e:
        logger.error(f"Error processing file {os.path.basename(FilePath)}: {str(e)}")
        return {"success": False, "detail": str(e)}

#----------WATCHDOG----------
def StartWatchdogScheduler():
    """
    Inicializa y lanza el scheduler para limpieza periódica.
    Debe llamarse en startup de FastAPI.
    """
    scheduler = AsyncIOScheduler()
    trigger = IntervalTrigger(hours=1)
    scheduler.add_job(cleanExpiredFiles, trigger, id="file_cleanup_job")
    scheduler.start()
    logger.info("Watchdog scheduler iniciado para limpieza periódica de archivos.")
    return scheduler
