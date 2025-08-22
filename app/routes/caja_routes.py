# app/routes/caja_routes.py
from flask import Blueprint, render_template, request, jsonify, redirect, url_for, session
from ..data_access import CajaDataAccess
from ..db_connection import num_to_letters

caja_bp = Blueprint('caja_bp', __name__)

@caja_bp.route('/caja')
def caja():
    if 'NombreUsuario' not in session:
        return redirect(url_for('auth_bp.login'))
    
    db = CajaDataAccess()
    sicia_name = db.get_company_name()
    
    return render_template('caja/caja.html', show_nav=True, active_page='caja', sicia_name=sicia_name)

@caja_bp.route('/caja/content/<content_name>')
def get_caja_content(content_name):
    """
    Ruta para obtener contenido dinámico para la página de Caja.
    """
    # Lógica de validación de permisos
    if 'NombreUsuario' not in session:
        return redirect(url_for('auth_bp.login'))

    db = CajaDataAccess()

    if content_name == 'recibos-provisionales':
        ultimo_consecutivo = db.get_next_receipt_consecutive()
        nuevo_consecutivo_str = f"RC{ultimo_consecutivo}"
        
        centro_costo_usuario = session.get('CentroCosto')

        centros_costo = db.get_cost_centers(centro_costo_usuario)
        rubros = db.get_rubros()

        return render_template(
            'caja/partials/recibos_provisionales_form.html',
            consecutivo=nuevo_consecutivo_str,
            pagado_a=session.get('NombreCompleto'),
            id_usuario=session.get('IdUsuario'),
            centros_costo=centros_costo,
            rubros=rubros
        )
    elif content_name == 'gestion-recibos':
        recibos_pendientes = db.get_pending_receipts()
        estado_caja = db.get_caja_state()
        return render_template('caja/partials/gestion_recibos_content.html',
                               recibos_pendientes=recibos_pendientes,
                               estado_caja=estado_caja)
    elif content_name == 'recibos-legalizados':
        return render_template('caja/partials/recibos_legalizados_content.html')
    else:
        return "", 404

@caja_bp.route('/caja/recibos-provisionales/guardar', methods=['POST'])
def guardar_recibo():
    db = CajaDataAccess()
    
    pagado_a = request.form.get('pagado_a')
    id_usuario = request.form.get('id_usuario')
    rubro = request.form.get('rubros')
    centro_costo = request.form.get('centro_costo')
    valor_str = request.form.get('valor')
    concepto = request.form.get('concepto')
    firma_data = request.form.get('firma')

    if not firma_data:
        return jsonify({"status": "error", "message": "La firma es obligatoria para guardar el recibo."})

    if not all([pagado_a, id_usuario, rubro, centro_costo, valor_str, concepto]):
        return jsonify({"status": "error", "message": "Los campos con (*) son obligatorios."})

    try:
        valor = float(valor_str)
    except ValueError:
        return jsonify({"status": "error", "message": "El valor ingresado no es un número válido."})
        
    consecutivo_num = db.get_next_receipt_consecutive()
    if consecutivo_num is None:
        return jsonify({"status": "error", "message": "No se pudo generar el número de recibo."})

    consecutivo_str = f"RC{consecutivo_num}"
    valor_letras = num_to_letters(valor)
    
    data_to_save = {
        'num_recibo': consecutivo_num,
        'codigo': consecutivo_str,
        'nit': id_usuario,
        'rubro': rubro,
        'centro_costo': centro_costo,
        'valor': valor,
        'concepto': concepto,
        'valor_letras': valor_letras,
        'firma': firma_data,
        'empresa': session.get('IdUsuario', '01'),
        'documento': 'RP',
        'tipo_norma': 'N',
        'tipo_mov': 0,
        'unidad_func': 'UFFIN',
        'cuenta': '0'
    }
    
    if db.save_receipt(data_to_save):
        return jsonify({"status": "success", "message": "El registro ha sido almacenado con éxito."})
    else:
        return jsonify({"status": "error", "message": "Ocurrió un error al guardar el registro."})
