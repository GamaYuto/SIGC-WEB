# app/db_connection.py
import ibm_db
import os
import base64

def get_db_connection():
    """
    Establece una conexión con la base de datos Informix.
    """
    database = os.getenv("INFORMIX_DATABASE")
    hostname = os.getenv("INFORMIX_HOST")
    port = os.getenv("INFORMIX_PORT")
    uid = os.getenv("INFORMIX_USER")
    pwd = os.getenv("INFORMIX_PASSWORD")
    
    conn_str = (
        f"DATABASE={database};"
        f"HOSTNAME={hostname};"
        f"PORT={port};"
        f"PROTOCOL=TCPIP;"
        f"UID={uid};"
        f"PWD={pwd};"
    )

    try:
        conn = ibm_db.connect(conn_str, "", "")
        print("¡Conexión a la base de datos Informix exitosa!")
        return conn
        
    except Exception as e:
        print(f"Error al conectar a la base de datos: {e}")
        return None

def close_db_connection(conn):
    """
    Cierra la conexión a la base de datos si está abierta.
    """
    if conn:
        ibm_db.close(conn)
        print("Conexión a la base de datos cerrada.")

def execute_select(sql_query):
    """
    Ejecuta una consulta SELECT y devuelve el primer resultado.
    """
    conn = get_db_connection()
    result = None
    if conn:
        try:
            stmt = ibm_db.exec_immediate(conn, sql_query)
            data = ibm_db.fetch_tuple(stmt)
            if data:
                result = data[0]
        except Exception as e:
            print(f"Error al ejecutar la consulta: {e}")
        finally:
            close_db_connection(conn)
    return result

def execute_select_all(sql_query):
    """
    Ejecuta una consulta SELECT y devuelve todos los resultados como una lista de tuplas.
    """
    conn = get_db_connection()
    results = []
    if conn:
        try:
            stmt = ibm_db.exec_immediate(conn, sql_query)
            row = ibm_db.fetch_tuple(stmt)
            while row:
                results.append(row)
                row = ibm_db.fetch_tuple(stmt)
        except Exception as e:
            print(f"Error al ejecutar la consulta: {e}")
        finally:
            close_db_connection(conn)
    return results

def num_to_letters(num):
    """
    Convierte un número a su representación en letras (simplificado).
    """
    unidades = ['', 'un', 'dos', 'tres', 'cuatro', 'cinco', 'seis', 'siete', 'ocho', 'nueve']
    decenas = ['', 'diez', 'veinte', 'treinta', 'cuarenta', 'cincuenta', 'sesenta', 'setenta', 'ochenta', 'noventa']
    especiales = ['diez', 'once', 'doce', 'trece', 'catorce', 'quince', 'dieciséis', 'diecisiete', 'dieciocho', 'diecinueve']

    if num < 10:
        return unidades[num]
    elif num < 20:
        return especiales[num - 10]
    elif num < 100:
        if num % 10 == 0:
            return decenas[num // 10]
        else:
            return decenas[num // 10] + ' y ' + unidades[num % 10]
    else:
        return "valor en letras"
