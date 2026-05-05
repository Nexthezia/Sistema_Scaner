from flask import Blueprint, render_template, request, jsonify, make_response
from models.db import get_connection
from routes.ubicaciones import get_departamentos
import io
import csv

rutas_bp = Blueprint("rutas", __name__, url_prefix="/rutas")

# ─────────────────────────────────────────────
#  Helpers
# ─────────────────────────────────────────────

def get_tiendas_por_depto(id_departamento: int) -> list:
    """Devuelve las tiendas que pertenecen a un departamento."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT DISTINCT t.id_tienda, t.nombre
        FROM   tiendas t
        INNER JOIN municipios m ON t.id_municipio = m.id_municipio
        WHERE  m.id_departamento = %s
        ORDER  BY t.nombre
        """,
        (id_departamento,),
    )
    tiendas = cursor.fetchall()
    conn.close()
    return tiendas


def _build_rutas_query(id_departamento, id_tienda):
    """Construye la cláusula WHERE y los parámetros para la consulta de rutas."""
    filtros, params = [], []
    if id_departamento:
        filtros.append("r.id_departamento = %s")
        params.append(id_departamento)
    if id_tienda:
        filtros.append("r.id_tienda = %s")
        params.append(id_tienda)
    where = ("WHERE " + " AND ".join(filtros)) if filtros else ""
    return where, params


def _get_departamento_de_tienda(cursor, id_tienda: int):
    """Obtiene el id_departamento al que pertenece una tienda."""
    cursor.execute(
        """
        SELECT m.id_departamento
        FROM   tiendas t
        INNER  JOIN municipios m ON t.id_municipio = m.id_municipio
        WHERE  t.id_tienda = %s
        """,
        (id_tienda,),
    )
    row = cursor.fetchone()
    return row["id_departamento"] if row else None


# ─────────────────────────────────────────────
#  Páginas
# ─────────────────────────────────────────────

@rutas_bp.route("/", methods=["GET"])
def gestionar_rutas():
    return render_template(
        "gestionar_rutas.html",
        title_web="GESTIONAR RUTAS",
        departamentos=get_departamentos(),
    )


@rutas_bp.route("/editar/<int:id_ruta>", methods=["GET"])
def editar_ruta_view(id_ruta):
    """Vista para editar una ruta existente."""
    departamentos = get_departamentos()
    return render_template(
        "gestionar_rutas.html",
        title_web=f"EDITAR RUTA #{id_ruta}",
        departamentos=departamentos,
        id_ruta_editar=id_ruta,
    )


@rutas_bp.route("/ver", methods=["GET"])
def ver_rutas():
    """Listado de rutas con filtros opcionales por departamento y tienda."""
    id_departamento = request.args.get("departamento", type=int)
    id_tienda = request.args.get("tienda", type=int)

    try:
        conn = get_connection()
        cursor = conn.cursor()

        where, params = _build_rutas_query(id_departamento, id_tienda)
        cursor.execute(
            f"""
            SELECT
                r.id_ruta,
                r.nombre_ruta,
                d.nombre          AS departamento,
                t.nombre          AS tienda,
                r.fecha_creacion,
                COUNT(dr.id_paquete) AS cantidad_paquetes
            FROM   rutas r
            LEFT   JOIN departamentos d  ON r.id_departamento = d.id_departamento
            LEFT   JOIN tiendas t        ON r.id_tienda       = t.id_tienda
            LEFT   JOIN detalle_ruta dr  ON r.id_ruta         = dr.id_ruta
            {where}
            GROUP  BY r.id_ruta, r.nombre_ruta, d.nombre, t.nombre, r.fecha_creacion
            ORDER  BY r.fecha_creacion DESC, r.id_ruta DESC
            """,
            params,
        )
        rutas = cursor.fetchall()

        departamento_seleccionado = id_departamento or (
            _get_departamento_de_tienda(cursor, id_tienda) if id_tienda else None
        )

        tiendas = get_tiendas_por_depto(departamento_seleccionado) if departamento_seleccionado else []
        conn.close()

    except Exception as exc:
        print(f"[ver_rutas] Error: {exc}")
        rutas, tiendas, departamento_seleccionado = [], [], None

    return render_template(
        "ver_rutas.html",
        title_web="VER RUTAS",
        rutas=rutas,
        departamentos=get_departamentos(),
        tiendas=tiendas,
        filtro_departamento=departamento_seleccionado,
        filtro_tienda=id_tienda,
        total_rutas=len(rutas),
        total_paquetes=sum(r["cantidad_paquetes"] or 0 for r in rutas),
    )


