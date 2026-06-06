from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def run(cmd: list[str]) -> None:
    subprocess.run(cmd, check=True)


def main() -> int:
    root = Path(__file__).resolve().parent
    run([sys.executable, "-m", "ruff", "format", "--check", str(root)])
    run([sys.executable, "-m", "ruff", "check", str(root)])
    run([sys.executable, "-m", "pytest"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

