import pandas as pd
from dash import html
from dash_ag_grid import AgGrid

# NOTA: Las reglas CSS para las clases bg-sit-2 a bg-sit-5 deben ir en assets/custom.css
# .bg-sit-2 { background-color: #FFE5E5; color: #000000; }
# .bg-sit-3 { background-color: #FFBFBF; color: #000000; }
# .bg-sit-4 { background-color: #FF8080; color: #FFFFFF; }
# .bg-sit-5 { background-color: #FF4C4C; color: #FFFFFF; }

# Mapeo de iniciales de mes para los encabezados secundarios
MONTH_LABELS = {
    "01": "E", "02": "F", "03": "M", "04": "A", "05": "M",
    "06": "J", "07": "J", "08": "A", "09": "S", "10": "O",
    "11": "N", "12": "D"
}

# Estilos de color según situación
SITUATION_STYLES = {
    2: {}, 3: {}, 4: {}, 5: {}
}  # Se usan solo para generar cellClassRules en definitions


def crear_pivot_table_aggrid(periodos):
    """
    Genera un AgGrid con estructura pivot, encabezados agrupados por año y mes,
    formato monetario y estilos condicionales según situación.
    """
    if not periodos:
        return html.Div("No hay datos para mostrar.")

    # 1) Organizar años y meses disponibles y cargar datos crudos
    columnas_por_anio = {}
    raw_data = {}
    for p in periodos:
        periodo = p.get("periodo", "")
        if len(periodo) == 5:
            periodo = periodo[:4] + periodo[4:].zfill(2)
        if len(periodo) == 6:
            anio, mes = periodo[:4], periodo[4:6]
            columnas_por_anio.setdefault(anio, set()).add(mes)
            for ent in p.get("entidades", []):
                entidad = ent.get("entidad", "")
                monto = ent.get("monto", 0) * 1000
                situacion = ent.get("situacion", 0) or 0
                if entidad not in raw_data:
                    raw_data[entidad] = {
                        "Entidad": entidad,
                        "Situación": situacion,
                        "Monto": monto,
                        "hist": {}
                    }
                raw_data[entidad]["hist"][(anio, mes)] = situacion

    sorted_anios = sorted(columnas_por_anio.keys(), reverse=True)
    for anio in sorted_anios:
        columnas_por_anio[anio] = sorted(columnas_por_anio[anio], reverse=True)

    # 2) Construir registros para AgGrid
    registros = []
    for data in raw_data.values():
        fila = {
            "Entidad": data["Entidad"],
            "Situación": data["Situación"],
            "Monto": int(data["Monto"])
        }
        for anio in sorted_anios:
            for mes in columnas_por_anio[anio]:
                key = f"{anio}-{mes}"
                fila[key] = data["hist"].get((anio, mes), "")
        registros.append(fila)

    df = pd.DataFrame(registros)

    # 3) defaultColDef con estilos generales
    default_col_def = {
        "resizable": True,
        "sortable": True,
        "filter": True,
        "suppressMenu": True, 
        "headerClass": "custom-header", 
        "cellStyle": {
            "backgroundColor": "#2D2D2D",
            "color": "white",
            "textAlign": "center",
            "fontSize": "0.8rem",
            "whiteSpace": "normal",
            "overflowWrap": "break-word"
        },
        "headerStyle": {
            "backgroundColor": "#393939",
            "color": "white",
            "textAlign": "center",
            "whiteSpace": "normal",
            "overflowWrap": "break-word"
        }
    }

    # 4) Definir columnas principales con flex por porcentaje
    col_defs = [
        {"headerName": "Entidad", "field": "Entidad", "flex": 25},
        {"headerName": "Situación", "field": "Situación", "flex": 10},
        {
            "headerName": "Monto ($)",
            "field": "Monto",
            "type": "numericColumn",
            "valueFormatter": {
                "function": "params.value != null ? '$ ' + params.value.toLocaleString('es-AR') : ''"
            },
            "sort": "desc",
            "sortIndex": 0,
            "flex": 10
        }
    ]

    # 5) Columnas por año con flex para meses sumando 55%
    total_meses = sum(len(columnas_por_anio[a]) for a in sorted_anios)
    flex_mes = 55 / total_meses if total_meses else 0
    for anio in sorted_anios:
        children = []
        for mes in columnas_por_anio[anio]:
            col_id = f"{anio}-{mes}"
            children.append({
                "headerName": MONTH_LABELS.get(mes, mes),
                "field": col_id,
                "flex": flex_mes,
                "cellClassRules": {
                    f"bg-sit-{k}": f"params.value == {k}" for k in SITUATION_STYLES.keys()
                }
            })
        col_defs.append({
            "headerName": anio,
            "children": children,
            "marryChildren": True
        })

    # 6) Renderizado final sin inyección de <style>
    return html.Div(
        AgGrid(
            id="tabla-ag-grid",
            columnDefs=col_defs,
            rowData=df.to_dict("records"),
            defaultColDef=default_col_def,
            dashGridOptions={
                "domLayout": "autoHeight",
                "suppressHorizontalScroll": False,
                "headerHeight": 32,
                "groupHeaderHeight": 32
            }
        ),
        className="ag-theme-alpine-dark",
        style={"width": "100%"}
    )