# ─────────────────────────────────────────────
#  API JSON
# ─────────────────────────────────────────────

@rutas_bp.route("/ver_detalles/<int:id_ruta>", methods=["GET"])
def ver_detalles_ruta_view(id_ruta):
    """Página para ver los detalles de una ruta en HTML sin usar JS."""
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT r.id_ruta, r.nombre_ruta, r.id_departamento, d.nombre as departamento,
                   r.id_tienda, t.nombre as tienda, r.fecha_creacion
            FROM rutas r
            LEFT JOIN departamentos d ON r.id_departamento = d.id_departamento
            LEFT JOIN tiendas t ON r.id_tienda = t.id_tienda
            WHERE r.id_ruta = %s
            """,
            (id_ruta,),
        )
        ruta = cursor.fetchone()

        if not ruta:
            conn.close()
            return "Ruta no encontrada", 404

        cursor.execute(
            """
            SELECT dr.posicion, p.codigo_barras, p.nombre_cliente,
                   p.telefono, p.email, p.precio,
                   d.nombre  AS departamento,
                   m.nombre  AS municipio,
                   t.nombre  AS tienda
            FROM detalle_ruta dr
            INNER JOIN paquetes      p ON dr.id_paquete      = p.id_paquete
            LEFT  JOIN departamentos d ON p.id_departamento  = d.id_departamento
            LEFT  JOIN municipios    m ON p.id_municipio     = m.id_municipio
            LEFT  JOIN tiendas       t ON p.id_tienda        = t.id_tienda
            WHERE dr.id_ruta = %s
            ORDER BY dr.posicion
            """,
            (id_ruta,),
        )
        paquetes = cursor.fetchall()
        conn.close()

        return render_template(
            "ver_detalles_ruta.html",
            title_web=f"Detalles - {ruta['nombre_ruta']}",
            ruta=ruta,
            paquetes=paquetes
        )
    except Exception as e:
        return f"Error al cargar detalles: {str(e)}", 500


@rutas_bp.route("/detalles/<int:id_ruta>", methods=["GET"])
def detalles_ruta(id_ruta: int):
    """Devuelve la cabecera y el detalle de paquetes de una ruta en JSON."""
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT r.id_ruta, r.nombre_ruta,
                   d.nombre AS departamento,
                   t.nombre AS tienda,
                   r.fecha_creacion
            FROM   rutas r
            LEFT   JOIN departamentos d ON r.id_departamento = d.id_departamento
            LEFT   JOIN tiendas t       ON r.id_tienda       = t.id_tienda
            WHERE  r.id_ruta = %s
            """,
            (id_ruta,),
        )
        ruta = cursor.fetchone()
        if not ruta:
            conn.close()
            return jsonify({"success": False, "error": "Ruta no encontrada"}), 404

        ruta = dict(ruta)
        if ruta.get("fecha_creacion"):
            ruta["fecha_creacion"] = ruta["fecha_creacion"].strftime("%d/%m/%Y %H:%M")

        cursor.execute(
            """
            SELECT dr.posicion,
                   p.id_paquete, p.codigo_barras, p.nombre_cliente,
                   p.telefono, p.email, p.precio,
                   d.nombre  AS departamento,
                   m.nombre  AS municipio,
                   t.nombre  AS tienda
            FROM   detalle_ruta dr
            INNER  JOIN paquetes      p ON dr.id_paquete      = p.id_paquete
            LEFT   JOIN departamentos d ON p.id_departamento  = d.id_departamento
            LEFT   JOIN municipios    m ON p.id_municipio     = m.id_municipio
            LEFT   JOIN tiendas       t ON p.id_tienda        = t.id_tienda
            WHERE  dr.id_ruta = %s
            ORDER  BY dr.posicion
            """,
            (id_ruta,),
        )
        paquetes = cursor.fetchall()
        conn.close()

        return jsonify({"success": True, "ruta": ruta, "paquetes": paquetes})

    except Exception as exc:
        return jsonify({"success": False, "error": str(exc)}), 500

