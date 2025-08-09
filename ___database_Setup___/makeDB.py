from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.database import Base
from app.models.user import User

import os
from dotenv import load_dotenv

# Cargar variables del archivo .env
load_dotenv()

# Obtener configuración de entorno
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")

# Verificación básica
if not all([DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME]):
    raise ValueError("❌ Faltan variables de entorno necesarias.")

# Crear engine sin base de datos seleccionada
engine_sin_db = create_engine(f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}")

# Crear base de datos si no existe
with engine_sin_db.connect() as conn:
    conn.execute(text(f"CREATE DATABASE IF NOT EXISTS {DB_NAME}"))
    conn.commit()

# Crear engine con base de datos
engine = create_engine(f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}")

# Crear todas las tablas definidas en los modelos
Base.metadata.create_all(bind=engine)

print("✅ Base de datos y tablas creadas correctamente.")
