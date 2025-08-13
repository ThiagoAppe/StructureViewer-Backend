import pyodbc

def get_informix_connection():
    # Conexión usando DSN configurado
    conn = pyodbc.connect(
        "DSN=manufact64"
    )
    return conn

def test_connection():
    try:
        conn = get_informix_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT FIRST 1 * FROM systables")  # Consulta simple de prueba
        row = cursor.fetchone()
        print("Conexión exitosa. Primer registro:", row)
        cursor.close()
        conn.close()
    except Exception as e:
        print("Error al conectar a Informix:", e)

if __name__ == "__main__":
    test_connection()
