from typing import Literal
import os

SIMULATED_DATA: Literal[0, 1] = 1
_env = os.getenv("SIMULATED_DATA")
if _env is not None:
    SIMULATED_DATA = 1 if _env.strip() == "1" else 0