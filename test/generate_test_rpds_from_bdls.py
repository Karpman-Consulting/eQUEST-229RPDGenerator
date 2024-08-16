import os
from pathlib import Path

from rpd_generator import main as rpd_generator
from rpd_generator.utilities import validate_configuration


def generate_test_rpds_from_bdls():
    validate_configuration.find_equest_installation()
    test_directory = Path(__file__).parents[1] / "test"
    test_bdl_files = [os.path.join(dirpath, filename)
                      for dirpath, _, filenames in os.walk(test_directory)
                      for filename in filenames if filename.endswith('.BDL')]
    for test_bdl_file in test_bdl_files:
        print(f"Processing BDL File for Test Case {str(Path(test_bdl_file).parent.name)}...")
        rpd_generator.write_rpd_json_from_bdl(
            [
                test_bdl_file
            ],
            test_bdl_file.replace(".BDL", ".json")
        )


if __name__ == "__main__":
    generate_test_rpds_from_bdls()
