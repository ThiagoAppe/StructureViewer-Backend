from sqlalchemy.orm import Session

from app.services.files.files_handler import (
    read_file_from_cache,
    delete_file_from_cache,
)

from app.crud.userFile import delete_user_file
from app.models.userFile import UserFile

from ___loggin___.logger import get_logger
from ___loggin___.config import LogArea, LogCategory

logger = get_logger(LogArea.SERVICES, LogCategory.FILES)


async def process_pdf_from_cache(
    file_uuid: str,
    db_session: Session,
    process_callback,
    delete_condition,
):
    """
    Flujo específico de documentos PDF.
    """

    file_bytes = read_file_from_cache(file_uuid, db_session)

    result = await process_callback(file_bytes)

    if delete_condition(result):
        delete_file_from_cache(file_uuid)

        user_file = (
            db_session.query(UserFile)
            .filter(UserFile.file_uuid == file_uuid)
            .first()
        )

        if user_file:
            delete_user_file(db_session, user_file.id)
            logger.info(f"Archivo eliminado DB y cache file_uuid={file_uuid}")
        else:
            logger.warning(
                f"No se encontró UserFile para file_uuid={file_uuid}"
            )

    return result
