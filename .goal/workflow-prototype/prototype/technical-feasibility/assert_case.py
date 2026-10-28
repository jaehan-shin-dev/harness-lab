"""Run the documented CLI and preserve its real output before asserting behavior."""

import argparse
import json
from pathlib import Path
import subprocess
import sys

parser = argparse.ArgumentParser()
parser.add_argument("--case", choices=["wait", "timeout"], required=True)
parser.add_argument("--out-dir", type=Path, required=True)
args = parser.parse_args()
root = Path(__file__).resolve().parent
out = args.out_dir.resolve()
out.mkdir(parents=True, exist_ok=False)
command = [sys.executable, str(root / "probe.py"), "--input",
           str(root / (args.case + ".json")), "--database",
           str(out / "reservations.sqlite")]
(out / "command.json").write_text(json.dumps(command, indent=2) + "\n")
run = subprocess.run(command, text=True, capture_output=True, timeout=15)
(out / "stdout.json").write_text(run.stdout)
(out / "stderr.txt").write_text(run.stderr)
(out / "exit-status.txt").write_text(str(run.returncode) + "\n")
assert run.returncode == 0, "probe command failed; inspect preserved stderr.txt"
result = json.loads(run.stdout)
assert result.get("reservations") == [["room-1", "A"]], result
assert result["holder"]["status"] == "reserved", result
expected = {"wait": "already_reserved", "timeout": "database_locked"}[args.case]
assert result["contender"]["status"] == expected, result
if args.case == "timeout":
    assert result["contender"]["error"] == "database is locked", result
print("PASS " + args.case + ": one reservation; contender=" + expected)
