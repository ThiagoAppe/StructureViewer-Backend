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
from app.schemas.user import UserCreate, UserRead
from app.crud.user import GetUsers, CreateUser, ValidateUser, UpdateLastToken, GetLastToken
from app.validation import ValidateToken, AuthRequired

load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY")

router = APIRouter(prefix="/users", tags=["Users"])

# --- Login ---
class LoginData(BaseModel):
    username: str
    password: str


def GenerateToken(db: Session, User, exp_minutes: int = 30):
    now = datetime.now(timezone.utc)
    exp = now + timedelta(minutes=exp_minutes)
    jti = str(uuid4())

    payload = {
        "id": User.Id,
        "jti": jti,
        "iat": int(now.timestamp()),
        "exp": int(exp.timestamp())
    }

    last_token = GetLastToken(db, User.Id)

    if last_token != jti:
        UpdateLastToken(db, User.Id, jti)

    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")  # type: ignore


@router.get("/me")
def GetActualUser(payload=Depends(AuthRequired)):
    return {"usuario": payload["id"]}


@router.post("/login")
def login(data: LoginData, response: Response, db: Session = Depends(GetDb)):
    user = ValidateUser(db, data.username, data.password)
    if user:
        token = GenerateToken(db, user)

        response = JSONResponse(content={"message": "Login exitoso"})
        response.set_cookie(
            key="access_token",
            value=token,
            httponly=True,
            secure=False,        # Está bien en local (sin HTTPS)
            samesite="lax",      # Compatible con `secure=False`
            max_age=60 * 60,
            path="/"
        )


        return response

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Usuario o contraseña incorrectos"
    )


@router.post("/logout", dependencies=[Depends(AuthRequired)])
def Logout(response: Response):
    response = JSONResponse(content={"message": "Sesión cerrada"})
    response.delete_cookie(key="access_token")
    return response


# --- CRUD ---
@router.get("/", response_model=list[UserRead], dependencies=[Depends(AuthRequired)])
def listar_usuarios(db: Session = Depends(GetDb)):
    return GetUsers(db)


@router.post("/", response_model=UserRead, dependencies=[Depends(AuthRequired)])
def nuevo_usuario(usuario: UserCreate, db: Session = Depends(GetDb)):
    return CreateUser(db, usuario)
