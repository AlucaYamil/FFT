import os, sys
import numpy as np

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from dashboard.live_dashboard import buffer, update

def test_sinewave():
    t = np.arange(256)
    buffer[:] = np.column_stack([np.sin(2*np.pi*5*t/800)*1000]*3).astype(np.int16)
    fig = update(0)
    assert len(fig.data) == 3
    assert len(fig.data[0].y) >= 200
