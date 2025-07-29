import jwt
import os
from dotenv import load_dotenv
from passlib.context import CryptContext
from datetime import datetime, timedelta

load_dotenv()

# Configuraciones
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"

# Contexto bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def generar_hash():
    password_plano = input("🔐 Ingresá la contraseña a hashear: ")
    hashed = pwd_context.hash(password_plano)
    print("✅ Hash generado:")
    print(hashed)

def decodificar_jwt():
    token = input("🔑 Ingresá el JWT: ")
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])  # type: ignore
        print("🧾 Payload decodificado:")
        for k, v in payload.items():
            if k == "exp":
                fecha = datetime.utcfromtimestamp(v)
                print(f"  {k}: {v} ({fecha} UTC)")
            else:
                print(f"  {k}: {v}")
    except jwt.ExpiredSignatureError:
        print("❌ El token ha expirado.")
    except jwt.InvalidTokenError:
        print("❌ El token no es válido.")

def generar_jwt():
    sub = input("👤 Ingresá el 'sub' (identificador del usuario, ej: admin): ")
    minutos = input("⏳ Tiempo de expiración en minutos (por defecto 10): ")
    try:
        exp_minutes = int(minutos) if minutos else 10
    except ValueError:
        exp_minutes = 10

    payload = {
        "sub": sub,
        "exp": datetime.utcnow() + timedelta(minutes=exp_minutes)
    }

    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM) # type: ignore
    print("✅ Token generado:")
    print(token)

def menu():
    print("=== Herramienta de Seguridad ===")
    print("1. Generar hash (bcrypt)")
    print("2. Decodificar JWT")
    print("3. Generar JWT")
    opcion = input("Elegí una opción (1, 2 o 3): ")

    if opcion == "1":
        generar_hash()
    elif opcion == "2":
        decodificar_jwt()
    elif opcion == "3":
        generar_jwt()
    else:
        print("Opción inválida.")

if __name__ == "__main__":
    menu()






