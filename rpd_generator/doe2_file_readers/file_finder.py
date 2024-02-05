import os


def find_equest_files():
    """
    Search recursively for a directory that matches a target directory starting from start_path.
    If found, checks if all target files exist within that directory.

    :return: Path of the directory if it exists with all target files, else None.
    """
    start_path = os.environ.get("ProgramFiles(x86)", "C:/")
    target_dir = "eQUEST 3-65-7175"
    target_files = ["D2Result.dll", "DOEBDL23.dll", "DOEBDL32.DLL"]
    for dirpath, dirnames, filenames in os.walk(start_path):
        # Check if current directory name matches target directory
        if os.path.basename(dirpath) == target_dir:
            # Check if all target files are in the current directory
            if all(file in filenames for file in target_files):
                return dirpath  # Return the path if all files are found
    return None  # Return None if the directory or files were not found
