# utils/formatter.py
from datetime import datetime

def formatear_moneda(valor):
    try:
        return "${:,.2f}".format(valor).replace(",", "X").replace(".", ",").replace("X", ".")
    except:
        return str(valor)

def formatear_periodo(periodo_str):
    try:
        fecha = datetime.strptime(periodo_str, "%Y%m")
        return fecha.strftime("%B %Y").capitalize()
    except:
        return periodo_str

def obtener_color_situacion(sit):
    """
    Dado el valor de situación, devuelve un diccionario de estilos en línea.
    """
    try:
        s = int(sit)
    except Exception:
        s = 0
    if s == 2:
        return {"backgroundColor": "#FFE5E5", "color": "#000000"}
    elif s == 3:
        return {"backgroundColor": "#FFBFBF", "color": "#000000"}
    elif s == 4:
        return {"backgroundColor": "#FF8080", "color": "#FFFFFF"}
    elif s == 5:
        return {"backgroundColor": "#FF4C4C", "color": "#FFFFFF"}
    else:
        return {}
