# app/data_access.py
import ibm_db
from .db_connection import get_db_connection, close_db_connection
import base64
import datetime # ⬅️ Importa el módulo datetime

class CajaDataAccess:
    """
    Clase para manejar las operaciones de la base de datos del módulo de Caja.
    """
    
    def __init__(self):
        pass

    def get_next_receipt_consecutive(self):
        """
        Genera el siguiente número consecutivo para un recibo de caja.
        """
        conn = get_db_connection()
        if conn:
            try:
                query = "SELECT MAX(cajcon) FROM rccajd WHERE cajcon LIKE 'RC%'"
                stmt = ibm_db.exec_immediate(conn, query)
                result = ibm_db.fetch_tuple(stmt)
                
                next_num = 1
                if result and result[0] is not None:
                    last_consecutive_str = result[0]
                    last_num = int(last_consecutive_str[2:])
                    next_num = last_num + 1
                
                return next_num
            except Exception as e:
                print(f"ERROR >>> Falló la generación del consecutivo: {e}")
                return None
            finally:
                close_db_connection(conn)
        return None

    def save_receipt(self, data):
        """
        Guarda un recibo provisional en la nueva tabla rccajd.
        """
        conn = get_db_connection()
        if conn:
            trans_success = False
            try:
                ibm_db.set_option(conn, {ibm_db.SQL_ATTR_AUTOCOMMIT: ibm_db.SQL_AUTOCOMMIT_OFF}, 1)
                
                firma_bytes = base64.b64decode(data['firma'].split(',')[1])
                fecha_actual = datetime.datetime.now().date() # ⬅️ Obtiene la fecha actual
                
                insert_query = """
                    INSERT INTO rccajd (
                        cajcon, cajnit, cajrub, cajcco, cajval, cajvle, cajdes, cajes1, cajes2, cajfec, cajfir,
                        cajemp, cajdoc, cajtnr, cajtmv, cajund, cajcue
                    ) VALUES (
                        ?, ?, ?, ?, ?, ?, ?,
                        ?, ?, ?, ?,
                        ?, ?, ?, ?, ?, ?
                    )
                """
                
                stmt = ibm_db.prepare(conn, insert_query)
                
                ibm_db.bind_param(stmt, 1, data['codigo'])
                ibm_db.bind_param(stmt, 2, data['nit'])
                ibm_db.bind_param(stmt, 3, data['rubro'])
                ibm_db.bind_param(stmt, 4, data['centro_costo'])
                ibm_db.bind_param(stmt, 5, data['valor'])
                ibm_db.bind_param(stmt, 6, data['valor_letras'])
                ibm_db.bind_param(stmt, 7, data['concepto'])
                ibm_db.bind_param(stmt, 8, 'P')
                ibm_db.bind_param(stmt, 9, '0')
                ibm_db.bind_param(stmt, 10, fecha_actual) # ⬅️ Enlaza la fecha actual
                ibm_db.bind_param(stmt, 11, firma_bytes, ibm_db.SQL_BIND_BIN)
                ibm_db.bind_param(stmt, 12, data['empresa'])
                ibm_db.bind_param(stmt, 13, data['documento'])
                ibm_db.bind_param(stmt, 14, data['tipo_norma'])
                ibm_db.bind_param(stmt, 15, data['tipo_mov'])
                ibm_db.bind_param(stmt, 16, data['unidad_func'])
                ibm_db.bind_param(stmt, 17, data['cuenta'])
                
                ibm_db.execute(stmt)
                
                trans_success = True
                
                print("DEBUG >>> Recibo guardado exitosamente.")
                return True
            except Exception as e:
                print(f"ERROR >>> Falló al guardar el recibo: {e}")
                return False
                
            finally:
                if conn:
                    if trans_success:
                        ibm_db.commit(conn)
                        print("DEBUG >>> Transacción confirmada.")
                    else:
                        ibm_db.rollback(conn)
                        print("DEBUG >>> Transacción deshecha.")
                    close_db_connection(conn)
        return False
        
    def get_company_name(self):
        """
        Obtiene el nombre de la compañía.
        """
        conn = get_db_connection()
        if conn:
            try:
                query = "SELECT cianom FROM sicia WHERE ciacod = '01'"
                stmt = ibm_db.exec_immediate(conn, query)
                data = ibm_db.fetch_tuple(stmt)
                if data:
                    return data[0]
                return None
            except Exception as e:
                print(f"ERROR >>> Falló al obtener el nombre de la compañía: {e}")
                return None
            finally:
                close_db_connection(conn)
        return None

    def get_cost_centers(self, user_cost_center):
        """
        Obtiene los centros de costo para el usuario.
        """
        conn = get_db_connection()
        if conn:
            try:
                query = f"SELECT ccocod, cconom FROM cocco WHERE ccocod = '{user_cost_center}'"
                print(f"DEBUG >>> Ejecutando consulta de centros de costo: {query}")
                stmt = ibm_db.exec_immediate(conn, query)
                
                results = []
                row = ibm_db.fetch_assoc(stmt)
                while row:
                    results.append(row)
                    row = ibm_db.fetch_assoc(stmt)
                return results
            except Exception as e:
                print(f"ERROR >>> Falló al obtener los centros de costo: {e}")
                return []
            finally:
                close_db_connection(conn)
        return []
        
    def get_rubros(self):
        """
        Obtiene los rubros de la base de datos.
        """
        conn = get_db_connection()
        if conn:
            try:
                query = "SELECT rubcod, rubnom FROM rubcajencd ORDER BY rubnom"
                print(f"DEBUG >>> Ejecutando consulta de rubros: {query}")
                stmt = ibm_db.exec_immediate(conn, query)
                
                results = []
                row = ibm_db.fetch_assoc(stmt)
                while row:
                    results.append(row)
                    row = ibm_db.fetch_assoc(stmt)
                return results
            except Exception as e:
                print(f"ERROR >>> Falló al obtener los rubros: {e}")
                return []
            finally:
                close_db_connection(conn)
        return []
