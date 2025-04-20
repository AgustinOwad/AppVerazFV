# test_plot_helpers.py

from utils.plot_helpers import crear_grafico_torta
import plotly.io as pio

# --- Datos de prueba: menos de 6 categorías ---
sample1 = [
    {"entidad": "Banco A", "monto": 41251, "situacion": 2},
    {"entidad": "Banco B", "monto": 3508, "situacion": 3},
    {"entidad": "Banco C", "monto": 402, "situacion": 4},
    {"entidad": "Banco D", "monto": 401,  "situacion": 2},
    {"entidad": "Banco E", "monto": 1100,  "situacion": 5},
    {"entidad": "Banco F", "monto": 2000,  "situacion": 5},
    {"entidad": "Banco G", "monto": 400,  "situacion": 5},
    {"entidad": "Banco H", "monto": 1340,  "situacion": 5},
]

# --- Datos de prueba: 6 o más categorías para fallback a barras ---
sample2 = sample1 + [
    {"entidad": f"Banco Extra{i}", "monto": 30000, "situacion": 3}
    for i in range(1, 3)  # suma 2 más → 7 categorías totales
]

# Elegí cuál probar
#fig = crear_grafico_torta(sample1)
fig = crear_grafico_torta(sample2)

fig.update_layout(
    paper_bgcolor="#2D2D2D",
    plot_bgcolor="#2D2D2D",
)

# Abre la figura en tu navegador
pio.show(fig)

# O guarda en un HTML para inspeccionar:
# pio.write_html(fig, 'debug_torta.html', auto_open=True)
