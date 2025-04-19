import dash
from dash import html
import dash_bootstrap_components as dbc
from flask import Flask
from layout import serve_layout
from callbacks import register_callbacks

server = Flask(__name__)
server.secret_key = "S3cr3tK3y"

app = dash.Dash(
    __name__,
    server=server,
    external_stylesheets=[dbc.themes.DARKLY],
    suppress_callback_exceptions=True
)
app.title = "FV - App Veraz"
app.layout = serve_layout

register_callbacks(app)

if __name__ == "__main__":
    app.run(debug=True)
