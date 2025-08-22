# app/routes/auth_routes.py
from flask import Blueprint, render_template, request, redirect, url_for, session
from ..auth_data_access import iniciar_sesion, validar_pass
import ibm_db

auth_bp = Blueprint('auth_bp', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        print("DEBUG >>> Entré a /login con POST")
        usuario = request.form['Txt_Usuario']
        password_ingresada = request.form['Txt_Pass']
        print(f"DEBUG >>> Datos recibidos -> usuario: {usuario}, password_ingresada: {password_ingresada}")

        resultado_validacion = validar_pass(usuario, password_ingresada)
        print(f"DEBUG >>> Resultado validar_pass: {resultado_validacion}")

        if resultado_validacion:
            user_data = iniciar_sesion(usuario)
            print(f"DEBUG >>> Datos obtenidos de iniciar_sesion: {user_data}")

            if user_data:
                if user_data.get('ideact') == 'S':
                    session['NombreUsuario'] = user_data.get('idecod', '').strip()
                    session['NombreCompleto'] = f"{user_data.get('idenom', '')} {user_data.get('ideap1', '')} {user_data.get('ideap2', '')}"
                    session['IdUsuario'] = user_data.get('ideide', '').strip()
                    session['GrupoUsuario'] = user_data.get('idegru', '').strip()
                    session['CentroCosto'] = user_data.get('idecco', '').strip()
                    session['Estado_Usuario'] = user_data.get('ideact', '').strip()

                    print("DEBUG >>> Login exitoso, redirigiendo a home")
                    return redirect(url_for('home'))
                else:
                    print("DEBUG >>> Usuario encontrado pero inactivo")
                    return render_template('login.html', error_message="El usuario no se encuentra activo.")
            else:
                print("DEBUG >>> iniciar_sesion devolvió None")
                return render_template('login.html', error_message="Credenciales incorrectas.")
        else:
            print("DEBUG >>> validar_pass devolvió False")
            return render_template('login.html', error_message="Credenciales incorrectas.")
    
    print("DEBUG >>> GET /login renderizando formulario")
    return render_template('login.html')

@auth_bp.route('/logout')
def logout():
    session.clear()
    print("DEBUG >>> Sesión cerrada")
    return redirect(url_for('auth_bp.login'))
