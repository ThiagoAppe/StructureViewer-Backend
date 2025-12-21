import os
import pyodbc
import re
import time
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from contextlib import contextmanager
from ___loggin___.logger import get_logger, LogArea, LogCategory

logger = get_logger(LogArea.DATABASE, LogCategory.SYSTEM)


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
    start_time = time.perf_counter()

    try:
        conn_str = (
            f"DSN={os.getenv('DB_INFORMIX_DSN', 'manufact64')};"
            f"UID={os.getenv('DB_INFORMIX_UID')};"
            f"PWD={os.getenv('DB_INFORMIX_PWD')};"
        )

        conn = pyodbc.connect(conn_str)

        elapsed = (time.perf_counter() - start_time) * 1000
        logger.info(f"Conexión establecida a Informix en {elapsed:.2f} ms")

        yield ReadOnlyConnection(conn)

    except pyodbc.Error as e:
        logger.error(f"Error al conectar con Informix: {e}")
        raise

    finally:
        if conn:
            conn.close()
            logger.info("Conexión Informix cerrada")

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
    Delegará cualquier atributo no definido hacia el cursor real.
    """
    WRITE_OPERATIONS = re.compile(
        r"^\s*(INSERT|UPDATE|DELETE|CREATE|DROP|ALTER|TRUNCATE|GRANT|REVOKE)",
        re.IGNORECASE,
    )

    def __init__(self, cursor):
        self._cursor = cursor

    def execute(self, query, *args, **kwargs):
        start_time = time.perf_counter()

        if self.WRITE_OPERATIONS.match(query):
            logger.warning("Intento de operación prohibida detectado")
            raise PermissionError("Operación de escritura no permitida en modo solo lectura.")

        result = self._cursor.execute(query, *args, **kwargs)

        elapsed = (time.perf_counter() - start_time) * 1000
        logger.debug(f"Query ejecutada en {elapsed:.2f} ms")

        return result

    def fetchall(self):
        start = time.perf_counter()
        rows = self._cursor.fetchall()
        elapsed = (time.perf_counter() - start) * 1000
        logger.debug(f"ReadOnlyCursor completado en {elapsed:.2f} ms, filas: {len(rows)}, Devolvió:")
        for row in enumerate(rows):
            logger.debug(row)
        return rows

    def fetchone(self):
        start = time.perf_counter()
        row = self._cursor.fetchone()
        elapsed = (time.perf_counter() - start) * 1000
        logger.debug(f"fetchone completado en {elapsed:.2f} ms")
        return row

    def close(self):
        return self._cursor.close()

    def __getattr__(self, name):
        """
        Delegación automática a `_cursor` para atributos no definidos,
        incluyendo `.description`, `.rowcount`, etc.
        """
        return getattr(self._cursor, name)
