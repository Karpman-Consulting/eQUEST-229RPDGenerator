import customtkinter as ctk
from pathlib import Path
from rpd_generator import main as rpd_generator
from rpd_generator.doe2_file_readers.bdlcio32 import process_input_file
from rpd_generator.doe2_file_readers.model_input_reader import ModelInputReader
from rpd_generator.config import Config


class MainAppData:
    def __init__(self):
        self.installation_path = ctk.StringVar()
        self.user_lib_path = None
        self.files_verified = False

        self.test_inp_path = ctk.StringVar()

    def process_inp_to_rpd_json(self):
        reader = ModelInputReader()
        reader.prepare_inp(str(self.test_inp_path.get()))
        test_inp_path = Path(self.test_inp_path.get())
        base_name = test_inp_path.stem
        dir_name = test_inp_path.parent
        temp_file = f"{base_name}_temp{test_inp_path.suffix}"

        process_input_file(
            # Substituting the path to the BDLCIO32.dll file with the path to the test file until bug resolved
            # str(Path(Config.EQUEST_INSTALL_PATH) / "Bdlcio32.dll"),
            str(Path(__file__).parents[1] / "test" / "BDLCIO32.dll"),
            str(Path(Config.DOE23_DATA_PATH) / "DOE23") + "\\",
            str(dir_name) + "\\",
            temp_file,
        )
        rpd_generator.generate_rpd_json([str(dir_name / f"{base_name}_temp.BDL")])
