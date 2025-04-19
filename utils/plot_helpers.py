# utils/plot_helpers.py
import plotly.express as px
import plotly.graph_objs as go

def crear_grafico_torta(entidades):
    entidades_filtradas = [e for e in entidades if e.get("monto", 0) > 0]
    entidades_ordenadas = sorted(entidades_filtradas, key=lambda x: x.get("monto", 0), reverse=True)
    if not entidades_ordenadas:
        return {}
    labels = [e["entidad"] for e in entidades_ordenadas]
    sizes = [e["monto"] for e in entidades_ordenadas]
    fig = px.pie(values=sizes, names=labels, title="Distribución de Deuda por Acreedor", hole=0.4)
    fig.update_traces(textposition='inside', textinfo='percent+label')
    fig.update_layout(paper_bgcolor="#2D2D2D", plot_bgcolor="#2D2D2D", font_color="white")
    return fig

def crear_grafico_evolucion(periodos):
    if not periodos:
        return {}
    sorted_periodos = sorted(periodos, key=lambda p: p.get("periodo", ""))
    x_labels = [p["periodo"] for p in sorted_periodos]
    y_values = [sum(e.get("monto", 0) for e in p.get("entidades", [])) * 1000 for p in sorted_periodos]
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=x_labels, y=y_values, mode="lines+markers", name="Deuda Total",
                             line=dict(color="#00bfff")))
    fig.update_layout(title="Evolución de Deuda Total",
                      xaxis_title="Periodo",
                      yaxis_title="Deuda ($)",
                      paper_bgcolor="#2D2D2D",
                      plot_bgcolor="#2D2D2D",
                      font_color="white")
    return fig
