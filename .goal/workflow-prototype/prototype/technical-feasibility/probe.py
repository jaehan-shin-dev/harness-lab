"""Exercise real SQLite transactions from two separate Python processes.

Public interface: python3 probe.py --input wait.json --database FRESH.sqlite
JSON on stdout includes environment, child events/errors, timing, and final rows.
"""

import argparse
import json
from pathlib import Path
import platform
import sqlite3
import subprocess
import sys
import time


def emit(value):
    print(json.dumps(value), flush=True)


def worker(args):
    connection = sqlite3.connect(args.database, timeout=args.timeout_ms / 1000)
    started = time.perf_counter()
    try:
        connection.execute("BEGIN IMMEDIATE")
        waited_ms = round((time.perf_counter() - started) * 1000, 3)
        emit({"event": "lock_acquired", "owner": args.owner,
              "waited_ms": waited_ms})
        time.sleep(args.hold_ms / 1000)
        connection.execute("INSERT INTO reservations VALUES (?, ?)",
                           (args.resource, args.owner))
        connection.commit()
        emit({"status": "reserved", "owner": args.owner,
              "waited_ms": waited_ms})
    except sqlite3.IntegrityError as error:
        connection.rollback()
        emit({"status": "already_reserved", "owner": args.owner,
              "waited_ms": waited_ms, "error_type": type(error).__name__,
              "error": str(error)})
    except sqlite3.OperationalError as error:
        if str(error) != "database is locked":
            raise
        connection.rollback()
        emit({"status": "database_locked", "owner": args.owner,
              "waited_ms": round((time.perf_counter() - started) * 1000, 3),
              "error_type": type(error).__name__, "error": str(error)})
    finally:
        connection.close()


def child_result(returncode, stdout, stderr):
    events = [json.loads(line) for line in stdout.splitlines() if line]
    final = events[-1] if events and "status" in events[-1] else {
        "status": "worker_failed"}
    return dict(final, exit_code=returncode, events=events, stderr=stderr)


def experiment(args):
    started = time.perf_counter()
    database = Path(args.database).resolve()
    if database.exists():
        raise SystemExit("Choose a fresh --database path to preserve earlier evidence")
    config = json.loads(Path(args.input).read_text())
    connection = sqlite3.connect(str(database))
    connection.execute("CREATE TABLE reservations "
                       "(resource TEXT PRIMARY KEY, owner TEXT NOT NULL)")
    connection.commit()
    journal_mode = connection.execute("PRAGMA journal_mode").fetchone()[0]
    connection.close()
    base = [sys.executable, str(Path(__file__).resolve()), "--worker",
            "--database", str(database), "--resource", config["resource"]]
    holder_command = base + ["--owner", config["holder"]["owner"],
                             "--hold-ms", str(config["holder"]["hold_ms"])]
    contender_command = base + ["--owner", config["contender"]["owner"],
                                "--timeout-ms",
                                str(config["contender"]["timeout_ms"])]
    holder = subprocess.Popen(holder_command, text=True, stdout=subprocess.PIPE,
                              stderr=subprocess.PIPE)
    first_event = holder.stdout.readline()
    if json.loads(first_event).get("event") != "lock_acquired":
        raise RuntimeError("Holder did not acquire the real database lock")
    contender = subprocess.run(contender_command, text=True, capture_output=True,
                               timeout=10)
    remaining_stdout, holder_stderr = holder.communicate(timeout=10)
    connection = sqlite3.connect(str(database))
    reservations = connection.execute(
        "SELECT resource, owner FROM reservations ORDER BY resource").fetchall()
    connection.close()
    emit({"environment": {"python": platform.python_version(),
                          "sqlite": sqlite3.sqlite_version,
                          "platform": platform.platform(),
                          "database": str(database),
                          "journal_mode": journal_mode},
          "input": config,
          "commands": {"holder": holder_command,
                       "contender": contender_command},
          "holder": child_result(holder.returncode,
                                 first_event + remaining_stdout, holder_stderr),
          "contender": child_result(contender.returncode, contender.stdout,
                                    contender.stderr),
          "reservations": reservations,
          "total_elapsed_ms": round((time.perf_counter() - started) * 1000, 3)})


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path)
    parser.add_argument("--database", required=True)
    parser.add_argument("--worker", action="store_true", help=argparse.SUPPRESS)
    parser.add_argument("--owner")
    parser.add_argument("--resource")
    parser.add_argument("--timeout-ms", type=int, default=2000)
    parser.add_argument("--hold-ms", type=int, default=0)
    args = parser.parse_args()
    worker(args) if args.worker else experiment(args)
