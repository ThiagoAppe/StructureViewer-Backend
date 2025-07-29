from typing import Optional
from sqlalchemy.orm import Session
from passlib.context import CryptContext

from app.models.user import User
from app.schemas.user import UserCreate

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def GetUsers(db: Session):
    # Devuelve todos los usuarios
    return db.query(User).all()

def UpdateLastToken(db: Session, UserId: int, TokenId: str) -> bool:
    # Actualiza el último token de un usuario
    UserDb = db.query(User).filter(User.Id == UserId).first()
    if UserDb:
        UserDb.LastToken = TokenId  # type: ignore
        db.commit()
        db.refresh(UserDb)
        return True
    return False

def GetLastToken(db: Session, UserId: int) -> Optional[str]:
    # Obtiene el último token guardado
    UserDb = db.query(User).filter(User.Id == UserId).first()
    return UserDb.LastToken if UserDb else None  # type: ignore

def CreateUser(db: Session, usuario: UserCreate):
    # Hashear la contraseña antes de guardar
    hashed_password = pwd_context.hash(usuario.Password)

    db_user = User(
        UserName=usuario.UserName,
        Email=usuario.Email,
        HashedPassword=hashed_password,
        DepartmentId=usuario.DepartmentId,
        IsActive=True,
        IsSuperuser=False,
        LastToken=None,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def ValidateUser(db: Session, username: str, password: str):
    # Valida credenciales del usuario
    user = db.query(User).filter(User.UserName == username).first()
    
    if not user:
        return False

    if pwd_context.verify(password, user.HashedPassword):  # type: ignore
        return user
