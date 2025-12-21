import os
import jwt
from uuid import uuid4
from dotenv import load_dotenv
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, status, Response
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.database import get_db
from app.crud.user import get_users, create_user, validate_user, update_last_token, get_last_token
from app.validation import validate_token, auth_required
from app.models.user import User

load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY")

router = APIRouter(prefix="/users", tags=["Users"])

class LoginData(BaseModel):
    user_name: str
    password: str

def generate_token(db: Session, user: User, exp_minutes: int = 600):
    """
    Genera un JWT para el usuario proporcionado.

    El token incluye:
    - id del usuario (claim "id")
    - identificador único de token (jti)
    - iat (issued at) y exp (expiración)

    También actualiza el registro `last_token` del usuario en la base de datos
    para permitir revocación / control de sesiones.

    Parámetros:
        db (Session): sesión de base de datos.
        user (User): instancia del usuario para el que se genera el token.
        exp_minutes (int): tiempo de expiración en minutos (por defecto 600).

    Retorna:
        str: JWT codificado.
    """
    now = datetime.now(timezone.utc)
    exp = now + timedelta(minutes=exp_minutes)
    jti = str(uuid4())

    payload = {
        "id": user.id,
        "jti": jti,
        "iat": int(now.timestamp()),
        "exp": int(exp.timestamp())
    }

    last_token = get_last_token(db, user.id)

    if last_token != jti:
        update_last_token(db, user.id, jti)

    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")  # type: ignore

@router.get("/me")
def get_actual_user(payload=Depends(auth_required), db: Session = Depends(get_db)):
    """
    Devuelve la información básica del usuario autenticado.

    Extrae el id del usuario desde el payload provisto por la dependencia de autenticación,
    consulta la base de datos y retorna:
    - user_name
    - roles (lista de nombres de rol)
    - permissions (lista única de permisos derivados de los roles)

    Lanza HTTPException 404 si el usuario no existe.
    """
    user_id = payload["id"]

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    roles = [role.name for role in user.roles] if user.roles else []
    permissions = []
    for role in user.roles:
        permissions.extend([perm.name for perm in role.permissions])

    return {
        "user_name": user.user_name,
        "roles": roles,
        "permissions": list(set(permissions))
    }

@router.post("/login")
def login(data: LoginData, response: Response, db: Session = Depends(get_db)):
    """
    Valida credenciales y crea una sesión.

    - Verifica las credenciales usando `validate_user`.
    - Si son correctas, genera un JWT mediante `generate_token`.
    - Devuelve una respuesta con la cookie `access_token` (httponly).

    En caso de credenciales inválidas lanza HTTP 401.
    """
    user = validate_user(db, data.user_name, data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario o contraseña incorrectos"
        )

    token = generate_token(db, user)

    res = JSONResponse(content={"message": "Login exitoso"})
    res.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=60 * 60 * 10,
        path="/"
    )
    return res

@router.post("/logout")
def logout():
    """
    Cierra la sesión del cliente eliminando la cookie `access_token`.

    Retorna un mensaje indicando que la sesión fue cerrada.
    """
    res = JSONResponse(content={"message": "Sesión cerrada"})
    res.delete_cookie(key="access_token")
    return res
