import importlib
import os
import socket
import sys
import threading

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import config


def _reload():
    importlib.reload(config)
    import acquisition.udp_receiver as ur
    import dashboard.callbacks as cb

    importlib.reload(ur)
    importlib.reload(cb)
    return cb


def test_no_socket_when_simulated(monkeypatch):
    created = []

    class DummySocket:
        def setsockopt(self, *a, **k):
            pass

        def bind(self, *a, **k):
            created.append("bind")

        def settimeout(self, *a, **k):
            pass

    def fake_socket(*a, **k):
        created.append("socket")
        return DummySocket()

    monkeypatch.setenv("SIMULATED_DATA", "1")
    monkeypatch.setattr(socket, "socket", fake_socket)

    class DummyThread:
        def __init__(self, target, daemon=False):
            self.target = target

        def start(self):
            pass

    monkeypatch.setattr(threading, "Thread", DummyThread)
    cb = _reload()
    cb.start_acquisition()
    assert created == []


def test_socket_created_when_real(monkeypatch):
    created = []

    class DummySocket:
        def setsockopt(self, *a, **k):
            pass

        def bind(self, *a, **k):
            created.append("bind")

        def settimeout(self, *a, **k):
            pass

    def fake_socket(*a, **k):
        created.append("socket")
        return DummySocket()

    monkeypatch.setenv("SIMULATED_DATA", "0")
    monkeypatch.setattr(socket, "socket", fake_socket)

    class DummyThread:
        def __init__(self, target, daemon=False):
            self.target = target

        def start(self):
            pass

    monkeypatch.setattr(threading, "Thread", DummyThread)
    cb = _reload()
    cb.start_acquisition()
    assert created.count("socket") == 1