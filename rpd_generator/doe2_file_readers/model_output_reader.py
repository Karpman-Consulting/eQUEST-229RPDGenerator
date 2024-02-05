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
        ctypes.c_char_p  # pszRowKey
    ]
    single_result_dll.restype = ctypes.c_long

    pfData_array = (ctypes.c_float * 1)()  # Initialize the array
    IMAX_VALUES = 1
    pszReportKey = None
    pszRowKey = None

    # Call the function
    single_result_dll(doe2_dir, project_fname, entry_id, pfData_array, IMAX_VALUES, pszReportKey, pszRowKey)
    return pfData_array[0]


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
           char pszReportKey[ 34 ];
           char pszRowKey[    34 ];
        };
"""


def get_multiple_results(d2_result_dll, doe2_dir, project_fname, entry_id):
    multiple_result_dll = d2_result_dll['D2R_GetMultipleResult']

    file_type = 1
    pf_data = (ctypes.c_float * 13)()
    max_values = 13
    num_mrts = 1

    class MRTArray(ctypes.Structure):
        _fields_ = [("entry_id", ctypes.c_int),
                    ("return_value", ctypes.c_int),
                    ("psz_report_key", ctypes.c_char * 34),
                    ("psz_row_key", ctypes.c_char * 34)]

    mrt = MRTArray()
    mrt_array = (MRTArray * num_mrts)()

    mrt_array[0].entry_id = entry_id
    mrt_array[0].psz_report_key = b"EM1"
    mrt_array[0].psz_row_key = b"\0"

    p_mrts = mrt_array

    multiple_result_dll(doe2_dir, project_fname, file_type, pf_data, max_values, num_mrts, p_mrts)

    return [data for data in pf_data]


# Examples
if __name__ == "__main__":
    print(get_single_results('C:\\Program Files (x86)\\eQUEST 3-65-7175\\D2Result.dll',
                             b'C:\\doe23\\EXE50e\\',
                             b"C:\\Users\\JacksonJarboe\\Documents\\Local Models\\CT Children's Hospital\\Final Model\\Proposed\\CT Childrens Hospital - Final - Baseline Design",
                             2001001))

    print(get_multiple_results('C:\\Program Files (x86)\\eQUEST 3-65-7175\\D2Result.dll',
                               b'C:\\doe23\\EXE50e\\',
                               b"C:\\Users\\JacksonJarboe\\Documents\\Local Models\\CT Children's Hospital\\Final Model\\Proposed\\CT Childrens Hospital - Final - Baseline Design",
                               2309007))
