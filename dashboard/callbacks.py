import logging
import threading
import time
from collections import deque

import numpy as np
import plotly.graph_objects as go
from dash import callback
from dash.dependencies import Input, Output

from config import SIMULATED_DATA
from processing.integration import accel_to_velocity
from processing.metrics import rms, magnitude_mm_s
from processing.spectrum import fft_mag
from settings import HW, UI
from standards.iso10816 import zone as iso_zone

if SIMULATED_DATA == 1:
    from acquisition import simulator as data_source
else:
    from acquisition import udp_receiver as data_source

setup_udp = data_source.setup_udp
receive_batch = data_source.receive_batch

logger = logging.getLogger(__name__)

sock = None
buf_t, buf_v = deque(maxlen=5 * HW.SAMPLE_RATE), deque(maxlen=5 * HW.SAMPLE_RATE)
acc_t, acc_v = deque(maxlen=UI.WINDOW_FFT), deque(maxlen=UI.WINDOW_FFT)
buf_rms = deque(maxlen=UI.WINDOW_RMS)
f_fft, a_fft = None, None


def acquisition_loop():
    global f_fft, a_fft
    while True:
        seq, raw = receive_batch(sock)
        if raw is None:
            continue
        logger.debug("[UDP] seq=%s, shape=%s", seq, raw.shape)

        acc = raw * HW.LSB_TO_G * HW.G_TO_MS2
        mag = np.linalg.norm(acc, axis=1)
        for m in mag:
            acc_t.append(time.time())
            acc_v.append(m)

        vel_arr = accel_to_velocity(acc, HW.DT)
        vel_mag = np.linalg.norm(vel_arr, axis=1)
        vel_mm_s = magnitude_mm_s(vel_mag)
        buf_t.append(time.time())
        buf_v.extend(vel_mm_s)
        buf_rms.append(rms(vel_mm_s))

        win = list(buf_v)[-UI.WINDOW_FFT :]
        if len(win) == UI.WINDOW_FFT:
            f_fft, a_fft = fft_mag(np.array(win), HW.SAMPLE_RATE)


def start_acquisition():
    global sock
    if SIMULATED_DATA == 0:
        sock = setup_udp("0.0.0.0", 9000)
    else:
        sock = None
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
def update_dashboard(_n_intervals, _rpm, iso_group):
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