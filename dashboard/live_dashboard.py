from __future__ import annotations

import os
import socket
import numpy as np
import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
import plotly.graph_objs as go

from acquisition.udp_receiver import get_packet
from conversion import acc_to_velocity
from signal_processing import apply_hanning_window, compute_fft, compute_rms
from calibration import calibration

FS = 800
BUFFER = np.zeros((FS, 3), dtype=float)

app = dash.Dash(__name__)
app.title = "Monitor de Vibraciones"

app.layout = html.Div(
    [
        html.H2("Monitoreo de Vibraciones"),
        html.Div(
            [
                html.Button("Calibrar (offset)", id="btn-cal", n_clicks=0),
                html.Button("Apagar servidor", id="btn-stop", n_clicks=0),
            ],
            style={"margin": "10px"},
        ),
        dcc.Graph(id="time-graph"),
        dcc.Graph(id="rms-graph"),
        dcc.Graph(id="fft-graph"),
        dcc.Interval(id="timer", interval=500, n_intervals=0),
        dcc.Store(id="rms-store", data=[]),
    ]
)


def _process_packet() -> np.ndarray:
    try:
        _, data = get_packet(timeout=0.05)
    except socket.timeout:
        return np.zeros((0, 3))
    vel = acc_to_velocity(data.astype(float), FS)
    for sample in vel:
        if calibration.capturing:
            calibration.add_sample(sample)
    if calibration.is_complete():
        calibration.compute_offset()
    vel -= calibration.offset
    return vel


@app.callback(
    Output("time-graph", "figure"),
    Output("fft-graph", "figure"),
    Output("rms-store", "data"),
    Input("timer", "n_intervals"),
    State("rms-store", "data"),
)
def update_signals(_, rms_history):
    global BUFFER
    new_vel = _process_packet()
    if new_vel.size:
        BUFFER = np.vstack([BUFFER[len(new_vel) :], new_vel])
    rms_val = compute_rms(BUFFER)
    rms_history = (rms_history or []) + [rms_val.tolist()]

    freqs, amps = compute_fft(apply_hanning_window(BUFFER), FS)

    t = np.arange(BUFFER.shape[0]) / FS
    fig_time = go.Figure()
    for i, axis in enumerate("XYZ"):
        fig_time.add_trace(go.Scatter(x=t, y=BUFFER[:, i], mode="lines", name=axis))
    fig_time.update_layout(xaxis_title="Tiempo (s)", yaxis_title="Velocidad (mm/s)")

    fig_fft = go.Figure()
    for i, axis in enumerate("XYZ"):
        fig_fft.add_trace(go.Scatter(x=freqs, y=amps[:, i], mode="lines", name=axis))
    fig_fft.update_layout(xaxis_title="Frecuencia (Hz)", yaxis_title="Amplitud (mm/s)")

    return fig_time, fig_fft, rms_history


@app.callback(Output("rms-graph", "figure"), Input("rms-store", "data"))
def draw_rms(data):
    fig = go.Figure()
    if data:
        arr = np.array(data)
        x = list(range(len(arr)))
        for i, axis in enumerate("XYZ"):
            fig.add_trace(go.Scatter(x=x, y=arr[:, i], mode="lines", name=axis))
    fig.update_layout(xaxis_title="Iteración", yaxis_title="RMS (mm/s)")
    return fig


@app.callback(
    Output("btn-cal", "disabled"),
    Input("btn-cal", "n_clicks"),
    Input("btn-stop", "n_clicks"),
    Input("timer", "n_intervals"),
    prevent_initial_call=True,
)
def manage_controls(cal_clicks, stop_clicks, _):
    ctx = dash.callback_context
    if not ctx.triggered:
        return calibration.capturing
    trigger = ctx.triggered[0]["prop_id"].split(".")[0]
    if trigger == "btn-cal":
        calibration.start_capture()
        return True
    if trigger == "btn-stop":
        os._exit(0)
    if calibration.is_complete():
        calibration.compute_offset()
        return False
    return calibration.capturing


def run_dashboard():
    app.run(debug=True)


if __name__ == "__main__":
    run_dashboard()