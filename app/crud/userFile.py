from sqlalchemy.orm import Session
from datetime import datetime, timezone
from app.models.userFile import UserFile, FileStatus
from ___loggin___.config import LogArea, LogCategory
from ___loggin___.logger import get_logger

log = get_logger(LogArea.CRUD, LogCategory.USER_FILE)

def create_user_file(db: Session, user_id: int, file_name: str, file_uuid: str) -> UserFile:
    try:
        new_file = UserFile(
            user_id=user_id,
            file_name=file_name,
            file_uuid=file_uuid,
            status=FileStatus.pending,
            upload_date=datetime.now(timezone.utc),
            last_access=datetime.now(timezone.utc),
            is_deleted=False,
        )
        db.add(new_file)
        db.commit()
        db.refresh(new_file)
        log.info(f"Archivo creado user_id={user_id} uuid={file_uuid}")
        return new_file
    except Exception as e:
        log.error(f"Error en create_user_file: {e}")
        raise

def get_user_file(db: Session, file_id: int) -> UserFile | None:
    try:
        file = db.query(UserFile).filter(UserFile.id == file_id, UserFile.is_deleted == False).first()
        if file:
            file.last_access = datetime.now(timezone.utc)
            db.commit()
            log.info(f"Acceso file_id={file_id}")
        return file
    except Exception as e:
        log.error(f"Error en get_user_file: {e}")
        raise

def get_user_file_by_uuid(db: Session, file_uuid: str) -> UserFile | None:
    try:
        file = db.query(UserFile).filter(UserFile.file_uuid == file_uuid, UserFile.is_deleted == False).first()
        if file:
            file.last_access = datetime.now(timezone.utc)
            db.commit()
            log.info(f"Acceso uuid={file_uuid}")
        return file
    except Exception as e:
        log.error(f"Error en get_user_file_by_uuid: {e}")
        raise

def get_user_files_by_user(db: Session, user_id: int) -> list[UserFile]:
    try:
        files = db.query(UserFile).filter(UserFile.user_id == user_id, UserFile.is_deleted == False).all()
        log.info(f"Listado user_id={user_id}")
        return files
    except Exception as e:
        log.error(f"Error en get_user_files_by_user: {e}")
        raise

def update_file_status(db: Session, file_id: int, new_status: FileStatus) -> UserFile | None:
    try:
        user_file = db.query(UserFile).filter(UserFile.id == file_id, UserFile.is_deleted == False).first()
        if not user_file:
            log.warning(f"No encontrado file_id={file_id}")
            return None

        old_status = user_file.status
        user_file.status = new_status
        user_file.last_access = datetime.now(timezone.utc)
        db.commit()
        db.refresh(user_file)

        db.execute(
            """
            INSERT INTO file_status_history (file_id, old_status, new_status, change_date)
            VALUES (:file_id, :old_status, :new_status, :change_date)
            """,
            {
                "file_id": file_id,
                "old_status": old_status.value,
                "new_status": new_status.value,
                "change_date": datetime.now(timezone.utc)
            }
        )
        db.commit()

        log.info(f"Estado cambiado file_id={file_id} {old_status} -> {new_status}")
        return user_file

    except Exception as e:
        log.error(f"Error en update_file_status: {e}")
        raise

def delete_user_file(db: Session, file_id) -> bool:
    try:
        user_file = db.query(UserFile).filter(UserFile.id == file_id, UserFile.is_deleted == False).first()
        if not user_file:
            log.warning(f"No encontrado file_id={file_id}")
            return False
        user_file.is_deleted = True
        user_file.last_access = datetime.now(timezone.utc)
        db.commit()
        log.info(f"Soft delete file_id={file_id}")
        return True
    except Exception as e:
        log.error(f"Error en delete_user_file: {e}")
        raise

def restore_user_file(db: Session, file_id: int) -> bool:
    try:
        user_file = db.query(UserFile).filter(UserFile.id == file_id, UserFile.is_deleted == True).first()
        if not user_file:
            log.warning(f"No restaurable file_id={file_id}")
            return False
        user_file.is_deleted = False
        user_file.last_access = datetime.now(timezone.utc)
        db.commit()
        log.info(f"Restaurado file_id={file_id}")
        return True
    except Exception as e:
        log.error(f"Error en restore_user_file: {e}")
        raise

def user_owns_file(db: Session, user_id: int, file_id: int) -> bool:
    try:
        file = db.query(UserFile).filter(
            UserFile.id == file_id,
            UserFile.user_id == user_id,
            UserFile.is_deleted == False
        ).first()
        result = file is not None
        log.info(f"Verificación permiso user_id={user_id} file_id={file_id} -> {result}")
        return result
    except Exception as e:
        log.error(f"Error en user_owns_file: {e}")
        raise
