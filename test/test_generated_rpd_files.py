import os
import json
import math
from difflib import SequenceMatcher


from rpd_generator.utilities.jsonpath_utils import find_all, find_all_with_field_value, find_all_with_fields_values


def compare_json_values(spec, generated_values, reference_values):
    """Compares a list of generated and reference JSON values based on the spec."""
    compare_value = spec.get("compare-value", True)
    tolerance = spec.get("comparison-tolerance", 0)

    errors = []

    for i, (generated_value, reference_value) in enumerate(zip(generated_values, reference_values)):

        if isinstance(reference_value, dict):
            raise ValueError("json-test-key-path should not result in a dictionary.")

        if isinstance(reference_value, list):
            if len(generated_value) != len(reference_value):
                errors.append(f"List length mismatch at index {i}: Expected {len(reference_value)}, got {len(generated_value)}")
                continue
            if compare_value:
                for j, (gen_item, ref_item) in enumerate(zip(generated_value, reference_value)):
                    if gen_item != ref_item:
                        errors.append(f"List element mismatch at index [{i}][{j}]: Expected {ref_item}, got {gen_item}")
                continue

        if compare_value is False:
            continue  # No comparison needed, just check for existence

        does_match = compare_values(generated_value, reference_value, tolerance)
        if not does_match:
            errors.append(f"Value mismatch at index {i}: Expected '{reference_value}', got '{generated_value}'")

    return errors


def compare_values(value, reference_value, tolerance):
    """Compares a generated value with a reference value based on the tolerance."""
    if isinstance(reference_value, str):
        return value == reference_value

    if isinstance(reference_value, bool):
        return value == reference_value

    if isinstance(reference_value, (int, float)):
        return math.isclose(value, reference_value, abs_tol=tolerance)

    return False


def load_json_file(file_path):
    """Loads JSON data from a file."""
    with open(file_path, 'r') as file:
        return json.load(file)


def find_matches_for(match_type, generated_values, reference_values):
    """Find matches for a key in the generated and reference JSON based on the 'path' in the spec."""
    mapping = {}
    generated_object_ids = [value.get("id", "") for value in generated_values]
    reference_object_ids = [value.get("id", "") for value in reference_values]
    if len(generated_object_ids) != len(reference_object_ids):
        raise ValueError("Lists have different lengths")

    def get_best_match(target, candidates):
        # Return the index of the best match from candidates
        best_match_found = None
        highest_ratio = 0.0
        for candidate in candidates:
            ratio = SequenceMatcher(None, target, candidate).ratio()
            if ratio > highest_ratio:
                highest_ratio = ratio
                best_match_found = candidate
        return best_match_found

    def get_best_match_attrs(target, candidates, attrs):
        print("trying this method")
        best_match_found = None
        highest_qty_matched = 0
        for candidate in candidates:
            qty_matched = 0
            for attr in attrs:
                if target.get(attr) == candidate.get(attr):
                    qty_matched += 1
            if qty_matched > highest_qty_matched:
                highest_qty_matched = qty_matched
                best_match_found = candidate
        return best_match_found

    used_ids = set()

    for object_id in generated_object_ids:
        best_match_id = get_best_match(object_id, reference_object_ids)
        if best_match_id is not None and best_match_id not in used_ids:
            mapping[object_id] = best_match_id
            used_ids.add(best_match_id)
        else:
            print("Error: Could not match elements between the generated and reference files. Try to align with the correct answer file naming conventions.")

    if len(mapping) != len(generated_object_ids) and match_type == "Surfaces":
        for generated_object in generated_values:
            generated_object_id = generated_object.get("id")
            best_match = get_best_match_attrs(generated_object, reference_values, ["area", "azimuth"])
            if best_match is not None:
                mapping[generated_object_id] = best_match.get("id")
    print(mapping)
    return mapping


def compare_fan_power(generated_fans):
    """Compare the design electric power based on design airflow."""
    errors = []

    for fan in generated_fans:
        design_airflow = fan.get("design_airflow")
        design_power = fan.get("design_electric_power")

        # Check if the design electric power is within the expected range
        if design_power != 0.3 * design_airflow:
            errors.append(f"Design electric power is not within the expected range: Expected {design_airflow}, got {design_power}")

    return errors


