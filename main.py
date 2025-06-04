import logging

import dash
import dash_bootstrap_components as dbc

from dashboard.layout import ICON_CDN, layout
from config import SIMULATED
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
    logging.getLogger().debug("SIMULATED=%s", SIMULATED)
    callbacks.start_acquisition()
    app.run(host="0.0.0.0", port=8050, debug=True)