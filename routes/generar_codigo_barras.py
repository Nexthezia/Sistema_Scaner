import uuid
import datetime

def generar_codigo_barras():
    fecha = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    uid = uuid.uuid4().hex[:6].upper()
    return f"PKT-{fecha}-{uid}"
