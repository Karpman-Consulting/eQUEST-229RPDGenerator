import customtkinter as ctk
import configparser
import os


class MainAppData:
    def __init__(self):
        self.install_path_entry = None
        self.installation_path = ctk.StringVar()
        self.doe22_data_path = None
        self.doe23_data_path = None
        self.user_lib_path = None

        self.files_verified = False

    def find_equest_installation(self):
        """
        Search recursively for a directory that matches a target directory starting from start_path.
        If found, checks if all target files exist within that directory in a case-insensitive manner.

        :return: Path of the directory if it exists with all target files, else None.
        """
        start_path = os.environ.get("ProgramFiles(x86)", "C:/")
        target_dir = "eQUEST 3-65-7175".lower()  # Convert target directory to lowercase
        target_files = [file.lower() for file in ["D2RESULT.DLL", "BDLCIO32.DLL"]]  # Convert target files to lowercase
        for dirpath, dirnames, filenames in os.walk(start_path):
            # Convert the filenames in current directory to lowercase for case-insensitive comparison
            filenames_lower = [file.lower() for file in filenames]
            # Check if current directory name matches target directory in a case-insensitive manner
            if os.path.basename(dirpath).lower() == target_dir:
                # Check if all target files are in the current directory in a case-insensitive manner
                if all(file in filenames_lower for file in target_files):
                    self.installation_path.set(dirpath)
                    self.set_data_path_from_config()

    def verify_equest_installation(self):
        install_path = self.installation_path.get()
        error_message = self.set_data_path_from_config()
        if error_message is not None:
            return error_message

        # List of files to check
        files_to_check = [os.path.join(install_path, "BDLCIO32.DLL"),
                          os.path.join(install_path, "D2Result.dll"),
                          os.path.join(self.doe22_data_path, "DOE-2\\eQ_Lib.dat"),
                          os.path.join(self.doe23_data_path, "DOE23\\eQ_Lib.dat"),
                          os.path.join(self.doe22_data_path, "DOE-2\\BDLLIB.DAT"),
                          os.path.join(self.doe23_data_path, "DOE23\\BDLLIB.DAT"),
                          os.path.join(self.doe22_data_path, "DOE-2\\Usrlib.dat"),
                          os.path.join(self.doe23_data_path, "DOE23\\Usrlib.dat")]

        # Check each file and raise an error if it doesn't exist
        for file_path in files_to_check:
            if not os.path.exists(file_path) and error_message is None:
                error_message = f"File not found: {file_path}\n"
            elif not os.path.exists(file_path):
                error_message += f"File not found: {file_path}\n"

        if error_message is None:
            self.files_verified = True

        return error_message

    def set_data_path_from_config(self):
        install_path = self.installation_path.get()
        doe22_ini_path = os.path.join(install_path, "eQUEST.ini")
        doe23_ini_path = os.path.join(install_path, "eQUESTD23.ini")
        if not os.path.exists(doe22_ini_path) or not os.path.exists(doe23_ini_path):
            return f"{doe22_ini_path} or {doe23_ini_path} not found. Please verify the installation path."
        config = configparser.ConfigParser()
        config.read(doe22_ini_path)
        self.doe22_data_path = config.get('paths', 'DataPath').strip('"')
        config.read(doe23_ini_path)
        self.doe23_data_path = config.get('paths', 'DataPath').strip('"')
        return None
