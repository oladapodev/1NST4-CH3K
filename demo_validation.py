#!/usr/bin/env python3
"""Demo validation runner for usage recording flow.

- Uses a fixed demo email for deterministic validation.
- Captures run output to a log file.
- Validates that the demo email appears in the generated results.

Run:
  uv run python demo_validation.py
"""

from __future__ import annotations

import subprocess
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).resolve().parent
DEMO_EMAIL = "demo-user@example.com"
INPUT_FILE = ROOT / "demo_input.txt"
RESULT_JSON = ROOT / "result" / "result.json"
RESULT_TXT = ROOT / "result" / "results.txt"
LOG_FILE = ROOT / "demo_run.log"


def run_demo() -> subprocess.CompletedProcess[str]:
    INPUT_FILE.write_text(f"{DEMO_EMAIL}\n")

    cmd = [
        "uv",
        "run",
        "python",
        "main.py",
        "--file",
        str(INPUT_FILE),
        "--threads",
        "1",
        "--delay",
        "0.1",
        "--output",
        str(ROOT / "result" / "results.txt"),
    ]
    command_str = " ".join(cmd)

    proc = subprocess.run(
        cmd,
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        check=False,
    )

    summary = [
        f"timestamp={datetime.utcnow().isoformat()}Z",
        f"demo_email={DEMO_EMAIL}",
        f"command={command_str}",
        f"return_code={proc.returncode}",
        "",
        "--- stdout ---",
        proc.stdout,
        "--- stderr ---",
        proc.stderr,
    ]
    LOG_FILE.write_text("\n".join(summary))

    return proc


def main() -> int:
    proc = run_demo()

    if proc.returncode != 0:
        print(f"[demo] command failed, check log: {LOG_FILE}")
        return proc.returncode

    found = False
    if RESULT_TXT.exists():
        found = DEMO_EMAIL in RESULT_TXT.read_text(errors="ignore")
    elif RESULT_JSON.exists():
        found = DEMO_EMAIL in RESULT_JSON.read_text(errors="ignore")

    if not found:
        print(f"[demo] completed but did not find {DEMO_EMAIL} in result output")
        print(f"[demo] log: {LOG_FILE}")
        return 1

    print(f"[demo] validation OK for email: {DEMO_EMAIL}")
    print(f"[demo] outputs: {RESULT_JSON} | {RESULT_TXT}")
    print(f"[demo] log: {LOG_FILE}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
