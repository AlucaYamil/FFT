import logging

import dash
import dash_bootstrap_components as dbc

from dashboard.layout import layout, ICON_CDN
from config import SIMULATED_DATA
from dashboard import callbacks

app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.FLATLY, ICON_CDN],
)
server = app.server
app.layout = layout

callbacks  # ensure callbacks registered

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG, format="%(message)s")
    logging.getLogger().debug("SIMULATED_DATA=%s", SIMULATED_DATA)
    callbacks.start_acquisition()
    app.run(host="0.0.0.0", port=8050, debug=True)