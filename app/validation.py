import os
import jwt
from fastapi import Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from dotenv import load_dotenv

from ___loggin___.loggerConfig import GetLogger
from app.database import GetDb
from app.crud.user import GetLastToken

logger = GetLogger("auth")

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")

if SECRET_KEY is None:
    raise RuntimeError("SECRET_KEY no está definida en las variables de entorno.")

Err_Token = "Err_Unauthorized"

def ValidateToken(request: Request, db: Session = Depends(GetDb)):
    if request.method == "OPTIONS":
        return None

    token = request.cookies.get("access_token")
    #print("Token en Validate", token)
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=Err_Token)

    #print("Token recibido en cookie:", token)

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])  # type: ignore
        # resto de la validación ...
        user_id = payload.get("id")
        token_jti = payload.get("jti")
        if user_id is None or token_jti is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=Err_Token)

        last_jti = GetLastToken(db, user_id)
        if last_jti != token_jti:
            logger.warning("Token reemplazado o inválido")
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=Err_Token)

        return payload

    except jwt.ExpiredSignatureError:
        logger.warning("Token expirado")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=Err_Token)

    except jwt.InvalidTokenError:
        logger.error("Token inválido")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=Err_Token)

def AuthRequired(payload=Depends(ValidateToken)):
    return payload
