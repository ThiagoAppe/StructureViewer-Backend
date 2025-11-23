import os
import pyodbc
import re
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from contextlib import contextmanager

# =========================
# Cargar variables de entorno
# =========================
load_dotenv()

# =========================
# Configuración MySQL (SQLAlchemy)
# =========================
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")

DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()

from app.models import department, subDepartment, user, userSubAreaPermission

def get_db():
    """
    Retorna la sesión de SQLAlchemy para MySQL.
    Usar con Depends en FastAPI o directamente.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# =========================
# Configuración Informix (pyodbc con DSN)
# =========================
@contextmanager
def get_sim_db():
    """
    Retorna una conexión activa a la base de datos Informix usando DSN.
    Se fuerza el modo de solo lectura para proteger la base de datos.
    Uso:
        with get_sim_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT ...")
            data = cursor.fetchall()
    """
    conn = None
    try:
        conn_str = (
            f"DSN={os.getenv('DB_INFORMIX_DSN', 'manufact64')};"
            f"UID={os.getenv('DB_INFORMIX_UID')};"
            f"PWD={os.getenv('DB_INFORMIX_PWD')};"
        )

        conn = pyodbc.connect(conn_str)
        yield ReadOnlyConnection(conn)

    except pyodbc.Error as e:
        print(f"❌ Error al conectar con Informix (DSN=manufact64): {e}")
        raise
    finally:
        if conn:
            conn.close()

# =========================
# Clase de conexión solo lectura
# =========================
class ReadOnlyConnection:
    """
    Envuelve una conexión de pyodbc para impedir cualquier operación de escritura.
    """
    def __init__(self, conn):
        self._conn = conn

    def cursor(self):
        return ReadOnlyCursor(self._conn.cursor())

    def close(self):
        self._conn.close()

class ReadOnlyCursor:
    """
    Cursor protegido para permitir únicamente SELECT.
    """
    WRITE_OPERATIONS = re.compile(
        r"^\s*(INSERT|UPDATE|DELETE|CREATE|DROP|ALTER|TRUNCATE|GRANT|REVOKE)",
        re.IGNORECASE,
    )

    def __init__(self, cursor):
        self._cursor = cursor

    def execute(self, query, *args, **kwargs):
        if self.WRITE_OPERATIONS.match(query):
            raise PermissionError("Operación de escritura no permitida en modo solo lectura.")
        return self._cursor.execute(query, *args, **kwargs)

    def fetchall(self):
        return self._cursor.fetchall()

    def fetchone(self):
        return self._cursor.fetchone()

    def close(self):
        self._cursor.close()
