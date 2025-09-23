from sqlalchemy.orm import Session
from datetime import datetime, timezone
from app.models.userFile import userfile, FileStatus

def create_user_file(db: Session, user_id: int, file_name: str, file_uuid: str) -> userfile:
    new_file = userfile(
        user_id=user_id,
        file_name=file_name,
        file_uuid=file_uuid,
        status=FileStatus.pending,
        upload_date=datetime.now(timezone.utc),
        last_access=datetime.now(timezone.utc),
    )
    db.add(new_file)
    db.commit()
    db.refresh(new_file)
    return new_file

def get_user_file(db: Session, file_id: int) -> userfile | None:
    return db.query(userfile).filter(userfile.id == file_id).first()

def get_user_files_by_user(db: Session, user_id: int) -> list[userfile]:
    return db.query(userfile).filter(userfile.user_id == user_id).all()

def update_file_status(db: Session, file_id: int, new_status: FileStatus) -> userfile | None:
    user_file = get_user_file(db, file_id)
    if not user_file:
        return None
    user_file.status = new_status
    user_file.last_access = datetime.now(timezone.utc)
    db.commit()
    db.refresh(user_file)
    return user_file

def delete_user_file(db: Session, file_id) -> bool:
    user_file = get_user_file(db, file_id)
    if not user_file:
        return False
    db.delete(user_file)
    db.commit()
    return True
