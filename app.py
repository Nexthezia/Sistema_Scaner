from flask import Flask
from routes.registrar_paquete import paquetes_bp

app = Flask(__name__)

# Registrar blueprint
app.register_blueprint(paquetes_bp)

if __name__ == "__main__":
    app.run(debug=True)
