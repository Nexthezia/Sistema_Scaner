from models.db import get_connection

def get_departamentos():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id_departamento, nombre FROM departamentos")
    data = cursor.fetchall()
    conn.close()
    return data

def get_municipios(id_departamento):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id_municipio, nombre FROM municipios
        WHERE id_departamento = %s
    """, (id_departamento,))
    data = cursor.fetchall()
    conn.close()
    return data

def get_tiendas(id_municipio):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id_tienda, nombre FROM tiendas
        WHERE id_municipio = %s
    """, (id_municipio,))
    data = cursor.fetchall()
    conn.close()
    return data
