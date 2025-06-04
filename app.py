"""
Archivo: app.py

Este dashboard rudimentario en Dash permite monitorear en tiempo real los datos de
velocidad y el espectro FFT generados por el pipeline de vibraciones. Lee periódicamente
los archivos CSV “velocity.csv” y “fft_result.csv” y actualiza dos gráficos:
1) Serie de velocidad (mm/s) para los ejes X, Y, Z.
2) Espectro FFT (amplitud vs. frecuencia) para los ejes X, Y, Z.

Requisitos:
- Instalar Dash y pandas:
    pip install dash pandas plotly

Para ejecutar:
    python app.py
Luego abrir el navegador en http://127.0.0.1:8050/
"""

import dash
from dash import html, dcc, Output, Input
import pandas as pd
import plotly.graph_objs as go

# Inicializar la aplicación Dash
app = dash.Dash(__name__)
app.title = "Monitoreo de Vibraciones en Tiempo Real"

# Layout del dashboard
app.layout = html.Div(
    style={"font-family": "Arial, sans-serif", "margin": "20px"},
    children=[
        html.H1("Dashboard de Monitoreo de Condición"),
        html.P("Estos gráficos se actualizan cada segundo, leyendo los CSV generados "
               "por el pipeline de vibraciones."),

        # Gráfico de velocidad en el tiempo
        html.Div([
            html.H2("Señal de Velocidad (mm/s)"),
            dcc.Graph(id="live-velocity-graph"),
        ], style={"margin-bottom": "40px"}),

        # Gráfico del espectro FFT
        html.Div([
            html.H2("Espectro FFT (mm/s)"),
            dcc.Graph(id="live-fft-graph"),
        ], style={"margin-bottom": "40px"}),

        # Intervalo para actualización automática (1000 ms = 1 s)
        dcc.Interval(
            id="interval-component",
            interval=1000,
            n_intervals=0
        ),
    ],
)


@app.callback(
    Output("live-velocity-graph", "figure"),
    Output("live-fft-graph", "figure"),
    Input("interval-component", "n_intervals")
)
def update_graphs(n):
    """
    Cada vez que se dispare el Interval (cada segundo), esta función:
    - Lee velocity.csv y fft_result.csv
    - Construye dos figuras Plotly:
        1) velocity_fig: gráfico de líneas de vx, vy, vz vs. time.
        2) fft_fig: gráfico de líneas de amp_x, amp_y, amp_z vs. frequency.
    """
    # 1) Leer CSV de velocidad
    try:
        df_vel = pd.read_csv("velocity.csv")
    except Exception:
        empty_fig = go.Figure()
        empty_fig.update_layout(
            title="No se encontró velocity.csv",
            xaxis_title="time (s)",
            yaxis_title="velocity (mm/s)"
        )
        return empty_fig, empty_fig

    # 2) Leer CSV de FFT
    try:
        df_fft = pd.read_csv("fft_result.csv")
    except Exception:
        empty_fig = go.Figure()
        empty_fig.update_layout(
            title="No se encontró fft_result.csv",
            xaxis_title="frequency (Hz)",
            yaxis_title="amplitude (mm/s)"
        )
        velocity_fig = go.Figure()
        velocity_fig.add_trace(go.Scatter(
            x=df_vel["time"], y=df_vel["vx"], mode="lines", name="Vx"
        ))
        velocity_fig.add_trace(go.Scatter(
            x=df_vel["time"], y=df_vel["vy"], mode="lines", name="Vy"
        ))
        velocity_fig.add_trace(go.Scatter(
            x=df_vel["time"], y=df_vel["vz"], mode="lines", name="Vz"
        ))
        velocity_fig.update_layout(
            xaxis_title="Tiempo (s)",
            yaxis_title="Velocidad (mm/s)",
            margin={"l": 40, "r": 10, "t": 40, "b": 40}
        )
        return velocity_fig, empty_fig

    # --- Construir figura de velocidad ---
    velocity_fig = go.Figure()
    velocity_fig.add_trace(go.Scatter(
        x=df_vel["time"],
        y=df_vel["vx"],
        mode="lines",
        name="Vx"
    ))
    velocity_fig.add_trace(go.Scatter(
        x=df_vel["time"],
        y=df_vel["vy"],
        mode="lines",
        name="Vy"
    ))
    velocity_fig.add_trace(go.Scatter(
        x=df_vel["time"],
        y=df_vel["vz"],
        mode="lines",
        name="Vz"
    ))
    velocity_fig.update_layout(
        title="Velocidad vs Tiempo",
        xaxis_title="Tiempo (s)",
        yaxis_title="Velocidad (mm/s)",
        margin={"l": 40, "r": 10, "t": 40, "b": 40}
    )

    # --- Construir figura de FFT ---
    fft_fig = go.Figure()
    fft_fig.add_trace(go.Scatter(
        x=df_fft["frequency"],
        y=df_fft["amp_x"],
        mode="lines",
        name="Amp X"
    ))
    fft_fig.add_trace(go.Scatter(
        x=df_fft["frequency"],
        y=df_fft["amp_y"],
        mode="lines",
        name="Amp Y"
    ))
    fft_fig.add_trace(go.Scatter(
        x=df_fft["frequency"],
        y=df_fft["amp_z"],
        mode="lines",
        name="Amp Z"
    ))
    fft_fig.update_layout(
        title="Espectro FFT",
        xaxis_title="Frecuencia (Hz)",
        yaxis_title="Amplitud (mm/s)",
        margin={"l": 40, "r": 10, "t": 40, "b": 40}
    )

    return velocity_fig, fft_fig


if __name__ == "__main__":
    # Iniciar el servidor Dash usando app.run en lugar de app.run_server
    app.run(debug=True)
