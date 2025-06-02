import dash
import dash_bootstrap_components as dbc
from dashboard.layout import layout, ICON_CDN
import importlib                                   # evita “unused import”

app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.FLATLY, ICON_CDN],
)
server     = app.server
app.layout = layout

importlib.import_module("dashboard.callbacks")     # registra callbacks

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8050, debug=True)