@rutas_bp.route("/get_tiendas/<int:id_departamento>", methods=["GET"])
def get_tiendas_por_departamento(id_departamento: int):
    """Devuelve todas las tiendas de un departamento."""
    try:
        return jsonify({"success": True, "tiendas": get_tiendas_por_depto(id_departamento)})
    except Exception as exc:
        return jsonify({"success": False, "error": str(exc)}), 500


@rutas_bp.route("/validar_codigo/<string:codigo>", methods=["GET"])
def validar_codigo_barras(codigo: str):
    """Valida que un código de barras exista y devuelve los datos básicos del paquete."""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id_paquete, nombre_cliente, codigo_barras FROM paquetes WHERE codigo_barras = %s",
            (codigo,),
        )
        paquete = cursor.fetchone()
        conn.close()

        if not paquete:
            return jsonify({"success": False, "error": "Código no encontrado"}), 404

        return jsonify({
            "success": True,
            "id_paquete": paquete["id_paquete"],
            "nombre_cliente": paquete["nombre_cliente"],
            "codigo_barras": paquete["codigo_barras"],
        })

    except Exception as exc:
        return jsonify({"success": False, "error": str(exc)}), 500


@rutas_bp.route("/guardar_ruta", methods=["POST"])
def guardar_ruta():
    """Crea una nueva ruta con sus paquetes."""
    data = request.json or {}
    nombre_ruta     = data.get("nombre_ruta")
    id_departamento = data.get("id_departamento")
    id_tienda       = data.get("id_tienda")
    paquetes        = data.get("paquetes", [])

    if not all([nombre_ruta, id_departamento, id_tienda, paquetes]):
        return jsonify({"success": False, "error": "Datos incompletos"}), 400

    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            "INSERT INTO rutas (nombre_ruta, id_departamento, id_tienda) VALUES (%s, %s, %s)",
            (nombre_ruta, id_departamento, id_tienda),
        )
        id_ruta = cursor.lastrowid

        cursor.executemany(
            "INSERT INTO detalle_ruta (id_ruta, id_paquete, posicion) VALUES (%s, %s, %s)",
            [(id_ruta, id_paquete, pos) for pos, id_paquete in enumerate(paquetes, 1)],
        )

        conn.commit()
        conn.close()

        return jsonify({
            "success": True,
            "id_ruta": id_ruta,
            "mensaje": f"Ruta '{nombre_ruta}' guardada con {len(paquetes)} paquetes",
        })

    except Exception as exc:
        return jsonify({"success": False, "error": str(exc)}), 500


