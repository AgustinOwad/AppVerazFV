# utils/plot_helpers.py

import plotly.express as px
import plotly.graph_objs as go
import textwrap
from datetime import datetime

# Paleta corporativa de tres tonos
CORP_PALETTE = ["#0d6efd", "#DFA83D", "#947F57"]


def crear_grafico_torta(entidades):
    """
    - Agrupa en “Otros” todo slice < 3 %.
    - Pull dinámico (0.04) en slices < 10 %.
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
        # 1) Agrupar < 3% en “Otros”
        mayores, otros_sum = [], 0
        for e in data:
            if e["_valor"] / total < 0.03:
                otros_sum += e["_valor"]
            else:
                mayores.append((e["entidad"], e["_valor"], e.get("situacion", "-")))
        if otros_sum > 0:
            mayores.insert(0, ("Otros", otros_sum, "N/A"))

        # 2) Desempaquetar y reordenar: “Otros” arriba, resto ASC
        others, *rest = mayores
        rest_sorted = sorted(rest, key=lambda x: x[-1])
        ordered = rest_sorted + [others]
        labels, sizes, situations = zip(*ordered)

        # 3) Textos multilínea
        wrapped = [textwrap.wrap(lbl, width=20)[:2] for lbl in labels]
        wrapped_html = ["<br>".join(lines) for lines in wrapped]
        formatted = [f"{int(v):,}".replace(",", ".") for v in sizes]
        percent = [f"{100 * v / total:.1f}%" for v in sizes]
        texts = [
            f"{wrapped_html[i]}<br>{percent[i]} ($ {formatted[i]})"
            for i in range(len(labels))
        ]

        # 4) Gráfico de barras horizontal
        textpos = ["inside" if v / total >= 0.10 else "outside" for v in sizes]
        fig = go.Figure(
            go.Bar(
                x=sizes,
                y=list(labels),
                orientation="h",
                marker_color=[CORP_PALETTE[i % len(CORP_PALETTE)] for i in range(len(labels))],
                marker_line_color="#2D2D2D",
                marker_line_width=1,
                text=texts,
                textposition=textpos,
                textangle=0,
                customdata=list(situations),
                hovertemplate=(
                    "%{y}<br>"
                    "Situación: %{customdata}<br>"
                    "Monto: $%{x:,.0f}"
                    "<extra></extra>"
                ),
            )
        )
        # 5) Ejes y layout
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
            x=0.5, y=-0.11, xref="paper", yref="paper",
            showarrow=False, font=dict(size=11, color="white")
        )
        return fig

    # 4) Agrupar < 3% en “Otros”
    mayores, otros = [], 0
    for e in data:
        if e["_valor"] / total < 0.03:
            otros += e["_valor"]
        else:
            mayores.append((e["entidad"], e["_valor"], e.get("situacion", "-")))
    if otros > 0:
        mayores.append(("Otros", otros, "N/A"))

    # 5) Desempaquetar
    labels = [m[0] for m in mayores]
    sizes = [m[1] for m in mayores]
    situations = [m[2] for m in mayores]
    colors = [CORP_PALETTE[i % 3] for i in range(len(labels))]

    # 6) Pull para <10%
    pulls = [0.04 if size / total < 0.10 else 0 for size in sizes]

    # 7) Textos multilínea
    wrapped = [textwrap.wrap(lbl, 20)[:2] for lbl in labels]
    wrapped_html = ["<br>".join(w) for w in wrapped]
    formatted = [f"{int(v):,}".replace(",", ".") for v in sizes]
    percent_vals = [f"{100 * v / total:.1f}%" for v in sizes]
    texts = [
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
        marker=dict(line=dict(color="#2D2D2D", width=1)),
        hovertemplate="Situación: %{customdata}<extra></extra>",
        customdata=situations
    )
    try:
        fig.data[0].update(connector=dict(visible=True, line=dict(color="white", width=1)))
    except ValueError:
        pass
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font_color="white",
        showlegend=False,
        margin=dict(l=20, r=20, t=0, b=0),
        separators=".,",
        uniformtext_mode="hide",
        uniformtext_minsize=8,
        transition={"duration": 500, "easing": "cubic-in-out"}
    )
    fig.add_annotation(
        text="Fuente: API BCRA – Central de Deudores",
        x=0.5, y=-0.01, xref="paper", yref="paper",
        showarrow=False, font=dict(size=11, color="white")
    )
    return fig

def crear_grafico_evolucion(periodos):
    if not periodos:
        return {}

    # 1) Orden cronológico y parse de fechas
    sorted_p   = sorted(periodos, key=lambda p: p.get("periodo", ""))
    period_dates = [datetime.strptime(p["periodo"], "%Y%m") for p in sorted_p]

    # 2) Valores en pesos
    valores = [
        sum(e.get("monto", 0) for e in p["entidades"]) * 1000
        for p in sorted_p
    ]

    # 3) Scatter línea corporativa
    fig = go.Figure(
        go.Scatter(
            x=period_dates,
            y=valores,
            mode="lines+markers",
            name="Deuda Total",
            line_color="#6da8fd"
        )
    )

    # 4) Eje X principal: mes abreviado, dtick mensual
    fig.update_xaxes(
        type="date",
        title_text="Mes",
        dtick="M1",
        tickformat="%b",
        showgrid=False,
        ticks="outside"
    )

    # 5) Eje Y
    fig.update_yaxes(
        title_text="Deuda en pesos",
        tickformat="~s",
        tickprefix="$",
        ticks="outside",
        gridcolor="#5c5c5c"
    )

    # 6) Layout general + eje X secundario solo con los años en enero
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font_color="white",
        # Margen inferior aumentado para que entren los dos ejes
        margin=dict(l=40, r=20, t=0, b=100),
        xaxis2=dict(
            type="date",
            title_text="",
            tickmode="array",
            tickvals=[d for d in period_dates if d.month == 1],
            ticktext=[str(d.year) for d in period_dates if d.month == 1],
            overlaying="x",
            side="bottom",
            anchor="y",
            position=0,
            # Pintamos encima para que no quede oculto tras nada
            layer="above traces",
            showgrid=False,
            ticks="outside",
            tickfont=dict(size=11, color="white")
        )
    )

    return fig