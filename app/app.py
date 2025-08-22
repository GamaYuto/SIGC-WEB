# app/app.py
from flask import Flask, jsonify, render_template, session, redirect, url_for
from .db_connection import get_db_connection, close_db_connection, execute_select
from .routes.caja_routes import caja_bp
from .routes.auth_routes import auth_bp # Importa el nuevo Blueprint

app = Flask(
    __name__,
    static_folder='../static',
    template_folder='../templates'
)

app.config['SECRET_KEY'] = 'tu_clave_secreta_aqui'

app.register_blueprint(caja_bp)
app.register_blueprint(auth_bp)

@app.route('/')
def home():
    if 'NombreUsuario' not in session:
        return redirect(url_for('auth_bp.login'))

    sicia_name = execute_select("SELECT cianom FROM sicia")
    return render_template(
        'index.html',
        sicia_name=sicia_name,
        active_page='home'
    )

@app.route('/test-db-connection')
def test_db():
    conn = get_db_connection()
    if conn:
        close_db_connection(conn)
        return jsonify({"status": "success", "message": "Conexión a la base de datos exitosa."})
    else:
        return jsonify({"status": "error", "message": "Fallo al conectar a la base de datos."}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)