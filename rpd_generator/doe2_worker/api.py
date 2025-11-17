import threading
import json
import subprocess
from pathlib import Path
from rpd_generator.config import Config

# Path to 32-bit Python interpreter
PY32 = Path(Config.PYTHON32_PATH)

# The worker script that actually runs the DLL calls
WORKER = Path(__file__).parent / "bdl_worker.py"

# singleton process + lock
_worker_proc = None
_worker_lock = threading.Lock()


def _ensure_worker():
    global _worker_proc
    if _worker_proc and (_worker_proc.poll() is None):
        return _worker_proc
    _worker_proc = subprocess.Popen(
        [str(PY32), str(WORKER)],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,  # keep for diagnostics
        text=True,
        bufsize=1,  # line-buffered
    )
    return _worker_proc


def _rpc(payload: dict):
    proc = _ensure_worker()
    with _worker_lock:
        proc.stdin.write(json.dumps(payload) + "\n")
        proc.stdin.flush()
        line = proc.stdout.readline()  # one JSON line back

    if not line:
        # Optionally read some stderr to help debug
        try:
            err_tail = proc.stderr.read() if proc.stderr else ""
        except Exception:
            err_tail = ""
        raise RuntimeError(f"Worker died or returned no output. Stderr:\n{err_tail}")

    resp = json.loads(line)

    if resp.get("status") == "ok":
        return resp

    # Error path
    raise RuntimeError(f"Worker error: {resp.get('error')}")


def process_inp(**kwargs):
    # kwargs includes: bdlcio_dll, doe2_data_dir, work_dir, file_name, lib_file_name?, bdl_dll_name?
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