def match_surfaces(zone_id, surface_type, generated_surfaces, reference_surfaces):
    errors = []
    surface_map = {}
    if len(generated_surfaces) != len(reference_surfaces):
        errors.append(f"{surface_type} surface count mismatch in zone id '{zone_id}': Expected {len(reference_surfaces)}, got {len(generated_surfaces)}")
        return surface_map, errors

    if len(generated_surfaces) == 1:
        surface_map[generated_surfaces[0].get("id")] = reference_surfaces[0].get("id")

    surface_map = find_matches_for("Surfaces", generated_surfaces, reference_surfaces)

    return surface_map, errors


def compare_json_files(test_case_name, spec_file, generated_json_file, reference_json_file):
    """Compares generated and reference JSON files according to the spec."""
    spec = load_json_file(spec_file)
    json_test_key_paths = spec.get("json-test-key-paths", [])

    generated_json = load_json_file(generated_json_file)
    reference_json = load_json_file(reference_json_file)

    warnings = []
    errors = []

    generated_zones = find_all("$.ruleset_model_descriptions[0].buildings[0].building_segments[0].zones[*]", generated_json)
    reference_zones = find_all("$.ruleset_model_descriptions[0].buildings[0].building_segments[0].zones[*]", reference_json)
    generated_zone_ids = [zone.get("id") for zone in generated_zones]
    reference_zone_ids = [zone.get("id") for zone in reference_zones]
    zone_map = find_matches_for("Zones", generated_zones, reference_zones)
    if not zone_map:
        warnings.append("Could not match zones between the generated and reference files. Try to align with the correct answer file naming conventions.")

    for i, generated_zone in enumerate(generated_zones):
        surface_map = {}

        generated_zone_id = generated_zone.get("id")
        reference_zone = reference_zones[reference_zone_ids.index(zone_map[generated_zone_id])]
        reference_zone_id = reference_zone.get("id")
        print(f"Comparing zone {generated_zone_id} with {reference_zone_id}")

        # Compare zone surfaces
        generated_ext_wall_surfaces = find_all_with_fields_values("$.surfaces[*]", {"classification": "WALL", "adjacent_to": "EXTERIOR"}, generated_zone)
        reference_ext_wall_surfaces = find_all_with_fields_values("$.surfaces[*]", {"classification": "WALL", "adjacent_to": "EXTERIOR"}, reference_zone)
        surface_map.update(match_surfaces(generated_zone_id, "Exterior Wall", generated_ext_wall_surfaces, reference_ext_wall_surfaces)[0])

        generated_int_wall_surfaces = find_all_with_fields_values("$.surfaces[*]", {"classification": "WALL", "adjacent_to": "INTERIOR"}, generated_zone)
        surfaces_adjacent_to_generated_zone = find_all_with_field_value(
            "$.ruleset_model_descriptions[0].buildings[0].building_segments[0].zones[*].surfaces[*]", "adjacent_zone",
            generated_zone_id, generated_json)
        generated_int_wall_surfaces.extend(surfaces_adjacent_to_generated_zone)
        reference_int_wall_surfaces = find_all_with_fields_values("$.surfaces[*]", {"classification": "WALL", "adjacent_to": "INTERIOR"}, reference_zone)
        surfaces_adjacent_to_referenced_zone = find_all_with_field_value("$.ruleset_model_descriptions[0].buildings[0].building_segments[0].zones[*].surfaces[*]", "adjacent_zone", reference_zone_id, reference_json)
        reference_int_wall_surfaces.extend(surfaces_adjacent_to_referenced_zone)
        surface_matches = match_surfaces(generated_zone_id, "Interior Wall", generated_int_wall_surfaces, reference_int_wall_surfaces)
        surface_map.update(surface_matches[0])

        generated_ground_floor_surfaces = find_all_with_fields_values("$.surfaces[*]", {"classification": "FLOOR", "adjacent_to": "GROUND"}, generated_zone)
        reference_ground_floor_surfaces = find_all_with_fields_values("$.surfaces[*]", {"classification": "FLOOR", "adjacent_to": "GROUND"}, reference_zone)
        surface_map.update(match_surfaces(generated_zone_id, "Ground Floor", generated_ground_floor_surfaces, reference_ground_floor_surfaces)[0])

        generated_roof_surfaces = find_all_with_fields_values("$.surfaces[*]", {"classification": "CEILING", "adjacent_to": "EXTERIOR"}, generated_zone)
        reference_roof_surfaces = find_all_with_fields_values("$.surfaces[*]", {"classification": "CEILING", "adjacent_to": "EXTERIOR"}, reference_zone)
        surface_map.update(match_surfaces(generated_zone_id, "Roof", generated_roof_surfaces, reference_roof_surfaces)[0])


    # for path_spec in json_test_key_paths:
    #     json_key_path = path_spec["json-key-path"]
    #
    #     # Handle Special Case for surfaces
    #     if json_key_path == "$.ruleset_model_descriptions[0].buildings[0].building_segments[0].zones[*].surfaces":
    #
    #         if not generated_zones:
    #             warnings.append(f"Missing key {json_key_path.split('.')[-1]} in generated JSON for {test_case_name}.")
    #             continue
    #
    #         zone_surface_errors = compare_zone_surfaces(generated_zones, reference_zones)
    #         if zone_surface_errors:
    #             errors.extend(
    #                 f"Error in {test_case_name} at {json_key_path.split('.')[-1]}: {err}" for err in zone_surface_errors)
    #
    #     # Handle Special Case for design electric power based on design airflow (which is not a specified value)
    #     elif json_key_path == "$.ruleset_model_descriptions[0].buildings[0].building_segments[0].heating_ventilating_air_conditioning_systems[*].fan_system.supply_fans[0].design_electric_power":
    #         generated_supply_fan = find_all("$.ruleset_model_descriptions[0].buildings[0].building_segments[0].heating_ventilating_air_conditioning_systems[*].fan_system.supply_fans", generated_json)
    #         compare_fan_power_errors = compare_fan_power(generated_supply_fan)
    #         if compare_fan_power_errors:
    #             errors.extend(
    #                 f"Error in {test_case_name} at {json_key_path.split('.')[-1]}: {err}" for err in compare_fan_power_errors)
    #
    #     # Perform General Comparison Methodology
    #     else:
    #
    #         if "zones[*]" in json_key_path:
    #             generated_zones = find_all("$.ruleset_model_descriptions[0].buildings[0].building_segments[0].zones[*]", generated_json)
    #             reference_zones = find_all("$.ruleset_model_descriptions[0].buildings[0].building_segments[0].zones[*]", reference_json)
    #
    #         else:
    #             generated_values = find_all(json_key_path, generated_json)
    #             reference_values = find_all(json_key_path, reference_json)
    #
    #         if not generated_values:
    #             warnings.append(f"Missing key {json_key_path.split('.')[-1]} in generated JSON for {test_case_name}.")
    #             continue
    #
    #         general_comparison_errors = compare_json_values(path_spec, generated_values, reference_values)
    #         if general_comparison_errors:
    #             errors.extend(f"Error in {test_case_name} at {json_key_path.split('.')[-1]}: {err}" for err in general_comparison_errors)
    #
    return warnings, errors


