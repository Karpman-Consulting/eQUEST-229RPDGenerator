import tempfile
import os
import shutil
from pathlib import Path

from rpd_generator import main as rpd_generator
from rpd_generator.config import Config
from rpd_generator.doe2_file_readers.bdlcio32 import process_input_file
from rpd_generator.utilities import validate_configuration


def process_test_input_files():
    validate_configuration.find_equest_installation()
    test_directory = Path(__file__).parents[1] / "test"
    test_inp_files = [os.path.join(dirpath, filename)
                      for dirpath, _, filenames in os.walk(test_directory)
                      for filename in filenames if filename.endswith('.inp')]

    with tempfile.TemporaryDirectory() as temp_dir:

        for test_inp_file in test_inp_files:
            print(f"Processing INP File for Test Case {str(Path(test_inp_file).parent.name)}...")
            # Prepare the inp file for processing and save the revised copy to the temporary directory
            temp_file_path = rpd_generator.prepare_inp(test_inp_file, temp_dir)

            # Set the paths for the inp file, json file, and the directories
            temp_inp_path = Path(temp_file_path)
            bdl_path = temp_inp_path.with_suffix(".BDL")
            doe23_path = Path(Config.DOE23_DATA_PATH) / "DOE23"
            test_bdlcio32_path = Path(__file__).parents[1] / "test" / "BDLCIO32.dll"

            # Process the inp file to create the BDL file with Diagnostic Comments (defaults and evaluated values) in the temporary directory
            process_input_file(
                # str(Path(Config.EQUEST_INSTALL_PATH) / "Bdlcio32.dll"),
                str(test_bdlcio32_path),
                # Substituting the path to the BDLCIO32.dll file with the path to the test file until bug resolved
                str(doe23_path) + "\\",
                str(temp_inp_path.parent) + "\\",
                temp_inp_path.name,
            )

            # Copy the BDL file from the temporary directory back to the project directory
            shutil.copy(str(bdl_path), os.path.dirname(test_inp_file))

            print(f"Diagnostic-Commented BDL file created.")
            print("----------------------------------------")


if __name__ == "__main__":
    process_test_input_files()
