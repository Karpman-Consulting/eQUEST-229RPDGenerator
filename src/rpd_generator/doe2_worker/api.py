import threading
import json
import subprocess
import sys
from pathlib import Path
from rpd_generator.config import Config

# ========================
# Path resolution (critical)
# ========================
if getattr(sys, "frozen", False):
    BASE = Path(sys._MEIPASS)  # ← correct for PyInstaller 6.x
    WORKER = BASE / "workers_x86" / "doe2_worker" / "bdl_worker" / "bdl_worker.exe"
    PY32 = None
else:
    BASE = Path(__file__).resolve().parents[3]
    PY32 = Path(Config.PYTHON32_PATH)
    WORKER = BASE / "workers_x86" / "doe2_worker" / "bdl_worker.py"
    WORKER_EXE = BASE / "workers_x86" / "doe2_worker" / "bdl_worker" / "bdl_worker.exe"

# ========================
# Worker process singleton
# ========================

_worker_proc = None
_worker_lock = threading.Lock()


def _ensure_worker():
    global _worker_proc

    if _worker_proc and (_worker_proc.poll() is None):
        return _worker_proc

    if getattr(sys, "frozen", False):
        cmd = [str(WORKER)]  # Run EXE when frozen
    else:
        if PY32.exists():
            cmd = [str(PY32), str(WORKER)]  # Run .py with 32-bit python during dev
        elif WORKER_EXE.exists():
            cmd = [str(WORKER_EXE)]  # Fall back to bundled EXE when python32 is absent
        else:
            raise FileNotFoundError(
                f"DOE-2 worker runtime not found. Expected either '{PY32}' or '{WORKER_EXE}'."
            )

    _worker_proc = subprocess.Popen(
        cmd,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1,
    )

    return _worker_proc


def _rpc(payload: dict):
    """Send one JSON-RPC command to the worker process."""
    proc = _ensure_worker()

    with _worker_lock:
        proc.stdin.write(json.dumps(payload) + "\n")
        proc.stdin.flush()
        line = proc.stdout.readline()

    if not line:
        # Worker crashed or failed to start
        try:
            err_tail = proc.stderr.read() if proc.stderr else ""
        except Exception:
            err_tail = ""
        raise RuntimeError(f"Worker returned no output.\nStderr:\n{err_tail}")

    resp = json.loads(line)

    if resp.get("status") == "ok":
        return resp

    raise RuntimeError(f"Worker error: {resp.get('error')}")


# ========================
# Public API wrappers
# ========================


def process_inp(**kwargs):
    return _rpc({"cmd": "process_inp", **kwargs})


def get_multiple_results_32(*, d2_result_dll, doe2_data_dir, project_fname, requests):
    return _rpc(
        {
            "cmd": "get_multiple",
            "d2_result_dll": d2_result_dll,
            "doe2_data_dir": doe2_data_dir,
            "project_fname": project_fname,
            "requests": requests,
        }
    )["results"]


def get_string_result_32(
    *, d2_result_dll, doe2_data_dir, project_fname, entry_id, report_key="", row_key=""
):
    return _rpc(
        {
            "cmd": "get_single",
            "d2_result_dll": d2_result_dll,
            "doe2_data_dir": doe2_data_dir,
            "project_fname": project_fname,
            "entry_id": entry_id,
            "report_key": report_key,
            "row_key": row_key,
        }
    )["results"]


def shutdown_worker():
    global _worker_proc
    try:
        _rpc({"cmd": "exit"})
    except Exception:
        pass
    finally:
        if _worker_proc and (_worker_proc.poll() is None):
            try:
                _worker_proc.terminate()
            except Exception:
                pass
        _worker_proc = None
