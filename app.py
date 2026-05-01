from flask import Flask, render_template
from routes.registrar_paquete import paquetes_bp
from routes.gestionar_rutas import rutas_bp

app = Flask(__name__)

#Guarda cache por 1 año
app = Flask(__name__)

# Configura el cache para 1 año (31,536,000 segundos)
#app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 31536000

# Registrar blueprints
app.register_blueprint(paquetes_bp)
app.register_blueprint(rutas_bp)


@app.route("/")
def index():
    return render_template("index.html", title_web="INICIO - ScanLogix")

if __name__ == "__main__":
    app.run(debug=True)
