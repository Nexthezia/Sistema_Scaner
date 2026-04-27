from flask import Blueprint, render_template, request, jsonify, redirect, url_for
from models.db import get_connection
from routes.generar_codigo_barras import generar_codigo_barras
from routes.ubicaciones import get_departamentos, get_municipios, get_tiendas

paquetes_bp = Blueprint("paquetes", __name__, url_prefix="/paquetes")

@paquetes_bp.route("/nuevo", methods=["GET"])
def nuevo_paquete():
    return render_template("registrar_paquete.html", title_web="REGISTRAR PAQUETE")

@paquetes_bp.route("/guardar", methods=["POST"])
def guardar_paquete():
    nombre_cliente  = request.form["nombre_cliente"]
    nombre_vendedor = request.form["nombre_vendedor"]
    telefono        = request.form["telefono"]
    email           = request.form["email"]
    id_departamento = request.form["id_departamento"]
    id_municipio    = request.form["id_municipio"]
    id_tienda       = request.form["id_tienda"]
    precio          = request.form["precio"]
    envio           = request.form["envio"]
    comision        = request.form["comision"]

    codigo_barras = generar_codigo_barras()

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO paquetes (
            nombre_cliente, nombre_vendedor, telefono, email,
            id_departamento, id_municipio, id_tienda,
            precio, codigo_barras, envio, comision
        ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
    """, (
        nombre_cliente, nombre_vendedor, telefono, email,
        id_departamento, id_municipio, id_tienda,
        precio, codigo_barras, envio, comision
    ))
    conn.commit()
    id_paquete = cursor.lastrowid

    # Municipio
    cursor.execute("SELECT nombre FROM municipios WHERE id_municipio = %s", (id_municipio,))
    row = cursor.fetchone()
    municipio_nombre = row["nombre"] if row else ""

    # Departamento
    cursor.execute("SELECT nombre FROM departamentos WHERE id_departamento = %s", (id_departamento,))
    row = cursor.fetchone()
    departamento_nombre = row["nombre"] if row else ""

    # Tienda
    cursor.execute("SELECT nombre FROM tiendas WHERE id_tienda = %s", (id_tienda,))
    row = cursor.fetchone()
    tienda_nombre = row["nombre"] if row else ""

    conn.close()

    return redirect(url_for("paquetes.etiqueta",
        id_paquete          = id_paquete,
        codigo_barras       = codigo_barras,
        nombre_cliente      = nombre_cliente,
        nombre_vendedor     = nombre_vendedor,
        telefono            = telefono,
        municipio           = municipio_nombre,
        departamento        = departamento_nombre,
        tienda              = tienda_nombre,
        precio              = precio,
        envio               = envio,
    ))


@paquetes_bp.route("/etiqueta")
def etiqueta():
    datos = {
        "id_paquete"     : request.args.get("id_paquete"),
        "codigo_barras"  : request.args.get("codigo_barras"),
        "nombre_cliente" : request.args.get("nombre_cliente"),
        "nombre_vendedor": request.args.get("nombre_vendedor"),
        "telefono"       : request.args.get("telefono"),
        "municipio"      : request.args.get("municipio"),
        "departamento"   : request.args.get("departamento"),
        "tienda"         : request.args.get("tienda"),
        "precio"         : request.args.get("precio"),
        "envio"          : request.args.get("envio"),
    }
    return render_template("etiqueta.html", **datos)

@paquetes_bp.route("/departamentos")
def departamentos():
    return jsonify(get_departamentos())

@paquetes_bp.route("/municipios/<int:id_departamento>")
def municipios(id_departamento):
    return jsonify(get_municipios(id_departamento))

@paquetes_bp.route("/tiendas/<int:id_municipio>")
def tiendas(id_municipio):
    return jsonify(get_tiendas(id_municipio))
