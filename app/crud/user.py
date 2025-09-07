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
    user_db = db.query(User).filter(User.id == UserId).first()
    if user_db:
        user_db.last_token = TokenId
        db.commit()
        db.refresh(user_db)
        return True
    return False

def GetLastToken(db: Session, UserId: int) -> Optional[str]:
    # Obtiene el último token guardado
    user_db = db.query(User).filter(User.id == UserId).first()
    return user_db.last_token if user_db else None

def CreateUser(db: Session, usuario: UserCreate):
    # Hashear la contraseña antes de guardar
    hashed_password = pwd_context.hash(usuario.password)

    db_user = User(
        user_name=usuario.user_name,
        email=usuario.email,
        hashed_password=hashed_password,
        department_id=usuario.department_id,
        is_active=True,
        is_superuser=False,
        last_token=None,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def ValidateUser(db: Session, username: str, password: str):
    # Valida credenciales del usuario
    user = db.query(User).filter(User.user_name == username).first()
    if not user:
        return False

    if pwd_context.verify(password, user.hashed_password):
        return user
    return False
