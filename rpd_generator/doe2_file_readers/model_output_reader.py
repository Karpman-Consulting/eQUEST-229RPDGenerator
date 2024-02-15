import ctypes


def get_single_results(d2_result_dll, doe2_dir, project_fname, entry_id):
    """
    Get Single Results
    ------------------
    Arguments
    ---------
    :param d2_result_dll: (string) path to user's eQUEST D2Result.dll file included with installation files
    :param project_fname: (binary string) path to project with project name NOT INCLUDING FILE EXTENSION
    :param entry_id: (int) id from NHRList.txt corresponding to the value to retrieve
    :param doe2_dir: (binary string) path to DOE-2 directory
    :return: value from binary simulation output files
    """
    # Load DLL
    d2_result_dll = ctypes.CDLL(d2_result_dll)
    single_result_dll = d2_result_dll.D2R_GetSingleResult
    single_result_dll.argtypes = [
        ctypes.c_char_p,  # pszDOE2Dir
        ctypes.c_char_p,  # pszFileName
        ctypes.c_int,  # iEntryID
        ctypes.POINTER(ctypes.c_float),  # pfData
        ctypes.c_int,  # iMaxValues
        ctypes.c_char_p,  # pszReportKey
        ctypes.c_char_p,  # pszRowKey
    ]


"""

Get Multiple Result
-------------------
Arguments
---------
pszDOE2Dir: path to DOE-2 directory
pszFileName: path to project (do not include any extension)
iFileType: 0 for Loads results, 1 for HVAC, 2 for Utility Rate; in general first digit of NHRlist ID minus 1
pfData: sample array to store the retrieved values
iMaxValues: number of items to retrieve (NI in NHRList.txt); should always be 1 when GetSingleResult is called
iNumMRTs: Number of MultResultsType structures pointed to by the following argument. Only the first 12 will be used, 
          each one must retrieve results from the same file and the number of items retrieved for each element should be equal.
pMRTs: Pointer to an array of MultResultsType structures:
       struct MultResultsType
        {
           int  iEntryID;      // from NHRList.txt
           int  iReturnValue;  // success/failure
           char pszReportKey[ 40 ];
           char pszRowKey[    40 ];
        };
"""


def get_multiple_results(d2_result_dll, doe2_data_dir, project_fname, request_array):
    """
    Get Multiple Results from the simulation output files
    :param d2_result_dll: (string) path to user's eQUEST D2Result.dll file included with installation files
    :param doe2_data_dir: (binary string) path to DOE-2 data directory with NHRList.txt
    :param project_fname: (binary string) path to project with project name NOT INCLUDING FILE EXTENSION
    :param request_array: (list) list of entry_id: (int) from NHRList.txt corresponding to the value to retrieve,
    report_key: (binary string) to use when RI > 0 and when value to retrieve refers to a particular BDL component,
    and row_key: (binary string) to use when KT > 0 and when a report has multiple row where each row provides results for a separate building component or month of the year
    :return: list of returned values from the binary simulation output files
    """
    d2_result_dll = ctypes.CDLL(d2_result_dll)
    multiple_result_dll = d2_result_dll.D2R_GetMultipleResult
    nhr_list_path = doe2_data_dir + rb"\NHRList.txt"

    num_mrts = len(request_array)
    mrt_array = (MRTArray * num_mrts)()
    if len(request_array) > 0:
        file_type = int(str(request_array[0][0])[0]) - 1
    else:
        return []

    max_values = 0
    for i, value_request in enumerate(request_array):
        entry_id, report_key, row_key = value_request

        mrt_array[i].entry_id = entry_id
        mrt_array[i].psz_report_key = report_key
        mrt_array[i].psz_row_key = row_key

        with open(nhr_list_path, "r") as nhr_list:
            for line in nhr_list:
                parts = [part.strip() for part in line.split(",")]
                if parts[0] == str(entry_id):
                    # Figure out the max_values for the value request (NI in NHRList.txt) and add to the total
                    max_values += int(parts[6])
                    break

    pf_data = (ctypes.c_float * max_values)()

    multiple_result_dll(
        doe2_data_dir, project_fname, file_type, pf_data, max_values, num_mrts, mrt_array
    )

    return [data for data in pf_data]
