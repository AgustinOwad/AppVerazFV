# utils/plot_helpers.py

import plotly.express as px
import plotly.graph_objs as go
import textwrap

# Paleta corporativa de tres tonos
CORP_PALETTE = ["#0d6efd", "#DFA83D", "#947F57"]

def crear_grafico_torta(entidades):
    """
    - Agrupa en “Otros” todo slice < 3 %.
    - Pull dinámico (0.04) en slices < 10 %.
    - Texto externo con salto de línea (máx 2 renglones) + "% ($valor)".
    """
    # 1) Filtrar y escalar
    data = [e for e in entidades if e.get("monto", 0) > 0]
    for e in data:
        e["_valor"] = e["monto"] * 1000

    # 2) Ordenar desc.
    data.sort(key=lambda x: x["_valor"], reverse=True)
    if not data:
        return {}

    total = sum(e["_valor"] for e in data)

    # 3) Fallback a barras si ≥ 6 categorías
    if len(data) >= 6:
        # 1) Agrupar < 3% en “Otros”
        total = sum(e["_valor"] for e in data)
        mayores, otros_sum = [], 0
        for e in data:
            if e["_valor"] / total < 0.03:
                otros_sum += e["_valor"]
            else:
                mayores.append((e["entidad"], e["_valor"], e.get("situacion", "-")))
        if otros_sum > 0:
            mayores.insert(0, ("Otros", otros_sum, "N/A"))  # “Otros” siempre primero

        # 2) Desempaquetar y reordenar: “Otros” arriba, resto ASC por monto
        others,*rest = mayores
        rest_sorted = sorted(rest, key=lambda x: x[-1])  # de menor monto a mayor
        ordered =  rest_sorted +[others] 
        labels, sizes, situations = zip(*ordered)

        # 3) Preparar textos: 2 líneas de nombre + 3ª línea "% ($valor)"
        wrapped = [textwrap.wrap(lbl, width=20)[:2] for lbl in labels]
        wrapped_html = ["<br>".join(lines) for lines in wrapped]
        formatted = [f"{int(v):,}".replace(",", ".") for v in sizes]
        percent    = [f"{100*v/total:.1f}%"       for v in sizes]
        texts = [
            f"{wrapped_html[i]}<br>{percent[i]} ($ {formatted[i]})"
            for i in range(len(labels))
        ]

        # 4) Crear manualmente el gráfico de barras horizontal para asegurar hover/textos correctos
        textpos = ["inside" if v/total >= 0.10 else "outside" for v in sizes]
        fig = go.Figure(
            go.Bar(
                x=sizes,
                y=list(labels),
                orientation="h",
                marker_color=[CORP_PALETTE[i % len(CORP_PALETTE)] for i in range(len(labels))],
                marker_line_color="#2D2D2D",
                marker_line_width=1,
                text=texts,                     # Textos ya alineados uno a uno
                textposition=textpos,
                textangle=0,                    # Fuerza horizontal
                customdata=list(situations),    # Situación por cada barra (incluye "N/A")
                hovertemplate=(
                    "%{y}<br>"
                    "Situación: %{customdata}<br>"
                    "Monto: $%{x:,.0f}"
                    "<extra></extra>"
                ),
            )
        )
        # 5) Ejes y layout (conservamos exactamente tu configuración aprobada)
        fig.update_yaxes(
            showticklabels=False,
            title_text="Acreedores",
            categoryorder="array",
            categoryarray=list(labels)
        )
        fig.update_xaxes(
            tickformat="~s",
            tickprefix="$",
            ticks="outside",
            gridcolor="#424242"
        )
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font_color="white",
            showlegend=False,
            margin=dict(l=20, r=20, t=0, b=50),
            transition={"duration": 500, "easing": "cubic-in-out"}
        )
        fig.add_annotation(
            text="Fuente: API BCRA – Central de Deudores",
            x=0.5,y=-0.11,xref="paper",yref="paper",
            showarrow=False,font=dict(size=11,color="white")
        )
        return fig

    # 4) Agrupar <3% en “Otros”
    mayores, otros = [], 0
    for e in data:
        if e["_valor"]/total < 0.03:
            otros += e["_valor"]
        else:
            mayores.append((e["entidad"], e["_valor"], e.get("situacion","-")))
    if otros > 0:
        mayores.append(("Otros", otros, "N/A"))

    # 5) Desempaquetar
    labels     = [m[0] for m in mayores]
    sizes      = [m[1] for m in mayores]
    situations = [m[2] for m in mayores]
    colors     = [CORP_PALETTE[i % 3] for i in range(len(labels))]

    # 6) Pull para <10%
    pulls = [0.04 if size/total < 0.10 else 0 for size in sizes]

    # 7) Textos
    wrapped       = [textwrap.wrap(lbl,20)[:2] for lbl in labels]
    wrapped_html  = ["<br>".join(w) for w in wrapped]
    formatted     = [f"{int(v):,}".replace(",",".") for v in sizes]
    percent_vals  = [f"{100*v/total:.1f}%" for v in sizes]
    texts         = [
        f"{wrapped_html[i]}<br>{percent_vals[i]} ($ {formatted[i]})"
        for i in range(len(labels))
    ]

    # 8) Pie
    fig = px.pie(
        values=sizes,
        names=labels,
        hole=0.4,
        color_discrete_sequence=colors
    )
    
    fig.data[0].rotation = 90

    fig.update_traces(
        text=texts,
        textinfo="text",
        textposition="outside",
        pull=pulls,
        textfont=dict(size=10),
        marker=dict(line=dict(color="#2D2D2D",width=1)),
        hovertemplate="Situación: %{customdata}<extra></extra>",
        customdata=situations
    )
    # inyectar el conector en el primer trace (si la versión de Plotly lo soporta)
    try:
        fig.data[0].update(connector=dict(visible=True, line=dict(color="white", width=1)))
    except ValueError:
        # la propiedad connector no existe en esta versión
        pass

    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font_color="white", showlegend=False,
        margin=dict(l=20,r=20,t=0,b=0),
        separators=".,",
        uniformtext_mode="hide",
        uniformtext_minsize=8,
        transition={"duration":500,"easing":"cubic-in-out"}
    )
    fig.add_annotation(
        text="Fuente: API BCRA – Central de Deudores",
        x=0.5,y=-0.01,xref="paper",yref="paper",
        showarrow=False,font=dict(size=11,color="white")
    )
    return fig


def crear_grafico_evolucion(periodos):
    if not periodos:
        return {}
    sorted_p = sorted(periodos, key=lambda p:p.get("periodo",""))
    x = [p["periodo"] for p in sorted_p]
    y = [sum(e.get("monto",0) for e in p["entidades"])*1000 for p in sorted_p]

    fig = go.Figure(
        go.Scatter(x=x,y=y,mode="lines+markers",name="Deuda Total",
                   line=dict(color="#00bfff"))
    )
    fig.update_layout(
        xaxis_title="Periodo", yaxis_title="Deuda ($)",
        paper_bgcolor="#2D2D2D", plot_bgcolor="#2D2D2D",
        font_color="white",
        margin=dict(l=40,r=20,t=0,b=40)
    )
    return fig
