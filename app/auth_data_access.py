# app/auth_data_access.py
import ibm_db
import base64
from .db_connection import get_db_connection, close_db_connection

def encriptar_pass(pass_clara):
    """
    Encripta una cadena usando Base64, replicando la lógica de C#.
    """
    encoded_bytes = pass_clara.encode('utf-16-le')
    return base64.b64encode(encoded_bytes).decode('utf-8')

def desencriptar_pass(pass_encriptada):
    """
    Desencripta una cadena usando Base64, replicando la lógica de C#.
    """
    try:
        decrypted_bytes = base64.b64decode(pass_encriptada)
        return decrypted_bytes.decode('utf-16-le')
    except:
        return ""

def iniciar_sesion(usuario):
    """
    Busca los datos de un usuario para el inicio de sesión.
    """
    query = f"SELECT idecod, ideide, idenom, ideap1, ideap2, ideofi, idegru, ideact, idecla, idecco, ideclaw, idemail FROM siided WHERE idecod ='{usuario}'"
    conn = get_db_connection()
    user_data = None
    
    if conn:
        try:
            print(f"DEBUG >>> Ejecutando query iniciar_sesion: {query}")
            stmt = ibm_db.exec_immediate(conn, query)
            user_data = ibm_db.fetch_assoc(stmt)
            print(f"DEBUG >>> Resultado iniciar_sesion: {user_data}")
            return user_data
        except Exception as e:
            print(f"ERROR >>> iniciar_sesion falló: {e}")
        finally:
            close_db_connection(conn)
    return None

def validar_pass(usuario, password):
    user_data = iniciar_sesion(usuario)
    if user_data:
        clave_db_encriptada = user_data.get('ideclaw', '') 
        print(f"DEBUG >>> IDECLAW en BD (Base64): {repr(clave_db_encriptada)}")

        pass_desencriptada = desencriptar_pass(clave_db_encriptada)

        print(f"DEBUG >>> Usuario ingresado: {usuario}")
        print(f"DEBUG >>> Password en BD (desencriptada cruda): {repr(pass_desencriptada)}")
        print(f"DEBUG >>> Password ingresada: {repr(password)}")

        pass_desencriptada = pass_desencriptada.replace("\x00", "").strip()
        password = password.replace("\x00", "").strip()
        
        print(f"DEBUG >>> Comparando '{pass_desencriptada}' == '{password}'")

        return pass_desencriptada == password
    else:
        print(f"DEBUG >>> Usuario {usuario} no encontrado en la BD")
    return False
