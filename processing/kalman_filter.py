import numpy as np


class Kalman1D:
    def __init__(self, q_signal=1e-3, q_bias=1e-6, r_measure=1e-2):
        self.x = np.zeros((2, 1))
        self.P = np.eye(2)
        self.F = np.eye(2)
        self.Q = np.diag([q_signal, q_bias])
        self.H = np.array([[1.0, 1.0]])
        self.R = np.array([[r_measure]])
        self.I = np.eye(2)

    def update(self, z: float) -> tuple[float, float]:
        self.x = self.F @ self.x
        self.P = self.F @ self.P @ self.F.T + self.Q
        S = self.H @ self.P @ self.H.T + self.R
        K = self.P @ self.H.T @ np.linalg.inv(S)
        y = np.array([[z]]) - self.H @ self.x
        self.x = self.x + K @ y
        self.P = (self.I - K @ self.H) @ self.P
        s_est = float(self.x[0, 0])
        b_est = float(self.x[1, 0])
        return s_est, b_est