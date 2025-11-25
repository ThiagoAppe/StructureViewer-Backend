from typing import Optional
from sqlalchemy.orm import Session
from passlib.context import CryptContext

from app.models.user import User
from app.schemas.user import UserCreate

# Logs
from ___loggin___.logger import get_category_logger
from ___loggin___.config import LogCategory

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Logger específico para usuarios (usando el enum correcto)
log = get_category_logger(LogCategory.USER)


def get_users(db: Session):
    try:
        users = db.query(User).all()
        log.info("get_users ejecutado correctamente")
        return users
    except Exception as e:
        log.error(f"Error en get_users: {e}")
        raise


def update_last_token(db: Session, user_id: int, token_id: str) -> bool:
    try:
        user_db = db.query(User).filter(User.id == user_id).first()
        if user_db:
            user_db.last_token = token_id
            db.commit()
            db.refresh(user_db)
            log.info(f"Token actualizado para user_id={user_id}")
            return True
        else:
            log.warning(f"user_id={user_id} no encontrado en update_last_token")
            return False
    except Exception as e:
        log.error(f"Error en update_last_token: {e}")
        raise


def get_last_token(db: Session, user_id: int) -> Optional[str]:
    try:
        user_db = db.query(User).filter(User.id == user_id).first()
        token = user_db.last_token if user_db else None
        log.info(f"get_last_token ejecutado para user_id={user_id}")
        return token
    except Exception as e:
        log.error(f"Error en get_last_token: {e}")
        raise


def create_user(db: Session, usuario: UserCreate):
    try:
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
        log.info(f"Usuario creado: {usuario.user_name}")
        return db_user
    except Exception as e:
        log.error(f"Error en create_user: {e}")
        raise


def validate_user(db: Session, username: str, password: str):
    try:
        user = db.query(User).filter(User.user_name == username).first()
        if not user:
            log.warning(f"Usuario no encontrado: {username}")
            return False

        if pwd_context.verify(password, user.hashed_password):
            log.info(f"Usuario validado: {username}")
            return user
        else:
            log.warning(f"Password incorrecto para usuario: {username}")
            return False
    except Exception as e:
        log.error(f"Error en validate_user: {e}")
        raise
