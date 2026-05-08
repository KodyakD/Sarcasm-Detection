from __future__ import annotations

import sys
from pathlib import Path

# Ensure backend modules are importable when tests run from different working dirs.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
