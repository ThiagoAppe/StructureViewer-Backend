import os
import jwt
from uuid import uuid4
from dotenv import load_dotenv
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, status, Response
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.database import GetDb
from app.crud.user import GetUsers, CreateUser, ValidateUser, UpdateLastToken, GetLastToken
from app.validation import ValidateToken, AuthRequired
from app.models.user import User

load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY")

router = APIRouter(prefix="/users", tags=["Users"])

# --- Login ---
class LoginData(BaseModel):
    user_name: str
    password: str

def GenerateToken(db: Session, User, exp_minutes: int = 120):
    now = datetime.now(timezone.utc)
    exp = now + timedelta(minutes=exp_minutes)
    jti = str(uuid4())

    payload = {
        "id": User.id,
        "jti": jti,
        "iat": int(now.timestamp()),
        "exp": int(exp.timestamp())
    }

    last_token = GetLastToken(db, User.id)

    if last_token != jti:
        UpdateLastToken(db, User.id, jti)

    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")  # type: ignore

@router.get("/me")
def GetActualUser(payload=Depends(AuthRequired), db: Session = Depends(GetDb)):
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
def login(data: LoginData, response: Response, db: Session = Depends(GetDb)):
    user = ValidateUser(db, data.user_name, data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario o contraseña incorrectos"
        )

    token = GenerateToken(db, user)

    res = JSONResponse(content={"message": "Login exitoso"})
    res.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        secure=False,   # cambiar a True en producción con HTTPS
        samesite="lax",
        max_age=60 * 60,
        path="/"
    )
    return res

@router.post("/logout")
def logout():
    res = JSONResponse(content={"message": "Sesión cerrada"})
    res.delete_cookie(key="access_token")
    return res
