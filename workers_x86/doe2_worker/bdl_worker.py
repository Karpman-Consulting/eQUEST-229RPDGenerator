import sys
import json
from pathlib import Path

# ===========================================================
# Both IDE mode + Frozen mode import logic
# ===========================================================

if getattr(sys, "frozen", False):
    # -------------------------------------------------------
    # FROZEN MODE (32-bit PyInstaller EXE)
    # -------------------------------------------------------
    ROOT = Path(sys._MEIPASS)
    sys.path.insert(0, str(ROOT))

else:
    # -------------------------------------------------------
    # IDE MODE (run directly from Python)
    # -------------------------------------------------------
    WORKER_DIR = Path(__file__).resolve().parent
    ROOT = WORKER_DIR

    # Search upward for project root that contains src/rpd_generator
    rpd_path = None
    while ROOT != ROOT.parent:
        candidate = ROOT / "src" / "rpd_generator"
        if candidate.exists():
            rpd_path = candidate
            break
        ROOT = ROOT.parent

    if rpd_path is None:
        print(
            "[bdl_worker DEBUG] ERROR: Could not locate rpd_generator in IDE mode",
            file=sys.stderr,
        )
    else:
        print(
            f"[bdl_worker DEBUG] rpd_generator found in IDE mode at: {rpd_path}",
            file=sys.stderr,
        )

    # Add both ROOT and ROOT/src
    for path in [ROOT, ROOT / "src"]:
        if path.exists():
            sys.path.insert(0, str(path))
        else:
            print(
                f"[bdl_worker DEBUG] WARNING: path does NOT exist → {path}",
                file=sys.stderr,
            )


# ===========================================================
# Imports
# ===========================================================

try:
    from rpd_generator.doe2_file_io.bdlcio32 import process_input_file
    from rpd_generator.doe2_file_io.model_output_reader import (
        get_string_result,
        get_multiple_results,
    )
except Exception as e:
    print("[bdl_worker DEBUG] IMPORT FAILURE:", e, file=sys.stderr)
    raise


# ===========================================================
# Worker logic (unchanged)
# ===========================================================


def _send(obj):
    sys.stdout.write(json.dumps(obj) + "\n")
    sys.stdout.flush()


def send_ok(result):
    _send({"status": "ok", "results": result})


def send_error(msg):
    _send({"status": "error", "error": msg})


def main():
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue

        try:
            req = json.loads(line)
        except json.JSONDecodeError:
            send_error("Invalid JSON")
            continue

        cmd = req.get("cmd")
        try:
            if cmd == "process_inp":
                process_input_file(
                    bdlcio_dll=req["bdlcio_dll"],
                    doe2_data_dir=req["doe2_data_dir"],
                    work_dir=req["work_dir"],
                    file_name=req["file_name"],
                    lib_file_name=req.get("lib_file_name"),
                    bdl_dll_name=req.get("bdl_dll_name", "DOEBDL23.DLL"),
                )
                send_ok(None)
                continue

            if cmd == "get_single":
                result = get_string_result(
                    req["d2_result_dll"],
                    req["doe2_data_dir"],
                    req["project_fname"],
                    req["entry_id"],
                    req.get("report_key", ""),
                    req.get("row_key", ""),
                )
                send_ok(result)
                continue

            if cmd == "get_multiple":
                result = get_multiple_results(
                    req["d2_result_dll"],
                    req["doe2_data_dir"],
                    req["project_fname"],
                    req["requests"],
                )
                send_ok(result)
                continue

            if cmd == "exit":
                send_ok("bye")
                return

            send_error(f"Unknown command: {cmd}")

        except Exception as e:
            send_error(str(e))


if __name__ == "__main__":
    main()
