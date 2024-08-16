from pathlib import Path
import argparse

from rpd_generator import main as rpd_generator
from rpd_generator.config import Config


def generate_test_rpds_from_bdls(output_dir=None, testing=False):
    # During testing, point the program to the temporary directory as the install-path where D2Result.dll is located
    if testing:
        Config.EQUEST_INSTALL_PATH = output_dir

    test_directory = Path(__file__).parents[1] / "test"
    test_bdl_files = [bdl_file for bdl_file in test_directory.rglob('*.BDL')]

    for test_bdl_file in test_bdl_files:
        print(f"Processing BDL File for Test Case {test_bdl_file.parent.name}...")
        if output_dir is not None:
            output_path = Path(output_dir) / test_bdl_file.with_suffix('.json').name
            rpd_generator.write_rpd_json_from_bdl([str(test_bdl_file)], str(output_path))
        else:
            output_path = test_bdl_file.with_suffix('.json')
            rpd_generator.write_rpd_json_from_bdl([str(test_bdl_file)], str(output_path))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate test RPDs from BDL files.")
    parser.add_argument('--output_dir', type=str, default=None, help='Directory to output the generated JSON files.')
    parser.add_argument('--testing', type=bool, default=False, help='Whether to run in testing mode.')

    args = parser.parse_args()
    generate_test_rpds_from_bdls(output_dir=args.output_dir, testing=args.testing)
