"""Repository-local entry point for the C2O reproduction command."""

from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from c2o_strategy.run import main


if __name__ == "__main__":
    main()
