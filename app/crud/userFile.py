from sqlalchemy.orm import Session
from datetime import datetime, timezone
from app.models.userFile import UserFile, FileStatus

def create_user_file(db: Session, user_id: int, file_name: str, file_uuid: str) -> UserFile:
    new_file = UserFile(
        UserId=user_id,
        FileName=file_name,
        FileUuid=file_uuid,
        Status=FileStatus.pending,
        UploadDate=datetime.now(timezone.utc),
        LastAccess=datetime.now(timezone.utc),
    )
    db.add(new_file)
    db.commit()
    db.refresh(new_file)
    return new_file

def get_user_file(db: Session, file_id: int) -> UserFile | None:
    return db.query(UserFile).filter(UserFile.Id == file_id).first()

def get_user_files_by_user(db: Session, user_id: int) -> list[UserFile]:
    return db.query(UserFile).filter(UserFile.UserId == user_id).all()

def update_file_status(db: Session, file_id: int, new_status: FileStatus) -> UserFile | None:
    user_file = get_user_file(db, file_id)
    if not user_file:
        return None
    user_file.Status = new_status
    user_file.LastAccess = datetime.now(timezone.utc)
    db.commit()
    db.refresh(user_file)
    return user_file

def delete_user_file(db: Session, file_id: int) -> bool:
    user_file = get_user_file(db, file_id)
    if not user_file:
        return False
    db.delete(user_file)
    db.commit()
    return True
