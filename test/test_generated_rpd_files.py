import os
import json
import math
from difflib import SequenceMatcher


from rpd_generator.utilities.jsonpath_utils import (
    find_one,
    find_all,
    find_all_with_field_value,
    find_all_with_filters,
)


def compare_json_values(spec, generated_values, reference_values):
    """Compares a list of generated and reference JSON values based on the spec."""
    compare_value = spec.get("compare-value", True)
    tolerance = spec.get("tolerance", 0)

    errors = []

    for i, (generated_value, reference_value) in enumerate(
        zip(generated_values, reference_values)
    ):

        if isinstance(reference_value, dict):
            raise ValueError("json-test-key-path should not result in a dictionary.")

        elif isinstance(reference_value, list):

            if len(generated_value) != len(reference_value):
                errors.append(
                    f"List length mismatch at index {i}: Expected {len(reference_value)}, got {len(generated_value)}"
                )
                continue

            if compare_value:
                for j, (gen_item, ref_item) in enumerate(
                    zip(generated_value, reference_value)
                ):
                    if gen_item != ref_item:
                        errors.append(
                            f"List element mismatch at index [{i}][{j}]: Expected {ref_item}, got {gen_item}"
                        )
                continue

        if compare_value is False:
            continue  # No comparison needed, just check for existence

        # Else: the values are strings, ints, or floats, and we need to compare them
        does_match = compare_values(generated_value, reference_value, tolerance)
        if not does_match:
            errors.append(
                f"Value mismatch at index {i}: Expected '{reference_value}', got '{generated_value}'"
            )

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
    with open(file_path, "r") as file:
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
        best_match_found = None
        highest_qty_matched = 0

        for candidate in candidates:
            qty_matched = 0
            for attr in attrs:
                target_value = target.get(attr)
                candidate_value = candidate.get(attr)

                if attr == "azimuth":
                    if (
                        target_value == candidate_value
                        or abs(target_value - candidate_value) == 180
                    ):
                        qty_matched += 1
                else:
                    if target_value == candidate_value:
                        qty_matched += 1

            if qty_matched > highest_qty_matched:
                highest_qty_matched = qty_matched
                best_match_found = candidate

        return best_match_found

    used_ids = set()

    if match_type == "Surfaces":
        for generated_object in generated_values:
            generated_object_id = generated_object.get("id")

            best_match = get_best_match_attrs(
                generated_object, reference_values, ["area", "azimuth"]
            )

            if best_match is not None:
                mapping[generated_object_id] = best_match.get("id")

    # If the match_type is not Surfaces, or if Surface matches could not be made based on area and azimuth, try to match based on id
    if len(mapping) != len(generated_object_ids):
        for object_id in generated_object_ids:
            best_match_id = get_best_match(object_id, reference_object_ids)
            if best_match_id is not None and best_match_id not in used_ids:
                mapping[object_id] = best_match_id
                used_ids.add(best_match_id)

    return mapping


def compare_fan_power(generated_fans):
    """Compare the design electric power based on design airflow."""
    errors = []

    for fan in generated_fans:
        design_airflow = fan.get("design_airflow")
        design_power = fan.get("design_electric_power")

        # Check if the design electric power is within the expected range
        if design_power != 0.3 * design_airflow:
            errors.append(
                f"Design electric power is not within the expected range: Expected {design_airflow}, got {design_power}"
            )

    return errors


def define_surface_map(generated_zone, reference_zone, generated_json, reference_json):
    generated_zone_id = generated_zone.get("id")
    surface_map = {}

    surface_types = [
        ("Exterior Wall", {"classification": "WALL", "adjacent_to": "EXTERIOR"}),
        ("Interior Wall", {"classification": "WALL", "adjacent_to": "INTERIOR"}),
        ("Ground Floor", {"classification": "FLOOR", "adjacent_to": "GROUND"}),
        ("Roof", {"classification": "CEILING", "adjacent_to": "EXTERIOR"}),
    ]

    for surface_name, filters in surface_types:
        generated_surfaces = find_all_with_filters(
            "$.surfaces[*]", filters, generated_zone
        )
        reference_surfaces = find_all_with_filters(
            "$.surfaces[*]", filters, reference_zone
        )

        if surface_name == "Interior Wall":
            # Extend with surfaces from other zones where this zone is the adjacent_zone
            generated_surfaces.extend(
                find_all_with_field_value(
                    "$.ruleset_model_descriptions[0].buildings[0].building_segments[0].zones[*].surfaces[*]",
                    "adjacent_zone",
                    generated_zone_id,
                    generated_json,
                )
            )
            reference_surfaces.extend(
                find_all_with_field_value(
                    "$.ruleset_model_descriptions[0].buildings[0].building_segments[0].zones[*].surfaces[*]",
                    "adjacent_zone",
                    reference_zone.get("id"),
                    reference_json,
                )
            )

        surface_map.update(
            match_surfaces(
                generated_zone_id, surface_name, generated_surfaces, reference_surfaces
            )[0]
        )

    return surface_map


