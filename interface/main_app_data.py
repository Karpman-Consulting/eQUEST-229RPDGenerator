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
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_file_path = reader.prepare_inp(str(self.test_inp_path.get()), temp_dir)
            self.copy_files_to_temp_dir(temp_dir)
            inp_path = Path(temp_file_path)
            json_path = inp_path.with_suffix('.json')
            base_name = inp_path.stem
            dir_name = inp_path.parent

            process_input_file(
                # Substituting the path to the BDLCIO32.dll file with the path to the test file until bug resolved
                # str(Path(Config.EQUEST_INSTALL_PATH) / "Bdlcio32.dll"),
                str(Path(__file__).parents[1] / "test" / "BDLCIO32.dll"),
                str(Path(Config.DOE23_DATA_PATH) / "DOE23") + "\\",
                str(dir_name) + "\\",
                os.path.basename(temp_file_path),
            )

            rpd_generator.generate_rpd_json([str(dir_name / f"{base_name}.BDL")])
            shutil.copy(str(json_path), os.path.dirname(self.test_inp_path.get()))
            print(f"RPD JSON file created")

    def copy_files_to_temp_dir(self, temp_dir):
        """
        Copy model files into the temporary directory for processing.
        ------------------
        Arguments
        ---------
        :param temp_dir: (string) path to the temporary directory

        :return: None
        """
        file_extensions = [".erp", ".lrp", ".srp", ".nhk"]
        model_dir = os.path.dirname(str(self.test_inp_path.get()))
        model_name = os.path.basename(str(self.test_inp_path.get())).split(".")[0]
        for ext in file_extensions:
            model_file = f"{model_name}{ext}"
            alternate_search_file = f"{model_name} - Baseline Design{ext}"

            if os.path.exists(os.path.join(model_dir, model_file)):
                shutil.copy2(os.path.join(model_dir, model_file), temp_dir)
            elif os.path.exists(os.path.join(model_dir, alternate_search_file)):
                destination_file = os.path.join(temp_dir, model_file)
                shutil.copy2(os.path.join(model_dir, alternate_search_file), destination_file)
            else:
                print(f"File {model_file} not found in {model_dir}")

