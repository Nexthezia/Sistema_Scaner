from flask import Blueprint, render_template, request
from routes.ubicaciones import get_departamentos, get_municipios, get_tiendas
from routes.etiqueta import guardar_y_redirigir, render_etiqueta
from flask import jsonify

paquetes_bp = Blueprint("paquetes", __name__, url_prefix="/paquetes")


@paquetes_bp.route("/nuevo", methods=["GET"])
def nuevo_paquete():
    return render_template("registrar_paquete.html")


@paquetes_bp.route("/guardar", methods=["POST"])
def guardar_paquete():
    return guardar_y_redirigir(request.form)


@paquetes_bp.route("/etiqueta")
def etiqueta():
    return render_etiqueta(request.args)


@paquetes_bp.route("/departamentos")
def departamentos():
    return jsonify(get_departamentos())


@paquetes_bp.route("/municipios/<int:id_departamento>")
def municipios(id_departamento):
    return jsonify(get_municipios(id_departamento))


@paquetes_bp.route("/tiendas/<int:id_municipio>")
def tiendas(id_municipio):
    return jsonify(get_tiendas(id_municipio))
