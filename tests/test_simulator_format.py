import numpy as np
from acquisition import simulator

def test_simulator_output_shape_and_type():
    seq, raw = simulator.receive_batch(n=64)
    assert raw.shape == (64, 3)
    assert raw.dtype == np.int16