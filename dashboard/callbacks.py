"""Callbacks de actualización del tablero."""

from __future__ import annotations

import logging
import threading
import time
from collections import deque

import numpy as np
import plotly.graph_objects as go
from dash import callback
from dash.dependencies import Input, Output

from acquisition import get_samples, setup
from processing import signal_pipeline
from processing.spectrum import fft_mag
from settings import HW, UI
from standards.iso10816 import zone as iso_zone

logger = logging.getLogger(__name__)

buf_t, buf_v = deque(maxlen=5 * HW.SAMPLE_RATE), deque(maxlen=5 * HW.SAMPLE_RATE)
acc_t, acc_v = deque(maxlen=UI.WINDOW_FFT), deque(maxlen=UI.WINDOW_FFT)
buf_rms = deque(maxlen=UI.WINDOW_RMS)
f_fft, a_fft = None, None


def acquisition_loop() -> None:
    """Lee datos periódicamente."""
    global f_fft, a_fft
    while True:
        seq, raw = get_samples()
        if raw is None:
            continue
        logger.debug("seq=%s shape=%s", seq, raw.shape)
        result = signal_pipeline(raw)
        acc = result["acc_ms2"]
        for m in np.linalg.norm(acc, axis=1):
            acc_t.append(time.time())
            acc_v.append(m)
        buf_t.append(time.time())
        buf_v.extend(result["vel_mm_s"])
        buf_rms.append(result["rms"])
        win = list(buf_v)[-UI.WINDOW_FFT :]
        if len(win) == UI.WINDOW_FFT:
            f_fft, a_fft = fft_mag(np.array(win), HW.SAMPLE_RATE)


def start_acquisition() -> None:
    """Inicia el hilo de adquisición."""
    setup("0.0.0.0", 9000)
    threading.Thread(target=acquisition_loop, daemon=True).start()


@callback(
    [
        Output("accel-graph", "figure"),
        Output("waveform", "figure"),
        Output("spectrum", "figure"),
        Output("rms-trend", "figure"),
        Output("rms-val", "children"),
        Output("peak-val", "children"),
        Output("inst-val", "children"),
        Output("diag-val", "children"),
    ],
    [
        Input("interval", "n_intervals"),
        Input("rpm-input", "value"),
        Input("iso-select", "value"),
    ],
)
def update_dashboard(_n_intervals: int, _rpm: int, iso_group: str):
    _ = (_n_intervals, _rpm)
    fig1 = go.Figure(go.Scatter(x=list(acc_t), y=list(acc_v), mode="lines"))
    fig1.update_layout(
        xaxis_title="Tiempo (s)", yaxis_title="Acc (m/s²)", template="plotly_white"
    )
    fig2 = go.Figure(go.Scatter(x=list(buf_t), y=list(buf_v), mode="lines"))
    fig2.update_layout(
        xaxis_title="Tiempo (s)", yaxis_title="Vel (mm/s)", template="plotly_white"
    )
    fig3 = go.Figure(
        go.Bar(x=f_fft.tolist() if f_fft else [], y=a_fft.tolist() if a_fft else [])
    )
    fig3.update_layout(
        xaxis_title="Frecuencia (Hz)", yaxis_title="Amplitud", template="plotly_white"
    )
    fig4 = go.Figure(
        go.Scatter(x=list(range(len(buf_rms))), y=list(buf_rms), mode="lines")
    )
    fig4.update_layout(
        xaxis_title="Muestras", yaxis_title="RMS (mm/s)", template="plotly_white"
    )
    last = buf_rms[-1] if buf_rms else 0
    peak = f_fft[a_fft.argmax()] if (a_fft is not None and len(a_fft) > 0) else 0
    diag = iso_zone(last, iso_group)
    return (
        fig1,
        fig2,
        fig3,
        fig4,
        f"{last:.2f} mm/s",
        f"{peak:.1f} Hz",
        f"{last:.2f} mm/s",
        diag,
    )