def define_hvac_map(generated_zone, reference_zone, generated_json, reference_json):
    generated_zone_id = generated_zone.get("id")
    hvac_map = {}

    generated_hvacs = find_all(
        "$.ruleset_model_descriptions[0].buildings[0].building_segments[0].heating_ventilating_air_conditioning_systems",
        generated_json,
    )
    reference_hvacs = find_all(
        "$.ruleset_model_descriptions[0].buildings[0].building_segments[0].heating_ventilating_air_conditioning_systems",
        reference_json,
    )

    return hvac_map


def define_terminal_map(generated_zone, reference_zone, generated_json, reference_json):
    generated_zone_id = generated_zone.get("id")
    terminal_map = {}

    generated_terminals = find_all(
        "$.ruleset_model_descriptions[0].buildings[0].building_segments[0].heating_ventilating_air_conditioning_systems[*].terminal_units[*]",
        generated_json,
    )
    reference_terminals = find_all(
        "$.ruleset_model_descriptions[0].buildings[0].building_segments[0].heating_ventilating_air_conditioning_systems[*].terminal_units[*]",
        reference_json,
    )

    return terminal_map


def match_surfaces(zone_id, surface_type, generated_surfaces, reference_surfaces):
    errors = []
    local_surface_map = {}

    if len(generated_surfaces) != len(reference_surfaces):
        errors.append(
            f"{surface_type} surface count mismatch in zone id '{zone_id}': Expected {len(reference_surfaces)}, got {len(generated_surfaces)}"
        )
        return local_surface_map, errors

    elif len(generated_surfaces) == 1:
        local_surface_map[generated_surfaces[0].get("id")] = reference_surfaces[0].get(
            "id"
        )
        return local_surface_map, errors

    else:
        local_surface_map = find_matches_for(
            "Surfaces", generated_surfaces, reference_surfaces
        )
        return local_surface_map, errors


