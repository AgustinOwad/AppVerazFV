import pandas as pd
from dash import dash_table
from dash.dash_table.Format import Format, Scheme, Symbol, Group

# Mapeo de iniciales de mes
MONTH_LABELS = {
    "01": "E", "02": "F", "03": "M", "04": "A", "05": "M",
    "06": "J", "07": "J", "08": "A", "09": "S", "10": "O",
    "11": "N", "12": "D"
}

# Estilos de color según situación
SITUATION_STYLES = {
    2: {"backgroundColor": "#FFE5E5", "color": "#000000"},
    3: {"backgroundColor": "#FFBFBF", "color": "#000000"},
    4: {"backgroundColor": "#FF8080", "color": "#FFFFFF"},
    5: {"backgroundColor": "#FF4C4C", "color": "#FFFFFF"}
}


def crear_pivot_table_dash(periodos):
    """
    Genera una DataTable con id="tabla-pivot-table" para permitir exportar a Excel.
    """
    # 1) Identificar años y meses
    columns_by_year = {}
    for p in periodos:
        per = p.get("periodo", "")
        if len(per) == 5:
            per = per[:4] + per[4:].zfill(2)
        if len(per) == 6:
            year, month = per[:4], per[4:6]
            columns_by_year.setdefault(year, set()).add(month)
    sorted_years = sorted(columns_by_year.keys(), reverse=True)
    for year in sorted_years:
        columns_by_year[year] = sorted(columns_by_year[year], reverse=True)

    # 2) Pivot de datos
    pivot_data = {}
    for p in sorted(periodos, key=lambda x: x.get("periodo", ""), reverse=True):
        per = p.get("periodo", "")
        if len(per) == 5:
            per = per[:4] + per[4:].zfill(2)
        if len(per) == 6:
            year, month = per[:4], per[4:6]
            for ent in p.get("entidades", []):
                name = ent.get("entidad", "")
                monto = ent.get("monto", 0) * 1000
                situ = ent.get("situacion", 0) or 0
                if name not in pivot_data:
                    pivot_data[name] = {
                        "Entidad": name,
                        "Situación": situ,
                        "Monto": monto,
                        "hist": {}
                    }
                pivot_data[name]["hist"][(year, month)] = situ

    # 3) DataFrame
    data_rows = []
    for info in pivot_data.values():
        row = {
            "Entidad": info["Entidad"],
            "Situación": info["Situación"],
            "Monto": info["Monto"]
        }
        for year in sorted_years:
            for month in columns_by_year[year]:
                col_id = f"{year}-{month}"
                row[col_id] = info["hist"].get((year, month), "")
        data_rows.append(row)
    df = pd.DataFrame(data_rows)

    # 4) Filter out fully empty year columns
    for year in list(sorted_years):
        valid = [m for m in columns_by_year[year] if not df[f"{year}-{m}"].astype(str).eq("").all()]
        if valid:
            columns_by_year[year] = valid
        else:
            sorted_years.remove(year)
            del columns_by_year[year]

    # 5) Columnas para DataTable
    columns = [
        {"name": ["", "Entidad"], "id": "Entidad", "type": "text"},
        {"name": ["", "Situación"], "id": "Situación", "type": "text"},
        {
            "name": ["", "Monto ($)"],
            "id": "Monto",
            "type": "numeric",
            "format": (
                Format(scheme=Scheme.fixed, precision=0, group=Group.yes)
                .group_delimiter(".")
                .decimal_delimiter(",")
                .symbol(Symbol.yes)
                .symbol_prefix("$")
            )
        }
    ]
    for year in sorted_years:
        first = True
        for month in columns_by_year[year]:
            columns.append({
                "name": [year if first else "", MONTH_LABELS.get(month, month)],
                "id": f"{year}-{month}",
                "type": "numeric"
            })
            first = False

    # 6) CSS y estilos condicionales… (igual que antes)
    css_rules = []
    for year in sorted_years:
        for m in columns_by_year[year]:
            col_id = f"{year}-{m}"
            css_rules.append({
                "selector": f"[data-dash-column='{col_id}'] .column-header--sort",
                "rule": "display: none !important;"
            })

    style_cell_cond = [
        {"if": {"column_id": "Entidad"}, "width": "25%"},
        {"if": {"column_id": "Situación"}, "width": "10%"},
        {"if": {"column_id": "Monto"}, "width": "10%"},
    ]
    total_months = sum(len(columns_by_year[yr]) for yr in sorted_years)
    mes_width = 55 / total_months if total_months else 0
    for year in sorted_years:
        for m in columns_by_year[year]:
            style_cell_cond.append({
                "if": {"column_id": f"{year}-{m}"},
                "width": f"{mes_width:.2f}%"
            })

    style_data_cond = []
    for year in sorted_years:
        for m in columns_by_year[year]:
            col_id = f"{year}-{m}"
            for val, st in SITUATION_STYLES.items():
                style_data_cond.append({
                    "if": {"filter_query": f"{{{col_id}}} = {val}", "column_id": col_id},
                    **st
                })

    # 7) Devolvemos la DataTable con **id** para exportar
    return dash_table.DataTable(
        id="tabla-pivot-table",
        data=df.to_dict("records"),
        columns=columns,
        sort_action="native",
        sort_by=[{"column_id": "Monto", "direction": "desc"}],
        css=css_rules,
        style_as_list_view=True,
        style_table={"width": "100%", "tableLayout": "fixed", "overflowX": "auto"},
        style_header={
            "backgroundColor": "#393939",
            "color": "white",
            "textAlign": "center",
            "height": "auto"
        },
        style_cell={
            "backgroundColor": "#2D2D2D",
            "color": "white",
            "textAlign": "center",
            "fontSize": "0.8rem",
            "whiteSpace": "normal",
            "wordWrap": "break-word"
        },
        style_cell_conditional=style_cell_cond,
        style_data_conditional=style_data_cond
    )
