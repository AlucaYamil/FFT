import dash_bootstrap_components as dbc
from dash import dcc, html

ICON_CDN = "https://cdn.jsdelivr.net/npm/bootstrap-icons@1.9.1/font/bootstrap-icons.css"


def card(title: str, body, color="primary", icon=None):
    header = []
    if icon:
        header.append(html.I(className=f"bi bi-{icon} me-2"))
    header.append(html.Span(title))
    return dbc.Card(
        [
            dbc.CardHeader(html.Div(header, className="d-flex align-items-center")),
            dbc.CardBody(body),
        ],
        color=color,
        className="shadow-sm h-100",
    )


layout = dbc.Container(
    [
        # --- Señales en tiempo ---
        dbc.Row(
            [
                dbc.Col(
                    card(
                        "Acc (m/s²)",
                        dcc.Graph(id="accel-graph"),
                        "info",
                        "speedometer2",
                    ),
                    width=6,
                ),
                dbc.Col(
                    card(
                        "Vel (mm/s)",
                        dcc.Graph(id="vibration-graph"),
                        "secondary",
                        "tachometer",
                    ),
                    width=6,
                ),
            ],
            className="mb-4",
        ),
        # --- FFT y tendencia RMS ---
        dbc.Row(
            [
                dbc.Col(
                    card("FFT", dcc.Graph(id="spectrum"), "warning", "graph-up"),
                    width=6,
                ),
                dbc.Col(
                    card(
                        "RMS – Histórico",
                        dcc.Graph(id="rms-trend"),
                        "danger",
                        "activity",
                    ),
                    width=6,
                ),
            ],
            className="mb-4",
        ),
        # --- Indicadores numéricos (IDs deben coincidir con callbacks) ---
        dbc.Row(
            [
                dbc.Col(
                    card("RMS actual (mm/s)", html.H4(id="rms-val"), color="danger"),
                    width=3,
                ),
                dbc.Col(
                    card(
                        "Frecuencia pico (Hz)", html.H4(id="peak-val"), color="warning"
                    ),
                    width=3,
                ),
                dbc.Col(
                    card("RMS instantáneo", html.H4(id="inst-val"), color="info"),
                    width=3,
                ),
                dbc.Col(
                    card("Zona ISO", html.H4(id="diag-val"), color="success"), width=3
                ),
            ],
            className="mb-4",
        ),
        # --- Panel de configuración ---
        dbc.Row(
            dbc.Col(
                dbc.Card(
                    dbc.CardBody(
                        [
                            html.Label("RPM"),
                            dbc.Input(
                                id="rpm-input",
                                type="number",
                                value=1390,
                                min=0,
                                step=10,
                            ),
                            html.Br(),
                            html.Label("Grupo ISO"),
                            dbc.Select(
                                id="iso-select",
                                options=[
                                    {"label": "G1", "value": "G1"},
                                    {"label": "G2", "value": "G2"},
                                ],
                                value="G1",
                            ),
                        ]
                    ),
                    className="shadow-sm",
                ),
                width=3,
            ),
            className="mb-4",
        ),
        dcc.Interval(id="interval", interval=500, n_intervals=0),
    ],
    fluid=True,
    className="p-4",
)