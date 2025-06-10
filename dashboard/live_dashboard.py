import os, sys, socket, numpy as np
import dash
from dash import dcc, html
import plotly.graph_objs as go
from dash.dependencies import Input, Output

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from acquisition.udp_receiver import get_packet

app    = dash.Dash(__name__)
buffer = np.zeros((256, 3), dtype=np.int16)   # ventana deslizante

app.layout = html.Div([
    html.H3("Vibraci\u00f3n en tiempo real"),
    dcc.Graph(id="vibration-graph"),          # ID \u00fanico
    dcc.Interval(id="poll", interval=200, n_intervals=0)  # 5 Hz
])

@app.callback(Output("vibration-graph", "figure"),
              Input("poll", "n_intervals"))
def update(_):
    global buffer
    try:
        _, pkt = get_packet(timeout=0.05)
        buffer = np.vstack([buffer[len(pkt):], pkt])
    except socket.timeout:
        pass  # mantiene los datos previos

    t = np.arange(len(buffer)) / 800  # eje tiempo (fs = 800 Hz)
    fig = go.Figure()
    for i, axis in enumerate("XYZ"):
        fig.add_trace(go.Scatter(x=t, y=buffer[:, i],
                                 mode="lines", name=axis))
    fig.update_layout(height=400, margin=dict(t=20, b=40))
    return fig

if __name__ == "__main__":
    app.run_server(debug=True)
