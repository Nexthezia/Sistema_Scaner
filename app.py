from flask import Flask, render_template
from routes.registrar_paquete import paquetes_bp
from routes.gestionar_rutas import rutas_bp
import traceback

app = Flask(__name__)

# Configura el cache para 1 año (31,536,000 segundos)
#app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 31536000

# Registrar blueprints
app.register_blueprint(paquetes_bp)
app.register_blueprint(rutas_bp)

@app.route("/")
def index():
    return render_template("index.html", title_web="INICIO - ScanLogix")

@app.errorhandler(Exception)
def handle_exception(e):
    """Captura cualquier error y lo muestra en pantalla para poder depurarlo."""
    return f"<h1>Error Interno (500)</h1><p><b>Fallo exacto:</b> {str(e)}</p><hr><pre>{traceback.format_exc()}</pre>", 500

if __name__ == "__main__":
    app.run(debug=True)
