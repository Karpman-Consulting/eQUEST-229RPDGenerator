import json
import math
import sys


def load_json(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)


def compare_json(reference, generated, optional_keys=[], tolerance_dict={}, warning_keys=[]):
    warnings = []
    errors = []
    compare_dicts(reference, generated, optional_keys, tolerance_dict, warning_keys, '', warnings, errors)
    return warnings, errors


def compare_dicts(ref_dict, gen_dict, optional_keys, tolerance_dict, warning_keys, parent_key, warnings, errors):
    for key in ref_dict:
        if key in optional_keys:
            continue
        full_key = f"{parent_key}.{key}" if parent_key else key

        if key not in gen_dict:
            message = f"Key '{full_key}' is missing in the generated JSON."
            if full_key in warning_keys:
                warnings.append(message)
            else:
                errors.append(message)
            continue

        if isinstance(ref_dict[key], dict):
            compare_dicts(ref_dict[key], gen_dict[key], optional_keys, tolerance_dict, warning_keys, full_key, warnings,
                          errors)
        elif isinstance(ref_dict[key], list):
            compare_lists(ref_dict[key], gen_dict[key], optional_keys, tolerance_dict, warning_keys, full_key, warnings,
                          errors)
        else:
            compare_values(ref_dict[key], gen_dict[key], tolerance_dict.get(full_key, None), full_key, warnings, errors,
                           warning_keys)

    # Check for extra keys in generated JSON
    for key in gen_dict:
        if key not in ref_dict and key not in optional_keys:
            message = f"Unexpected key '{key}' found in generated JSON."
            if f"{parent_key}.{key}" in warning_keys:
                warnings.append(message)
            else:
                errors.append(message)


def compare_lists(ref_list, gen_list, optional_keys, tolerance_dict, warning_keys, parent_key, warnings, errors):
    if len(ref_list) != len(gen_list):
        message = f"List length mismatch at '{parent_key}'. Expected {len(ref_list)}, found {len(gen_list)}."
        if parent_key in warning_keys:
            warnings.append(message)
        else:
            errors.append(message)

    for i, (ref_item, gen_item) in enumerate(zip(ref_list, gen_list)):
        full_key = f"{parent_key}[{i}]"
        if isinstance(ref_item, dict):
            compare_dicts(ref_item, gen_item, optional_keys, tolerance_dict, warning_keys, full_key, warnings, errors)
        elif isinstance(ref_item, list):
            compare_lists(ref_item, gen_item, optional_keys, tolerance_dict, warning_keys, full_key, warnings, errors)
        else:
            compare_values(ref_item, gen_item, tolerance_dict.get(full_key, None), full_key, warnings, errors,
                           warning_keys)


def compare_values(ref_value, gen_value, tolerance, key, warnings, errors, warning_keys):
    if isinstance(ref_value, (int, float)) and isinstance(gen_value, (int, float)):
        if tolerance is None:
            tolerance = 0
        if not math.isclose(ref_value, gen_value, rel_tol=tolerance):
            message = f"Value mismatch at '{key}'. Expected {ref_value} but found {gen_value} with tolerance {tolerance}."
            if key in warning_keys:
                warnings.append(message)
            else:
                errors.append(message)
    elif ref_value != gen_value:
        message = f"Value mismatch at '{key}'. Expected '{ref_value}' but found '{gen_value}'."
        if key in warning_keys:
            warnings.append(message)
        else:
            errors.append(message)


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python compare_json.py <reference_json> <generated_json> <tolerance_file>")
        sys.exit(1)

    reference_json_file = sys.argv[1]
    generated_json_file = sys.argv[2]
    tolerance_file = sys.argv[3]

    reference_json = load_json(reference_json_file)
    generated_json = load_json(generated_json_file)
    tolerance_dict = load_json(tolerance_file) if tolerance_file else {}

    optional_keys = tolerance_dict.get("optional_keys", [])
    tolerance_values = tolerance_dict.get("tolerances", {})
    warning_keys = tolerance_dict.get("warning_keys", [])

    warnings, errors = compare_json(reference_json, generated_json, optional_keys, tolerance_values, warning_keys)

    if warnings:
        print("Warnings:")
        for warning in warnings:
            print(f"  - {warning}")

    if errors:
        print("Errors:")
        for error in errors:
            print(f"  - {error}")

    if not warnings and not errors:
        print("JSON files match.")
        sys.exit(0)
    elif errors:
        sys.exit(1)
    else:
        sys.exit(0)