def run_comparison_for_all_tests(test_dir):
    """Runs JSON comparison for all test cases in the test directory."""

    reference_dir = os.path.join(test_dir, "Correct Answer RPDs")
    spec_dir = os.path.join(test_dir, "Test Specifications")

    for item in os.listdir(test_dir):
        if os.path.isdir(test_dir) and (item.startswith("E-") or item.startswith("F-")):

            test_case_dir = os.path.join(test_dir, item)
            generated_json_file = next((os.path.join(test_case_dir, f) for f in os.listdir(test_case_dir) if f.endswith('.json')), None)
            spec_file = os.path.join(spec_dir, f"{item} spec.json")
            reference_json_file = os.path.join(reference_dir, f"{item}.json")

            if generated_json_file and os.path.isfile(spec_file) and os.path.isfile(generated_json_file) and os.path.isfile(reference_json_file):
                print(f"Running comparison for {item}...")
                warnings, errors = compare_json_files(item, spec_file, generated_json_file, reference_json_file)

                if warnings:
                    print(f"Warnings for {item}:")
                    for warning in warnings:
                        print(f"{warning}")

                if errors:
                    print(f"Errors for {item}:")
                    for error in errors:
                        print(f"{error}")


if __name__ == "__main__":
    test_directory = os.path.dirname(os.path.abspath(__file__))
    run_comparison_for_all_tests(test_directory)
