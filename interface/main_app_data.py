import os
import configparser
import customtkinter as ctk
from pathlib import Path
from rpd_generator import main as rpd_generator
from rpd_generator.doe2_file_readers.bdlcio32 import process_input_file
from rpd_generator.doe2_file_readers.model_input_reader import ModelInputReader


class MainAppData:
    def __init__(self):
        self.install_path_entry = None
        self.installation_path = ctk.StringVar()
        self.doe22_data_path = None
        self.doe23_data_path = None
        self.user_lib_path = None

        self.files_verified = False

        self.test_inp_path = ctk.StringVar()

    def find_equest_installation(self):
        """
        Search recursively for a directory that matches a target directory starting from start_path.
        If found, checks if all target files exist within that directory in a case-insensitive manner.

        :return: Path of the directory if it exists with all target files, else None.
        """
        start_path = Path(os.environ.get("ProgramFiles(x86)", "C:/"))
        target_dir = "eQUEST 3-65-7175".lower()  # Convert target directory to lowercase
        target_files = [
            "d2result.dll",
            "bdlcio32.dll",
        ]  # Converted target files to lowercase for comparison

        for path in start_path.rglob("*"):
            # Check if the current path is a directory and matches the target directory name (case-insensitive)
            if path.is_dir() and path.name.lower() == target_dir:
                # List all files in the current directory (case-insensitive match)
                files_in_dir = [
                    file.name.lower() for file in path.iterdir() if file.is_file()
                ]
                # Check if all target files exist in the current directory (case-insensitive)
                if all(file in files_in_dir for file in target_files):
                    self.installation_path.set(str(path))
                    self.set_data_path_from_config()
                    return

    def verify_equest_installation(self):
        install_path = Path(self.installation_path.get())
        error_message = self.set_data_path_from_config()
        if error_message is not None:
            return error_message

        # List of files to check
        files_to_check = [
            install_path / "BDLCIO32.DLL",
            install_path / "D2Result.dll",
            Path(self.doe22_data_path) / "DOE-2" / "eQ_Lib.dat",
            Path(self.doe23_data_path) / "DOE23" / "eQ_Lib.dat",
            Path(self.doe22_data_path) / "DOE-2" / "BDLLIB.DAT",
            Path(self.doe23_data_path) / "DOE23" / "BDLLIB.DAT",
            Path(self.doe22_data_path) / "DOE-2" / "Usrlib.dat",
            Path(self.doe23_data_path) / "DOE23" / "Usrlib.dat",
        ]

        # Check each file and raise an error if it doesn't exist
        for file_path in files_to_check:
            if not file_path.exists() and error_message is None:
                error_message = f"File not found: {file_path}\n"
            elif not file_path.exists():
                error_message += f"File not found: {file_path}\n"

        if error_message is None:
            self.files_verified = True

        return error_message

    def set_data_path_from_config(self):
        install_path = Path(self.installation_path.get())
        doe22_ini_path = install_path / "eQUEST.ini"
        doe23_ini_path = install_path / "eQUESTD23.ini"
        if not doe22_ini_path.exists() or not doe23_ini_path.exists():
            return f"{doe22_ini_path} or {doe23_ini_path} not found. Please verify the installation path."
        config = configparser.ConfigParser()
        config.read(doe22_ini_path)
        self.doe22_data_path = config.get("paths", "DataPath").strip('"')
        config.read(doe23_ini_path)
        self.doe23_data_path = config.get("paths", "DataPath").strip('"')
        return None

    def process_inp_to_rpd_json(self):
        reader = ModelInputReader()
        reader.copy_inp_with_diagnostic_comments(str(self.test_inp_path.get()))
        test_inp_path = Path(self.test_inp_path.get())
        base_name = test_inp_path.stem
        dir_name = test_inp_path.parent
        temp_file = f"{base_name}_temp{test_inp_path.suffix}"

        process_input_file(
            # Path to Bdlcio32.dll using self.installation_path
            str(Path(__file__).parents[1] / "test/BDLCIO32.dll"),
            bytes(str(Path(self.doe22_data_path) / "DOE23") + "\\", "utf-8"),
            bytes(str(dir_name) + "\\", "utf-8"),
            bytes(temp_file, "utf-8"),
        )
        rpd_generator.generate_rpd_json(
            [str(dir_name / f"{base_name}_temp.BDL")],
            str(Path(self.installation_path.get()) / "D2Result.dll"),
            bytes(str(Path(self.doe22_data_path) / "DOE23/"), "utf-8"),
        )
