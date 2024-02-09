import ctypes


def process_input_file(bdlcio_dll, doe2_dir, work_dir, file_name, lib_file_name=None):
    """
    Process the input file using the BDLCIO32.dll file from the eQUEST installation directory.
    :param bdlcio_dll: location of the dll file as a string
    :param doe2_dir: location of the DOE-2 data directory as a binary string
    :param work_dir: parent directory location of the input file as a binary string
    :param file_name: file name of the input file as a binary string
    :param lib_file_name: optional location of the USRLIB.DAT file as a binary string
    :return:
    """
    if lib_file_name is None:
        lib_file_name = doe2_dir + b"USRLIB.DAT"

    bdlcio32 = ctypes.WinDLL(bdlcio_dll)

    # Define the prototype of the Init functions
    bdlcio32.BDLCIO32_Init.argtypes = []
    bdlcio32.BDLCIO32_Init.restype = None

    bdlcio32.BDLCIO32_Init()
    print("DLL initialized")

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
    # Calling the function from the DLL located in the eQUEST installation directory results in an OSError
    # Use a try/except block to bypass the error, then verify that the BDL output file was created
    try:
        bdlcio32.BDLCIO32_ReadInput(
            work_dir,
            doe2_dir,
            file_name,
            lib_file_name,
            no_scrn_msg,
            write_nhk_file,
            callback_func_pointer,
        )
    except OSError:
        print("Bypassing OSError from eQUEST installation DLL file")

    return
