import importlib
import os
import socket
import sys

# Add project root to Python path so test can import local packages
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, PROJECT_ROOT)

import acquisition
import config


def reload_acquisition() -> None:
    importlib.reload(config)
    importlib.reload(acquisition)


def test_no_socket_when_simulated(monkeypatch):
    created = []

    class DummySocket:
        def __init__(self, *a, **k):
            created.append("socket")

        def setsockopt(self, *a, **k):
            pass

        def bind(self, *a, **k):
            created.append("bind")

        def settimeout(self, *a, **k):
            pass

    monkeypatch.setenv("SIMULATED_DATA", "1")
    monkeypatch.setattr(socket, "socket", DummySocket)
    reload_acquisition()
    acquisition.setup()
    assert created == []


def test_socket_created_when_real(monkeypatch):
    created = []

    class DummySocket:
        def __init__(self, *a, **k):
            created.append("socket")

        def setsockopt(self, *a, **k):
            pass

        def bind(self, *a, **k):
            created.append("bind")

        def settimeout(self, *a, **k):
            pass

    monkeypatch.setenv("SIMULATED_DATA", "0")
    monkeypatch.setattr(socket, "socket", DummySocket)
    reload_acquisition()
    acquisition.setup()
    assert created.count("socket") == 1