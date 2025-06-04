import importlib
import numpy as np
import dashboard.callbacks as cb
from acquisition import simulator
from processing import signal_pipeline

def test_update_dashboard_returns_data():
    importlib.reload(cb)
    seq, raw = simulator.receive_batch(n=128)
    result = signal_pipeline(raw)
    for m in np.linalg.norm(result["acc_ms2"], axis=1):
        cb.acc_t.append(0)
        cb.acc_v.append(m)
    cb.buf_t.append(0)
    cb.buf_v.extend(result["vel_mm_s"])
    cb.buf_rms.append(result["rms"])
    figs = cb.update_dashboard(0, 0, "G1")
    assert len(figs[0].data[0].y) > 0
    assert len(figs[1].data[0].y) > 0