@rutas_bp.route("/actualizar/<int:id_ruta>", methods=["POST"])
def actualizar_ruta(id_ruta: int):
    """Actualiza la cabecera de una ruta y, opcionalmente, reemplaza sus paquetes."""
    data = request.json or {}
    nombre_ruta     = data.get("nombre_ruta")
    id_departamento = data.get("id_departamento")
    id_tienda       = data.get("id_tienda")
    paquetes        = data.get("paquetes", [])

    if not all([nombre_ruta, id_departamento, id_tienda]):
        return jsonify({"success": False, "error": "Datos básicos incompletos"}), 400

    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            UPDATE rutas
            SET    nombre_ruta = %s, id_departamento = %s, id_tienda = %s
            WHERE  id_ruta = %s
            """,
            (nombre_ruta, id_departamento, id_tienda, id_ruta),
        )

        if paquetes:
            cursor.execute("DELETE FROM detalle_ruta WHERE id_ruta = %s", (id_ruta,))
            cursor.executemany(
                "INSERT INTO detalle_ruta (id_ruta, id_paquete, posicion) VALUES (%s, %s, %s)",
                [(id_ruta, id_paquete, pos) for pos, id_paquete in enumerate(paquetes, 1)],
            )

        conn.commit()
        conn.close()

        return jsonify({"success": True, "mensaje": "Ruta actualizada exitosamente"})

    except Exception as exc:
        return jsonify({"success": False, "error": str(exc)}), 500


@rutas_bp.route("/imprimir/<int:id_ruta>")
def imprimir_ruta(id_ruta):
    """Genera una página HTML formateada para imprimir los detalles de una ruta."""
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT r.id_ruta, r.nombre_ruta, d.nombre as departamento,
                   t.nombre as tienda, r.fecha_creacion
            FROM rutas r
            LEFT JOIN departamentos d ON r.id_departamento = d.id_departamento
            LEFT JOIN tiendas t ON r.id_tienda = t.id_tienda
            WHERE r.id_ruta = %s
            """,
            (id_ruta,),
        )
        ruta = cursor.fetchone()

        if not ruta:
            conn.close()
            return "Ruta no encontrada", 404

        cursor.execute(
            """
            SELECT dr.posicion, p.codigo_barras, p.nombre_cliente, p.telefono, p.precio
            FROM detalle_ruta dr
            INNER JOIN paquetes p ON dr.id_paquete = p.id_paquete
            WHERE dr.id_ruta = %s
            ORDER BY dr.posicion
            """,
            (id_ruta,),
        )
        paquetes = cursor.fetchall()
        conn.close()

        return render_template("imprimir_ruta.html", ruta=ruta, paquetes=paquetes)
    except Exception as e:
        print(f"Error al generar impresión de ruta: {e}")
        return "Error al generar la página de impresión", 500


@rutas_bp.route("/descargar/<int:id_ruta>")
def descargar_ruta_csv(id_ruta):
    """Genera y descarga un archivo CSV con los detalles de la ruta."""
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT r.nombre_ruta, d.nombre as departamento, t.nombre as tienda, r.fecha_creacion
            FROM rutas r
            LEFT JOIN departamentos d ON r.id_departamento = d.id_departamento
            LEFT JOIN tiendas t ON r.id_tienda = t.id_tienda
            WHERE r.id_ruta = %s
            """,
            (id_ruta,),
        )
        ruta = cursor.fetchone()

        if not ruta:
            conn.close()
            return "Ruta no encontrada", 404

        cursor.execute(
            """
            SELECT dr.posicion, p.codigo_barras, p.nombre_cliente, p.telefono, p.email, p.precio
            FROM detalle_ruta dr
            INNER JOIN paquetes p ON dr.id_paquete = p.id_paquete
            WHERE dr.id_ruta = %s
            ORDER BY dr.posicion
            """,
            (id_ruta,),
        )
        paquetes = cursor.fetchall()
        conn.close()

        output = io.StringIO()
        writer = csv.writer(output, delimiter=";")

        writer.writerow(["Ruta", ruta["nombre_ruta"]])
        writer.writerow(["Departamento", ruta["departamento"] or ""])
        writer.writerow(["Tienda", ruta["tienda"] or ""])
        writer.writerow(["Fecha", ruta["fecha_creacion"].strftime("%d/%m/%Y %H:%M") if ruta["fecha_creacion"] else ""])
        writer.writerow([])
        writer.writerow(["Posicion", "Codigo barras", "Cliente", "Telefono", "Email", "Precio"])

        for paquete in paquetes:
            writer.writerow([
                paquete['posicion'], paquete['codigo_barras'], paquete['nombre_cliente'],
                paquete['telefono'] or "", paquete['email'] or "", paquete['precio'] or ""
            ])

        nombre_sano = "".join(c for c in ruta["nombre_ruta"] if c.isalnum() or c in (" ", "_")).rstrip()
        nombre_archivo = f"ruta_{nombre_sano}.csv"

        # Corrección: construir la respuesta correctamente con BOM para UTF-8
        csv_bytes = b"\xef\xbb\xbf" + output.getvalue().encode("utf-8")
        response = make_response(csv_bytes)
        response.headers["Content-Disposition"] = f"attachment; filename={nombre_archivo}"
        response.headers["Content-Type"] = "text/csv; charset=utf-8"
        return response

    except Exception as e:
        print(f"Error al descargar CSV: {e}")
        return "Error al generar el archivo CSV", 500
