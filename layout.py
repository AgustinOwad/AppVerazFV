# layout.py

from dash import html, dcc
import dash_bootstrap_components as dbc

def login_layout():
    return dbc.Container(
        [
            dbc.Card(
                [
                    html.Div(
                        html.Img(
                            src="/assets/images/FVLawFirmLogo.png",
                            style={"height": "80px", "marginBottom": "1rem"}
                        ),
                        className="d-flex justify-content-center mt-4"
                    ),

                    html.H2("Iniciar Sesión", className="text-center mb-3"),

                    dbc.CardBody(
                        [
                            dbc.Form(
                                [
                                    dbc.Label("Usuario", html_for="login-username"),
                                    dbc.Input(
                                        id="login-username",
                                        placeholder="Ingrese su usuario",
                                        type="text",
                                        autoFocus=True
                                    ),
                                    dbc.Label("Contraseña", html_for="login-password", className="mt-3"),
                                    dbc.InputGroup(
                                        [
                                            dbc.Input(
                                                id="login-password",
                                                placeholder="Ingrese su contraseña",
                                                type="password"
                                            ),
                                            dbc.InputGroupText(
                                                html.I(className="bi bi-eye-fill", id="toggle-pass"),
                                                style={"cursor": "pointer"}
                                            )
                                        ]
                                    ),
                                    dbc.Button(
                                        "Iniciar Sesión",
                                        id="login-button",
                                        color="primary",
                                        className="mt-4 w-100"
                                    ),
                                ]
                            ),

                            # Espacio reservado para la alerta (altura fija)
                            html.Div(
                                dbc.Alert(
                                    id="login-alert",
                                    is_open=False,
                                    dismissable=True,
                                    duration=4000,
                                    style={
                                        "width": "100%",
                                        "whiteSpace": "normal",
                                        "wordBreak": "break-word",
                                        "padding": "0.5rem 1rem",
                                        "display": "flex",
                                        "alignItems": "center",
                                        "minHeight": "42px",  # <- este ajuste sutil lo centra
                                        "lineHeight": "1.3"   # <- opcional, mejora alineación tipográfica
                                    }
                                ),
                                style={"height": "50px", "marginTop": "1rem", "width": "100%"}
                            )

                        ]
                    )
                ],
                className="animate__animated animate__fadeInDown",
                style={
                    "maxWidth": "400px",
                    "borderRadius": "1rem",
                    "boxShadow": "0 4px 12px rgba(0,0,0,0.2)"
                }
            )
        ],
        fluid=True,
        className="d-flex justify-content-center align-items-center",
        style={
            "height": "100vh",
            "background": "linear-gradient(135deg, rgb(19,30,61), #2c3e50, #4ca1af)"
        }
    )


def header():
    return dbc.Navbar(
        html.Div(  # Reemplazamos dbc.Container por html.Div + clases
            html.Div(
                [
                    # CUIT + botón
                    html.Div(
                        dbc.InputGroup(
                            [
                                dbc.Input(
                                    id="input-cuit",
                                    placeholder="CUIT/CUIL (11 dígitos)",
                                    type="text",
                                    style={
                                        "borderRadius": "1rem 0 0 1rem",
                                        "paddingLeft": "1rem",
                                        "flex": "1"
                                    }
                                ),
                                dbc.Button(
                                    "Consultar",
                                    id="consultar-button",
                                    color="primary",
                                    style={
                                        "borderRadius": "0 1rem 1rem 0",
                                        "paddingLeft": "1.5rem",
                                        "paddingRight": "1.5rem"
                                    }
                                ),
                            ],
                            style={"width": "330px"},
                            className="me-0"
                        ),
                        className="d-flex align-items-center"
                    ),

                    # Título + Divider + Logo
                    html.Div(
                        [
                            html.H2(
                                "CONSULTA DE DEUDAS BCRA",
                                className="m-0 me-3 text-end",
                                style={"fontSize": "1.7rem", "color": "white"}
                            ),
                            html.Div(
                                style={
                                    "borderLeft": "1px solid rgba(255,255,255,0.3)",
                                    "height": "64px",
                                    "margin": "0 1rem"
                                }
                            ),
                            html.Img(
                                src="/assets/images/FVLawFirmLogo.png",
                                style={"height": "64px", "width": "auto"}
                            ),
                        ],
                        className="d-flex align-items-center justify-content-end ms-auto"
                    ),
                ],
                className="d-flex justify-content-between w-100"
            ),
            className="container-fluid px-2"  # Eliminamos padding y max-width indeseado
        ),
        color="dark",
        dark=True,
        sticky="top",
        className="py-2"
    )


def dashboard_layout():
    return html.Div(
        [
            # HEADER SIN MÁRGENES NI PADDING
            header(),

            # CONTENIDO CON MÁRGENES LATERALES
            html.Div(
                [
                    html.Div(id="consulta-message", className="mt-3"),
                    dbc.Card(
                        [
                            dbc.CardHeader(
                                dbc.Row(
                                    [
                                        dbc.Col(html.Span("Tabla Unificada", className="fw-bold")),
                                        dbc.Col(
                                            dbc.Button("Exportar a Excel", id="export-excel", color="secondary", size="sm"),
                                            width="auto",
                                            className="ms-auto"
                                        )
                                    ],
                                    align="center",
                                )
                            ),
                            dbc.CardBody(html.Div(id="tabla-pivot"))
                        ],
                        className="mb-4"
                    ),
                    dbc.Row(
                         [
                             dbc.Col(
                                dbc.Card(
                                    [
                                        dbc.CardHeader("Distribución por Acreedor"),
                                        # Hacemos que el CardBody sea flex column
                                        dbc.CardBody(
                                            html.Div(id="grafico-torta"),
                                            style={
                                                "display": "flex",
                                                "flexDirection": "column",
                                                "height": "100%",  # occupe todo el Card
                                                "padding": "0"
                                            }
                                        )
                                    ],
                                    style={"height": "100%"}  # El Card ocupa todo el Col
                                ),
                                md=6,
                                style={"height": "450px"}  # o el valor que prefieras
                            ),
                             dbc.Col(
                                 dbc.Card(
                                     [
                                         dbc.CardHeader("Evolución Total"),
                                         dbc.CardBody(html.Div(id="grafico-evolucion"))
                                     ]
                                 ),
                                 md=6
                             ),
                         ],
                         className="mb-4"
                     ),
                    dbc.Card(
                        [
                            dbc.CardHeader("Detalle Mes-Año por Entidad"),
                            dbc.CardBody(html.Div(id="tabla-detalle"))
                        ]
                    )
                ],
                style={
                    "paddingLeft": "10px",
                    "paddingRight": "10px"
                }
            )
        ],
        style={
            "padding": "0",
            "margin": "0",
            "width": "100%"
        }
    )


def serve_layout():
    return html.Div(
        [
            dcc.Location(id="url", refresh=False),
            dcc.Store(id="current-user"),
            html.Div(id="page-content")
        ]
    )
