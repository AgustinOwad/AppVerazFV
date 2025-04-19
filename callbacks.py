# callbacks.py

from dash import Output, Input, State, callback_context, no_update, dcc, html
from dash.exceptions import PreventUpdate
import pandas as pd
import dash_bootstrap_components as dbc

from auth import verificar_credenciales
from sql_api import consultar_deuda_historica
from layout import login_layout, dashboard_layout
from utils.data_tables_aggrid import crear_pivot_table_aggrid
from utils.plot_helpers import crear_grafico_torta, crear_grafico_evolucion
from utils.formatter import formatear_periodo

def formatear_cuit(cuit: str) -> str:
    """
    Formatea un CUIT tipo '30687120066' como '30-68712006-6'
    """
    return f"{cuit[:2]}-{cuit[2:10]}-{cuit[10:]}"

def register_callbacks(app):

    @app.callback(
        Output("page-content", "children"),
        Input("url", "pathname"),
        State("current-user", "data"),
    )
    def display_page(pathname, current_user):
        if pathname == "/login" or not current_user:
            return login_layout()
        return dashboard_layout()

    @app.callback(
        Output("login-alert", "children"),
        Output("login-alert", "color"),
        Output("login-alert", "is_open"),
        Output("current-user", "data"),
        Output("url", "pathname"),
        Input("login-button", "n_clicks"),
        Input("login-username", "n_submit"),
        Input("login-password", "n_submit"),
        State("login-username", "value"),
        State("login-password", "value"),
        prevent_initial_call=True
    )
    def login(n_clicks, n_usr, n_pass, usuario, contrasena):
        # Ver qué disparó el callback
        triggered = callback_context.triggered or []
        # Si fue el mounting inicial, no hacer nada
        if all(t["value"] is None for t in triggered):
            raise PreventUpdate

        # 1) Validar campos vacíos
        faltantes = []
        if not usuario:
            faltantes.append("usuario")
        if not contrasena:
            faltantes.append("contraseña")
        if faltantes:
            if len(faltantes) == 1:
                msg = f"Por favor, ingrese su {faltantes[0]}"
            else:
                msg = "Por favor, ingrese usuario y contraseña"
            # No actualizamos URL ni current-user para que la alerta persista
            return msg, "warning", True, None, no_update

        # 2) Verificar credenciales
        user, rol = verificar_credenciales(usuario, contrasena)
        if user:
            # Login exitoso: redirigimos y almacenamos current-user
            return (
                f"✔️ Bienvenido, {user}!",
                "success",
                True,
                {"username": user, "rol": rol},
                "/dashboard"
            )

        # 3) Credenciales inválidas
        return (
            "Credenciales incorrectas",
            "danger",
            True,
            None,
            no_update
        )

    @app.callback(
        Output("login-password", "type"),
        Input("toggle-pass", "n_clicks"),
        State("login-password", "type"),
        prevent_initial_call=True
    )
    def toggle_password(n_clicks, tipo):
        return "text" if tipo == "password" else "password"

    @app.callback(
        Output("consulta-message", "children"),
        Output("tabla-pivot", "children"),
        Output("grafico-torta", "children"),
        Output("grafico-evolucion", "children"),
        Output("tabla-detalle", "children"),
        Output("input-cuit", "value"),
        Input("consultar-button", "n_clicks"),
        Input("input-cuit", "n_submit"),
        State("input-cuit", "value"),
        prevent_initial_call=True
    )
    def ejecutar_consulta(n_clicks, n_submit, cuit):
        if not cuit or not cuit.isdigit() or len(cuit) != 11:
            msg = dbc.Alert(
                [
                    html.Span("❌", className="me-2"),
                    html.Span("CUIT inválido.")
                ],
                color="danger",
                dismissable=False,
                className="py-2 px-3 mt-3",
                style={
                    "backgroundColor": "#dc354510",
                    "border": "1px solid #dc354555",
                    "color": "#dc3545",
                    "fontWeight": "500",
                    "borderRadius": "0.5rem",
                }
            )
            return msg, no_update, no_update, no_update, no_update, ""

        data = consultar_deuda_historica(cuit)
        if "error" in data:
            msg = dbc.Alert(
                [
                    html.Span("❌", className="me-2"),
                    html.Span(f"Error: {data['error']}")
                ],
                color="danger",
                dismissable=False,
                className="py-2 px-3 mt-3",
                style={
                    "backgroundColor": "#dc354510",
                    "border": "1px solid #dc354555",
                    "color": "#dc3545",
                    "fontWeight": "500",
                    "borderRadius": "0.5rem",
                }
            )
            return msg, no_update, no_update, no_update, no_update, ""

        if not data.get("periodos"):
            msg = dbc.Alert(
                [
                    html.Span("❌", className="me-2"),
                    html.Span("El CUIT consultado no tiene información disponible.")
                ],
                color="danger",
                dismissable=False,
                className="py-2 px-3 mt-3",
                style={
                    "backgroundColor": "#dc354510",
                    "border": "1px solid #dc354555",
                    "color": "#dc3545",
                    "fontWeight": "500",
                    "borderRadius": "0.5rem",
                }
            )
            return msg, no_update, no_update, no_update, no_update, ""


        razon_social = data["denominacion"]
        cuit_formateado = formatear_cuit(str(cuit))  # aseguramos que sea string

        msg = dbc.Alert(
            [
                html.Span("✔", className="me-2"),
                html.Strong("Datos para: "),
                html.Span(f"{razon_social} ", className="me-2"),
                html.Span(f"(CUIT: {cuit_formateado})", className="text-muted")
            ],
            color="info",
            dismissable=False,
            className="py-2 px-3 mt-3",
            style={
                "backgroundColor": "#0d6efd10",
                "border": "1px solid #0d6efd55",
                "color": "#0d6efd",
                "fontWeight": "500",
                "borderRadius": "0.5rem",
            }
        )

        table = crear_pivot_table_aggrid(data["periodos"])
        torta = dcc.Graph(figure=crear_grafico_torta(
            sorted(data["periodos"], key=lambda p: p["periodo"], reverse=True)[0]["entidades"]
        ))
        evo = dcc.Graph(figure=crear_grafico_evolucion(data["periodos"]))

        header = html.Thead(html.Tr([
            html.Th("Mes-Año"), html.Th("Entidad"),
            html.Th("Monto ($)"), html.Th("Situación")
        ]))
        rows = []
        for p in sorted(data["periodos"], key=lambda x: x["periodo"], reverse=True):
            mes_ano = formatear_periodo(p["periodo"])
            for ent in p["entidades"]:
                m = int(ent["monto"] * 1000)
                rows.append(html.Tr([
                    html.Td(mes_ano),
                    html.Td(ent["entidad"]),
                    html.Td(f"${m:,.0f}".replace(",", ".")),
                    html.Td(ent.get("situacion", "-"))
                ]))
        detalle = dbc.Table(
            [header] + rows,
            striped=True, bordered=True, hover=True, responsive=True
        )

        return msg, table, torta, evo, detalle,""

    @app.callback(
        Output("download-excel", "data"),
        Input("export-excel", "n_clicks"),
        State("tabla-pivot-table", "data"),
        prevent_initial_call=True
    )
    def exportar_excel(n, data):
        df = pd.DataFrame(data)
        return dcc.send_data_frame(df.to_excel, "tabla_unificada.xlsx", index=False)
