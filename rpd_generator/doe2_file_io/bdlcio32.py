import sys
import ctypes
import subprocess
import json
from pathlib import Path

from rpd_generator.config import Config

BDL_PY = Path(Config.PYTHON32_PATH)
BDL_WORKER = Path(__file__).parent / "bdl_worker.py"


def process_input_file(
    bdlcio_dll: str,
    doe2_data_dir: str,
    work_dir: str,
    file_name: str,
    lib_file_name=None,
    bdl_dll_name="DOEBDL23.DLL",
):
    """
    Process the input file using the BDLCIO32.dll file from the eQUEST installation directory.
    :param bdlcio_dll: location of the dll file as a string
    :param doe2_data_dir: location of the DOE-2 data directory as a string
    :param work_dir: parent directory location of the input file as a string
    :param file_name: file name of the input file as a string
    :param lib_file_name: optional location of the USRLIB.DAT file as a string
    :param bdl_dll_name: Name of the BDL DLL to load (default: "DOEBDL23.DLL")
    :return:
    """

    if lib_file_name is None:
        lib_file_name = str(Path(doe2_data_dir) / "USRLIB.DAT")

    bdlcio32 = ctypes.WinDLL(bdlcio_dll)
    # Define the prototype of BDLCIO32_InitByName
    bdlcio32.BDLCIO32_InitByName.argtypes = [ctypes.c_char_p]
    bdlcio32.BDLCIO32_InitByName.restype = ctypes.c_long

    # Initialize the DLL with the specified BDL DLL name
    init_result = bdlcio32.BDLCIO32_InitByName(bdl_dll_name.encode("utf-8"))
    if init_result == 0:
        raise OSError(f"Failed to initialize with BDL DLL: {bdl_dll_name}")

    # Define the prototype for BDLCIO32_ReadInput
    bdlcio32.BDLCIO32_ReadInput.argtypes = [
        ctypes.c_char_p,
        ctypes.c_char_p,
        ctypes.c_char_p,
        ctypes.c_char_p,
        ctypes.c_long,
        ctypes.c_int,
        ctypes.POINTER(ctypes.c_int),
    ]
    bdlcio32.BDLCIO32_ReadInput.restype = ctypes.c_long

    no_scrn_msg = 0
    write_nhk_file = 0
    callback_func_pointer = ctypes.POINTER(ctypes.c_int)()
    try:
        bdlcio32.BDLCIO32_ReadInput(
            work_dir.encode("mbcs"),
            doe2_data_dir.encode("mbcs"),
            file_name.encode("mbcs"),
            lib_file_name.encode("mbcs"),
            no_scrn_msg,
            write_nhk_file,
            callback_func_pointer,
        )
        print("INP file processed to BDL.", file=sys.stderr)

    except OSError as e:
        print(f"Error processing INP file to BDL: {e}", file=sys.stderr)

    return


def process_inp_to_bdl(bdlcio32, doe2_data, work_dir, file_name):
    payload = {
        "command": "process_inp",
        "bdlcio_dll": str(bdlcio32),
        "doe2_data_dir": str(doe2_data),
        "work_dir": str(work_dir),
        "file_name": file_name,
    }

    proc = subprocess.Popen(
        [str(BDL_PY), str(BDL_WORKER)],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        bufsize=1,
    )
    stdout, stderr = proc.communicate(json.dumps(payload))
    if stderr.strip():
        raise RuntimeError(stderr)
    result = json.loads(stdout)
    if result["status"] != "ok":
        raise RuntimeError(result["message"])
    return result.get("results")
