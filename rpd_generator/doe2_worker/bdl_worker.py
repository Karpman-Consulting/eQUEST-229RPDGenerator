import sys
import json
from pathlib import Path

# --- Import rpd_generator modules safely (supports PyInstaller) ---
ROOT = Path(__file__).resolve()
while ROOT.name != "rpd_generator" and ROOT.parent != ROOT:
    ROOT = ROOT.parent
ROOT = ROOT.parent

if getattr(sys, "frozen", False):  # PyInstaller
    ROOT = Path(sys._MEIPASS)

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from rpd_generator.doe2_file_io.bdlcio32 import process_input_file
from rpd_generator.doe2_file_io.model_output_reader import (
    get_string_result,
    get_multiple_results,
)


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
            # ---------------------
            # INP → BDL
            # ---------------------
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

            # ---------------------
            # Single string result
            # ---------------------
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

            # ---------------------
            # Multiple results
            # ---------------------
            if cmd == "get_multiple":
                result = get_multiple_results(
                    req["d2_result_dll"],
                    req["doe2_data_dir"],
                    req["project_fname"],
                    req["requests"],
                )
                send_ok(result)
                continue

            # ---------------------
            # Exit worker
            # ---------------------
            if cmd == "exit":
                send_ok("bye")
                return

            send_error(f"Unknown command: {cmd}")

        except KeyError as e:
            send_error(f"Missing required key: {e}")
        except Exception as e:
            send_error(str(e))


if __name__ == "__main__":
    main()
