import os
import jwt
from fastapi import Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from dotenv import load_dotenv

from ___loggin___.logger import get_logger
from ___loggin___.config import LogArea, LogCategory

from app.database import get_db
from app.crud.user import get_last_token

logger = get_logger(LogArea.AUTH, LogCategory.AUTH)

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")

if SECRET_KEY is None:
    raise RuntimeError("SECRET_KEY no está definida en las variables de entorno.")

Err_Token = "Err_Unauthorized"


def validate_token(request: Request, db: Session = Depends(get_db)):
    """
    Valida el token JWT recibido en las cookies.
    
    Verifica:
    - Que exista un token.
    - Que el token pueda decodificarse correctamente.
    - Que contenga los campos requeridos.
    - Que coincida con el último jti registrado en base de datos.
    
    Retorna el payload decodificado si el token es válido.
    """

    #logger.debug("Entrando a ValidateToken")

    if request.method == "OPTIONS":
        #logger.debug("Solicitud OPTIONS detectada, omitiendo autenticación")
        return None

    token = request.cookies.get("access_token")
    #logger.debug(f"Token recibido de cookies: {token}")

    if not token:
        #logger.warning("No se encontró token en las cookies")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=Err_Token)

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])  # type: ignore
        user_id = payload.get("id")
        token_jti = payload.get("jti")

        if user_id is None or token_jti is None:
            #logger.error("Token inválido: falta 'id' o 'jti'")
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=Err_Token)

        #logger.debug(f"Payload decodificado correctamente: id={user_id}, jti={token_jti}")

        last_jti = get_last_token(db, user_id)
        #logger.debug(f"Último jti almacenado: {last_jti}")

        if last_jti != token_jti:
            #logger.warning("Token reemplazado o inválido")
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=Err_Token)

        #logger.info(f"Token válido para user_id={user_id}")
        return payload

    except jwt.ExpiredSignatureError:
        #logger.warning("Token expirado")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=Err_Token)

    except jwt.InvalidTokenError as e:
        #logger.error(f"Token inválido: {str(e)}")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=Err_Token)


def auth_required(payload=Depends(validate_token)):
    """
    Dependencia que asegura que el token ha sido validado correctamente.
    
    Retorna el payload validado para uso en rutas protegidas.
    """

    #logger.info(f"Validación de autenticación exitosa para usuario: {payload.get('id')}")
    return payload