def compare_json_files(
    test_case_name, spec_file, generated_json_file, reference_json_file
):
    """Compares generated and reference JSON files according to the spec."""
    spec = load_json_file(spec_file)
    json_test_key_paths = spec.get("json-test-key-paths", [])

    generated_json = load_json_file(generated_json_file)
    reference_json = load_json_file(reference_json_file)

    warnings = []
    errors = []

    generated_zones = find_all(
        "$.ruleset_model_descriptions[0].buildings[0].building_segments[0].zones[*]",
        generated_json,
    )
    reference_zones = find_all(
        "$.ruleset_model_descriptions[0].buildings[0].building_segments[0].zones[*]",
        reference_json,
    )
    generated_zone_ids = [zone.get("id") for zone in generated_zones]
    reference_zone_ids = [zone.get("id") for zone in reference_zones]

    # Define a map for zones which will be used to define the maps of other objects
    object_id_map = find_matches_for("Zones", generated_zones, reference_zones)
    if not object_id_map:
        warnings.append(
            "Could not match zones between the generated and reference files. Try to align with the correct answer file naming conventions."
        )
        # Return early if zones could not be matched
        return warnings, errors

    for i, generated_zone in enumerate(generated_zones):
        generated_zone_id = generated_zone.get("id")
        reference_zone_id = object_id_map[generated_zone_id]
        reference_zone = reference_zones[reference_zone_ids.index(reference_zone_id)]

        # Define maps for surfaces, HVAC systems, and terminal units
        surface_map = define_surface_map(
            generated_zone, reference_zone, generated_json, reference_json
        )
        object_id_map.update(surface_map)

        hvac_map = define_hvac_map(
            generated_zone, reference_zone, generated_json, reference_json
        )
        object_id_map.update(hvac_map)

    # Once maps have been defined, iterate through the test specs
    for path_spec in json_test_key_paths:
        json_key_path = path_spec["json-key-path"]

        # Handle Special Case for design electric power based on design airflow (which is not a specified value)
        if json_key_path.split(".")[-1] == "design_electric_power":

            generated_supply_fan = find_all(
                "$.ruleset_model_descriptions[*].buildings[*].building_segments[*].heating_ventilating_air_conditioning_systems[*].fan_system.supply_fans",
                generated_json,
            )
            compare_fan_power_errors = compare_fan_power(generated_supply_fan)
            if compare_fan_power_errors:
                errors.extend(
                    f"Error in {test_case_name} at {json_key_path.split('.')[-1]}: {err}"
                    for err in compare_fan_power_errors
                )

        # Begin the General Comparison Methodology
        else:

            # Handle comparison of data derived from zones which may not be in the same order as the reference zones
            if (
                "zones[*]" in json_key_path
                and "surfaces[*]" not in json_key_path
                and "terminals[*]" not in json_key_path
            ):
                aligned_generated_values = []
                aligned_reference_values = []

                # Populate data for each zone individually and ensure correct alignment via object mapping
                for generated_zone in generated_zones:
                    generated_zone_id = generated_zone.get("id")
                    reference_zone_id = object_id_map[generated_zone_id]

                    # Extract values from aligned zones using the specified key path
                    aligned_generated_value = find_one(
                        json_key_path.replace(
                            "zones[*]", f'zones[*][?(@.id="{generated_zone_id}")]'
                        ),
                        generated_json,
                    )
                    if aligned_generated_value:
                        aligned_generated_values.append(aligned_generated_value)

                    aligned_reference_value = find_one(
                        json_key_path.replace(
                            "zones[*]", f'zones[*][?(@.id="{reference_zone_id}")]'
                        ),
                        reference_json,
                    )
                    if aligned_reference_value:
                        aligned_reference_values.append(aligned_reference_value)

                if not aligned_generated_values:
                    warnings.append(
                        f"Missing key {json_key_path.split('.')[-1]} in generated JSON for {test_case_name}."
                    )
                    continue

                general_comparison_errors = compare_json_values(
                    path_spec, aligned_generated_values, aligned_reference_values
                )
                errors.extend(general_comparison_errors)

            elif "surfaces[*]" in json_key_path:
                pass

            elif "terminals[*]" in json_key_path:
                pass

            elif "heating_ventilating_air_conditioning_systems[*]" in json_key_path:
                pass

            else:

                generated_values = find_all(json_key_path, generated_json)
                reference_values = find_all(json_key_path, reference_json)

                if not generated_values:
                    warnings.append(
                        f"Missing key {json_key_path.split('.')[-1]} in generated JSON for {test_case_name}."
                    )
                    continue

                #
                general_comparison_errors = compare_json_values(
                    path_spec, generated_values, reference_values
                )
                if general_comparison_errors:
                    errors.extend(
                        f"Error in {test_case_name} at {json_key_path.split('.')[-1]}: {err}"
                        for err in general_comparison_errors
                    )

    return warnings, errors


def run_comparison_for_all_tests(test_dir):
    """Runs JSON comparison for all test cases in the test directory."""

    reference_dir = os.path.join(test_dir, "Correct Answer RPDs")
    spec_dir = os.path.join(test_dir, "Test Specifications")

    for item in os.listdir(test_dir):
        if os.path.isdir(test_dir) and (item.startswith("E-") or item.startswith("F-")):

            test_case_dir = os.path.join(test_dir, item)
            generated_json_file = next(
                (
                    os.path.join(test_case_dir, f)
                    for f in os.listdir(test_case_dir)
                    if f.endswith(".json")
                ),
                None,
            )
            spec_file = os.path.join(spec_dir, f"{item} spec.json")
            reference_json_file = os.path.join(reference_dir, f"{item}.json")

            if (
                generated_json_file
                and os.path.isfile(spec_file)
                and os.path.isfile(generated_json_file)
                and os.path.isfile(reference_json_file)
            ):
                print(f"Running comparison for {item}...")
                warnings, errors = compare_json_files(
                    item, spec_file, generated_json_file, reference_json_file
                )

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
