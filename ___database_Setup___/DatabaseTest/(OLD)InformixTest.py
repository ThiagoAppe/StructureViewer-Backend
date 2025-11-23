import os
import pyodbc
from dotenv import load_dotenv

load_dotenv()

def GetInformixDb():
    """
    Retorna una conexión activa a la base de datos Informix usando pyodbc.
    Las credenciales se cargan desde .env.
    """
    try:
        ConnStr = (
            f"DRIVER={{{os.getenv('DB_INFORMIX_DRIVER')}}};"
            f"SERVER={os.getenv('DB_INFORMIX_SERVER')};"
            f"DATABASE={os.getenv('DB_INFORMIX_DATABASE')};"
            f"HOST={os.getenv('DB_INFORMIX_HOST')};"
            f"SERVICE={os.getenv('DB_INFORMIX_SERVICE')};"
            f"PROTOCOL={os.getenv('DB_INFORMIX_PROTOCOL')};"
            f"UID={os.getenv('DB_INFORMIX_UID')};"
            f"PWD={os.getenv('DB_INFORMIX_PWD')};"
        )

        Conn = pyodbc.connect(ConnStr)
        return Conn

    except Exception as e:
        print("❌ Error al conectar a Informix:", e)
        raise

def TestArticulo():
    """
    Consulta la tabla 'art' para obtener el artículo con código '02350-01'
    y muestra los datos en consola.
    """
    try:
        Conn = GetInformixDb()
        Cursor = Conn.cursor()

        Sql = "SELECT * FROM art WHERE art_articu = ?"
        CodigoArticulo = "11624"

        Cursor.execute(Sql, (CodigoArticulo,))
        Row = Cursor.fetchone()

        if Row:
            print(f"✅ Artículo encontrado ({CodigoArticulo}):")
            print(Row)
        else:
            print(f"⚠️ No se encontró el artículo con código {CodigoArticulo}.")

        Cursor.close()
        Conn.close()

    except Exception as e:
        print("❌ Error durante la consulta:", e)

if __name__ == "__main__":
    TestArticulo()
 
import os
import pyodbc
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from app.models import department, subDepartment, user, userSubAreaPermission

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
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def GetDb():
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
# Configuración Informix (pyodbc)
# =========================
def GetInformixDb():
    """
    Retorna una conexión activa a la base de datos Informix usando pyodbc.
    Las credenciales se cargan desde .env.
    """
    try:
        ConnStr = (
            f"DRIVER={{{os.getenv('INFORMIX_DRIVER')}}};"
            f"SERVER={os.getenv('INFORMIX_SERVER')};"
            f"DATABASE={os.getenv('INFORMIX_DATABASE')};"
            f"HOST={os.getenv('INFORMIX_HOST')};"
            f"SERVICE={os.getenv('INFORMIX_SERVICE')};"
            f"PROTOCOL={os.getenv('INFORMIX_PROTOCOL')};"
            f"UID={os.getenv('INFORMIX_UID')};"
            f"PWD={os.getenv('INFORMIX_PWD')};"
        )

        Conn = pyodbc.connect(ConnStr)
        return Conn

    except Exception as e:
        print("❌ Error al conectar a Informix:", e)
        raise







### import requests
from bs4 import BeautifulSoup
import re

