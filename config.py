"""Configuración global de la aplicación."""

from __future__ import annotations

import logging
import os
from typing import Literal

logger = logging.getLogger(__name__)

SIMULATED: Literal[0, 1] = 1
_env = os.getenv("SIMULATED_DATA")
if _env is not None:
    SIMULATED = 1 if _env.strip() == "1" else 0
logger.debug("SIMULATED=%s", SIMULATED)