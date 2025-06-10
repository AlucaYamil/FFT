import numpy as np
import pandas as pd
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app import update_graphs


def test_sinewave(tmp_path, monkeypatch):
    t = np.linspace(0, 1, 800)
    vel = pd.DataFrame({
        "time": t,
        "vx": np.sin(2 * np.pi * 5 * t),
        "vy": np.sin(2 * np.pi * 5 * t),
        "vz": np.sin(2 * np.pi * 5 * t),
    })
    fft = pd.DataFrame({
        "frequency": np.linspace(0, 400, 400),
        "amp_x": np.ones(400),
        "amp_y": np.ones(400),
        "amp_z": np.ones(400),
    })
    vel.to_csv(tmp_path / "velocity.csv", index=False)
    fft.to_csv(tmp_path / "fft_result.csv", index=False)

    monkeypatch.chdir(tmp_path)
    fig_vel, fig_fft = update_graphs(0)
    assert len(fig_vel.data) == 3
    assert len(fig_fft.data) == 3