def GetStructure(articleCode: str):
    print(f"[DEBUG] Starting GetStructure for code: {articleCode}")

    url = f"http://192.168.0.2/reportes/estructura.php?art={articleCode}&herr=1"
    try:
        response = requests.get(url)
        response.encoding = 'utf-8'
        print(f"[DEBUG] HTTP status code: {response.status_code}")
        if response.status_code != 200:
            error_msg = f"HTTP Error: {response.status_code}"
            print(f"[ERROR] {error_msg}")
            return None, error_msg
    except Exception as e:
        print(f"[EXCEPTION] requests.get error: {e}")
        return None, str(e)

    soup = BeautifulSoup(response.text, "html.parser")
    rows = soup.find_all("tr")

    structure = []
    stack = []

    codePattern = re.compile(r"^(\d+)\s*(\.*)\s*([A-Z0-9\-\/]+)", re.I)

    for idx, row in enumerate(rows):
        cells = row.find_all("td")
        if not cells or not cells[0].text.strip():
            continue

        text1 = cells[0].get_text(strip=True).upper()
        match = codePattern.match(text1)

        if match:
            level = match.group(2).count(".")
            code = match.group(3)
            quantity = cells[1].get_text(strip=True) if len(cells) > 1 else ""
            description = cells[2].get_text(strip=True) if len(cells) > 2 else ""

            # Usar nombres de clave compatibles con el renderizador React
            node = {
                "codigo": code,
                "cantidad": quantity,
                "descripcion": description,
                "level": level,
                "hijos": []
            }

            while stack and stack[-1]["level"] >= level:
                stack.pop()

            if stack:
                stack[-1]["hijos"].append(node)
            else:
                structure.append(node)

            stack.append(node)
        else:
            print(f"[DEBUG] Row {idx} with text '{text1}' did not match pattern")

    # Validación para artículos vacíos
    if (
        len(structure) == 1 and
        structure[0]["codigo"] == articleCode and
        not structure[0]["descripcion"].strip()
    ):
        return None, "Code does not exist"

    return structure, None

    # art_descr1 char(40) not null, DESCRIPCION (1) 
    # art_tipoar char(2) not null, TIPO DE ARTICULO (1)
    # art_tipint char(1) not null, TIPO INTERNO DE ARTICULO (1)
    # art_artven char(1) not null, MARCA ARTICULO VENDIBLE (1)
    # art_uminte char(2) not null, UNIDAD DE MEDIDA INTERNA (1)
    # art_desadi char(1) not null,       MARCA DE DESCRIPCION ADICIONAL (1)
    # art_umcomp char(2),       UNIDAD DE MEDIDA DE COMPRAS (2)
    # art_coefco decimal(9,2),  COEFICIENTE DE CONVERSION UMC/UMI (2)
    # art_calcco char(1),    COD. DE CALCULO (MUL o DIV COEF. DE CONVERSION) (2)
    # art_umvent char(2),       UNIDAD DE MEDIDA DE VENTA (1)
    # art_coefve decimal(9,2),  COEFICIENTE DE CONVERSION UMV/UMI (1)
    # art_calcve char(1),     COD. DE CALCULO (MUL o DIV COEF. DE CONVERSION) (1)
    # art_pesoar decimal(9,4),  PESO DEL ARTICULO (1)
    # art_volume decimal(7,2),  VOLUMEN DEL ARTICULO (1)
    # art_tiempo decimal(9,4),  CONTENIDO DE MANO DE OBRA (MIN) (1)
    # art_tieacu decimal(10,4), ACUMULADO DE MANO DE OBRA/MAQUINA (MIN) (5)
    # art_plano char(15),       CODIGO DEL PLANO (1)
    # art_sustit char(15),      ARTICULO SUSTITUTO (1)
    # art_tpacam char(1) not null,
    # art_cambio char(4),       CAMBIO DE INGENIERIA VIGENTE (1)
    # art_camfec date,          FECHA DEL ULTIMO CAMBIO DE INGENIERIA (1)
    # art_codcon char(6),       CODIGO DE CONTENEDOR (1)
    # art_cancon decimal(10,2),       CANTIDAD DE ARTICULOS POR CONTENEDOR (1)
    # art_nrocon smallint,      CANTIDAD DE TARJETAS KAN-BAN (3)
    # art_ccprim char(4),       CENTRO DE COSTO PRINCIPAL (1)
    # art_provee char(7),       PROVEEDOR PRINCIPAL (2)
    # art_artpro char(15),      COD. ARTICULO DEL PROVEEDOR (2)
    # art_marca char(15),       MARCA COMERCIAL DEL ARTICULO (2)
    # art_tippro	char(1),       TIPO DE PROGRAMACION (3) 
    # art_polord char(1),       POLITICA DE ORDENES (3) 
    # art_diagru smallint,      DIAS DE AGRUPAMIENTO (3)
    # art_apepn0     char(3)         TIPO APERTURA A PRONOSITICO DE VENTAS.
    # art_direct char(1),       TIPO DE DIRECTIZACION (2)
    # art_tipcon char(1),       TIPO DE CONSUMO (3)
    # art_scrap decimal(4,2),   SCRAP O MERMA STANDARD (1)
    # art_punrep decimal(10,2), PUNTO DE REPOSICION (3)
    # art_calrep char(1), MARCA TIPO DE CALCULO DEL PUNTO DE REPOSICION (3)
    # art_ordmin decimal(10,2), TAMANIO MINIMO DE UNA ORDEN (2) (3)
    # art_ordmul decimal(10,2), CANTIDAD MULTIPLO DE UNA ORDEN (2) (3)
    # art_ordfij decimal(10,2), TAMANIO FIJO DE LAS ORDENES (2) (3)
    # art_ordmax decimal(10,2), TAMANIO MAXIMO DE UNA ORDEN (2) (3)
    # art_stoalm decimal(10,2), STOCK EN ALMACENES CONSOLIDADO (5)
    # art_stores decimal(10,2), STOCK RESERVADO CONSOLIDADO (5)
    # art_stopro decimal(10,2), STOCK EN PROCESO PARA ORD.FABRIC. (5)
    # art_stocal decimal(10,2), CANTIDAD EN CONTROL DE CALIDAD (5)
    # art_stoflu decimal(10,2), STOCK EN PROCESO POR FLUJO (5)
    # art_stompt decimal(10,2),  STOCK EN PODER DE TERCEROS (5)
    # art_pingre decimal(10,2),  CANTIDAD PENDIENTE DE INGRESO (5)
    # art_planta char(2),        PLANTA DE FABRICACION (3)
    # art_report char(1),    MARCA DE PRODUCCION REPORTABLE  (3)
    # art_celpro char(5)     CELDA DE PRODUCCION (3)
    # art_plazof smallint,       PLAZO DE ENTREGA FIJO (DIAS) (2) (3)
    # art_plazov decimal(7,3),   PLAZO DE ENTREGA UNITARIO (MIN) (2) (3)
    # art_plazoc smallint,      PLAZO DE CONTROL DE CALIDAD DIAS HABILES (2) (3)
    # art_plazop decimal(5,2),  PLAZO DE ENTREGA PROMEDIO (DIAS) (2) (3)
    # art_progra char(4),       PROGRAMADOR (2) (3)
    # art_abcsto char(1),       MARCA ABC STOCK (5)
    # art_fabcst date,          FECHA MARCA ABC STOCK (5)
    # art_abccoh char(1),       MARCA ABC CONSUMO HISTORICO (5)
    # art_fabcch date,          FECHA MARCA ABC CONSUMO HISTORICO (5)
    # art_abccof char(1),       MARCA ABC CONSUMO FUTURO (5)
    # art_fabccf date,          FECHA MARCA ABC CONSUMO FUTURO (5)
    # art_loteop decimal(10,2), LOTE OPTIMO (2) (3)
    # art_lotepr decimal(10,2), LOTE PROMEDIO (2) (3)
    # art_lotest decimal(10,2), LOTE ESTANDAR (4)
    # art_conmac decimal(10,2), CONSUMO MES ACTUAL (5)
    # art_conman decimal(10,2),  CONSUMO MES ANTERIOR (5)
    # art_conmhi decimal(10,2),  CONSUMO MES HISTORICO (5)  
    # art_conmfu decimal(10,2),  CONSUMO MES FUTURO (5)
    # art_confec date,          ULTIMA FECHA DE CONSUMO (5)
    # art_fabran decimal(10,2),  FABRICADO MES ANTERIOR (5)
    # art_fabrac decimal(10,2), FABRICADO MES ACTUAL (5)
    # art_fabrmm decimal(10,2),   FABRICADO MES HISTORICO (5)
    # art_fabfec date,          ULTIMA FECHA DE FABRICACION (5)
    # art_compan decimal(10,2), COMPRADO MES ANTERIOR (5)
    # art_compac decimal(10,2), COMPRADO MES ACTUAL (5)
    # art_compmm decimal(10,2),  COMPRADO MES HISTORICO (5)
    # art_comfec date,          ULTIMA FECHA DE COMPRA (5)
    # art_ultprv char(7),       PROVEEDOR DE LA ULTIMA COMPRA (5)
    # art_ultpre money(16,4),   PRECIO DE LA ULTIMA COMPRA (5)
    # art_lowlev smallint not null,      NIVEL MAS BAJO EN ESTRUCTURA (1)
    # art_marimp char(1),                MARCA DE IMPORTADO O NO
    # art_oriafo char(2),                ORIGEN DE AFORO (4)
    # art_gruafo char(2),                GRUPO DE AFORO (4)
    # art_stkneg char(1) not null,       PERMITE STOCK NEGATIVO (Backflushing)
    # art_ctrlot char(1) not null,       USO EXCLUSIVO DE FUNC. DE TRAZABILIDAD
    # art_canmax decimal(10,2) not null, USO EXCLUSIVO DE FUNC. DE TRAZABILIDAD
    # art_diasvu smallint not null,      USO EXCLUSIVO DE FUNC. DE TRAZABILIDAD
    # art_diasrt smallint not null,      USO EXCLUSIVO DE FUNC. DE TRAZABILIDAD
    # art_feclot date,                   USO EXCLUSIVO DE FUNC. DE TRAZABILIDAD
    # art_codlot char(1) not null,       USO EXCLUSIVO DE FUNC. DE TRAZABILIDAD
    # art_refart char(15)    CODIGO DEL ARTICULO "REFERENCIAL"
    # art_refprx char(1) not null,     MARCA TOMA PROXIMO NRO. DE LOTE del 
    # art_refprf char(1) not null,     MARCA TOMA PREFIJO NRO. DE LOTE del 
    # art_refsuf char(1) not null,     MARCA TOMA SUFIJO NRO. DE LOTE del 
    # art_prxlot integer not null,       USO EXCLUSIVO DE FUNC. DE TRAZABILIDAD
    # art_tammas smallint not null,      TAMANIO DE MASCARA DEL NRO. SERIE/LOTE
    # art_prfijo char(15)                PREFIJO del NRO. DE SERIE/LOTE
    # art_sufijo char(15)                SUFIJO del NRO. DE SERIE/LOTE
    # art_sugcns char(1) not null,       USO EXCLUSIVO DE FUNC. DE TRAZABILIDAD
    # art_tiptrz char(1) not null,       USO EXCLUSIVO DE FUNC. DE TRAZABILIDAD
    # art_mezcla char(1) not null,       USO EXCLUSIVO DE FUNC. DE TRAZABILIDAD
    # art_tipres char(1) not null,       USO EXCLUSIVO DE FUNC. DE TRAZABILIDAD
    # art_usasug char(1) not null,       USA SUGERENCIAS DE CAMBIO DE FECHAS
    # art_cargae char(1) not null,       PARAMETROS DE CARGA AUTOMATICA DE AEs
    # art_txtet1 char(5) 		  CODIGO DE CLIENTE P/ IMPRESION ETIQUETAS
    # art_txtet2 char(10)		  BREVE DESCRIPCION P/ IMPRESION DE ETIQUETAS
    # art_malog1 char(14) not null, NOMBRE ULT. MANTENIMIENTO DATOS INGEN. (5)
    # art_mafec1 date not null,     FECHA   "         "         "     "    (5)
    # art_malog2 char(14), NOMBRE (LOGIN) ULT. MANTENIMIENTO DATOS COMPRA (5)
    # art_mafec2 date,     FECHA           "         "         "      "   (5) 
    # art_malog3 char(14), NOMBRE (LOGIN) ULT. MANTENIMIENTO DATOS PLANIF. (5)
    # art_mafec3 date,     FECHA           "         "         "       "   (5)
    # art_malog6 char(14), NOMBRE (LOGIN) ULT. MANTENIMIENTO
    # art_mafec6 date      FECHA           "         "