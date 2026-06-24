import sys
import json
import math
from pathlib import Path
from difflib import get_close_matches
from enum import Enum

from rpd_generator.utilities.jsonpath_utils import (
    find_one,
    find_all,
    find_all_with_field_value,
    find_all_with_filters,
)
from rpd_generator.utilities.get_dict_of_zones_and_terminals_served_by_hvac_sys import (
    get_dict_of_zones_and_terminals_served_by_hvac_sys,
)
from rpd_generator.utilities.get_dict_of_surfaces_with_construction_assigned import (
    get_dict_of_surfaces_with_construction_assigned,
)


class EvaluationCriteriaOptions(Enum):
    VALUE = "VALUE"
    PRESENT = "PRESENT"
    REFERENCE = "REFERENCE"
    QUANTITY = "QUANTITY"


class TestOutcomeOptions(Enum):
    MATCH = "MATCH"
    DIFFER = "DIFFER"
    NOT_IMPLEMENTED = "NOT_IMPLEMENTED"
    UNKNOWN = "UNKNOWN"


TestOutcomeOptions.__test__ = False


# RPD Generation Test Report
results_data = {
    "generation_software_name": "",
    "generation_software_version": "",
    "modeling_software_name": "",
    "modeling_software_version": "",
    "schema_version": "",
    "ruleset_name": "",
    "ruleset_checking_specification_name": "",
    "test_case_reports": [],  # List of test case report dicts
}


# Test Case Report
def add_test_case_report(test_case_dir, generated_file_name):
    files_utilized = [
        f.name
        for f in test_case_dir.iterdir()
        if f.is_file() and f.suffix not in [".rpd"]
    ]
    test_case_report = {
        "test_id": test_case_dir.name,
        "generated_file_name": generated_file_name,
        "files_utilized": files_utilized,
        "specification_tests": [],
    }
    results_data["test_case_reports"].append(test_case_report)
    return test_case_report


# Specification Test
def add_specification_test(test_case_report, data_path, evaluation_criteria=""):
    specification_test = {
        "data_path": data_path,
        "evaluation_criteria": evaluation_criteria,
        "test_results": [],
    }
    test_case_report["specification_tests"].append(specification_test)
    return specification_test


# Test Result
def add_test_result(
    specification_test,
    generated_instance_id,
    reference_instance_id,
    test_outcome,
    notes="",
):
    data_element = specification_test["data_path"].split(".")[-1]
    test_result = {
        "generated_instance_id": generated_instance_id,  # if generated_instance_id else None,
        "reference_instance_id": (
            reference_instance_id if reference_instance_id else None
        ),
        "data_element": data_element,
        "test_outcome": test_outcome,
        "notes": notes,
    }
    specification_test["test_results"].append(test_result)
    return test_result


def load_json_file(file_path):
    """Loads JSON data from a file."""
    with open(file_path, "r") as file:
        return json.load(file)


def compare_json_values(
    spec,
    generated_values,
    reference_values,
    generated_ids,
    specification_test,
    object_id_map,
):
    """Compares a list of generated and reference JSON values based on the spec."""
    json_key_path = spec["json-key-path"]
    compare_value = spec.get("compare-value", True)
    tolerance = spec.get("tolerance", 0)

    warnings = []
    errors = []

    for i, generated_id in enumerate(generated_ids):

        if generated_id not in generated_values and i in generated_values:
            generated_id = i

        if generated_id not in generated_values:
            continue  # Skip if generated_id was not mapped successfully

        generated_value = generated_values[generated_id]
        reference_value = reference_values[generated_id]
        reference_id = object_id_map.get(generated_id)

        if isinstance(reference_id, dict):
            reference_id = reference_id.get("id")

        if generated_value is None and reference_value is not None:
            notes = f"Missing value for key '{json_key_path.split('.')[-1]}' at {generated_ids[i]}"
            add_test_result(
                specification_test,
                generated_id,
                reference_id,
                TestOutcomeOptions.NOT_IMPLEMENTED.value,
            )
            warnings.append(notes)
            continue

        if isinstance(reference_value, dict):
            raise ValueError("json-test-key-path should not result in a dictionary.")

        elif isinstance(reference_value, list):
            # Reference value is a list. Set EvaluationCriteriaOptions to QUANTITY
            specification_test[
                "evaluation_criteria"
            ] = EvaluationCriteriaOptions.QUANTITY.value

            if len(generated_value) != len(reference_value):
                notes = f"List length mismatch at '{generated_ids[i]}' for key '{json_key_path.split('.')[-1]}'. Expected: {len(reference_value)}; got: {len(generated_value)}"
                add_test_result(
                    specification_test,
                    generated_id if not isinstance(generated_id, int) else None,
                    reference_id if not isinstance(reference_id, int) else None,
                    TestOutcomeOptions.DIFFER.value,
                )
                errors.append(notes)
                continue
            else:
                add_test_result(
                    specification_test,
                    generated_id if not isinstance(generated_id, int) else None,
                    reference_id if not isinstance(reference_id, int) else None,
                    TestOutcomeOptions.MATCH.value,
                )

            if compare_value:
                # Reference value is a list with value comparisons. Combine QUANTITY and VALUE
                specification_test[
                    "evaluation_criteria"
                ] = EvaluationCriteriaOptions.VALUE.value

                for j, (gen_item, ref_item) in enumerate(
                    zip(generated_value, reference_value)
                ):
                    if gen_item != ref_item:
                        notes = f"List element mismatch for {generated_ids[i]} at index [{j}]. Expected: {ref_item}; got: {gen_item}"
                        add_test_result(
                            specification_test,
                            generated_id,
                            reference_id,
                            TestOutcomeOptions.DIFFER.value,
                        )
                        errors.append(notes)
                continue

        elif isinstance(reference_value, str) and not compare_value:
            specification_test[
                "evaluation_criteria"
            ] = EvaluationCriteriaOptions.REFERENCE.value

            if (
                generated_value in object_id_map
                and object_id_map[generated_value] == reference_value
            ) or ("schedule" in json_key_path):
                add_test_result(
                    specification_test,
                    generated_id if not isinstance(generated_id, int) else None,
                    reference_id if not isinstance(reference_id, int) else None,
                    TestOutcomeOptions.MATCH.value,
                )

            else:
                add_test_result(
                    specification_test,
                    generated_id,
                    reference_id,
                    TestOutcomeOptions.UNKNOWN.value,
                )

        if compare_value is False:
            # Check for presence of generated value
            if generated_value:
                add_test_result(
                    specification_test,
                    generated_id if not isinstance(generated_id, int) else None,
                    reference_id if not isinstance(reference_id, int) else None,
                    TestOutcomeOptions.MATCH.value,
                )
            else:
                notes = f"Missing value for key '{json_key_path.split('.')[-1]}' at {generated_ids[i]}"
                add_test_result(
                    specification_test,
                    generated_id if not isinstance(generated_id, int) else None,
                    reference_id if not isinstance(reference_id, int) else None,
                    TestOutcomeOptions.NOT_IMPLEMENTED.value,
                    notes,
                )
                warnings.append(notes)
            continue  # No comparison needed, just check for existence

        if reference_value is None and generated_value is None:
            continue  # Both values are None, no need to compare

        # Evaluate based on value comparison
        specification_test[
            "evaluation_criteria"
        ] = EvaluationCriteriaOptions.VALUE.value
        test_outcome = TestOutcomeOptions.NOT_IMPLEMENTED.value

        # Else: the values are strings, ints, or floats, and we need to compare them
        does_match = compare_values(generated_value, reference_value, tolerance)

        if does_match:
            test_outcome = TestOutcomeOptions.MATCH.value

        if not does_match and reference_value is None:
            warnings.append(
                f"Extra data provided at '{generated_ids[i]}' for key '{json_key_path.split('.')[-1]}'. Expected: 'None'; got: '{generated_value}'"
            )
            # Avoid adding a test result when extra data is provided
            continue

        elif not does_match:
            notes = f"Value mismatch at '{generated_ids[i]}' for key '{json_key_path.split('.')[-1]}'. Expected: '{reference_value}'; got: '{generated_value}'"
            errors.append(notes)
            test_outcome = TestOutcomeOptions.DIFFER.value

        add_test_result(
            specification_test,
            generated_id if not isinstance(generated_id, int) else None,
            reference_id if not isinstance(reference_id, int) else None,
            test_outcome,
        )

    if not generated_ids:
        notes = f"No generated IDs found for key '{json_key_path.split('.')[-1]}'"
        add_test_result(
            specification_test,
            None,
            None,
            TestOutcomeOptions.DIFFER.value,
        )
        warnings.append(notes)

    return warnings, errors


def get_zones_from_json(json_data):
    """Extracts zones from the given JSON data."""
    return find_all(
        "$.ruleset_model_descriptions[*].buildings[*].building_segments[*].zones[*]",
        json_data,
    )


def find_best_match(target, candidates, cutoff=0.4):
    """Finds the best match for a target in a list of candidates."""
    matches = get_close_matches(target, candidates, n=1, cutoff=cutoff)
    return matches[0] if matches else None


def get_mapping(
    match_type,
    generated_values,
    reference_values,
    generated_zone_id=None,
    reference_zone_id=None,
    object_id_map=None,
):
    """Find matches for a key in the generated and reference JSON based on the json path in the spec."""

    if len(generated_values) != len(reference_values):
        print(
            f"{match_type} count mismatch. Expected: {len(reference_values)}; got: {len(generated_values)}. Verify the object mapping."
        )
    mapping = {}
    if match_type == "Constructions":
        mapping = match_constructions_by_surfaces_assigned(
            generated_values, reference_values
        )

    elif match_type == "Materials":
        mapping = match_by_attributes_with_excess_generated(
            generated_values,
            reference_values,
            attrs=["thickness", "conductivity", "density", "specific_heat", "r_value"],
        )

    elif match_type == "Surfaces":
        mapping = match_by_attributes(
            generated_values,
            reference_values,
            generated_zone_id,
            reference_zone_id,
            ["area", "azimuth"],
        )

    elif match_type == "Subsurfaces":
        mapping = match_by_attributes(
            generated_values,
            reference_values,
            generated_zone_id,
            reference_zone_id,
            ["area", "azimuth", "classification"],
        )

    elif match_type == "HVAC Systems":
        mapping = match_sys_by_zones_served(
            generated_values, reference_values, object_id_map
        )
        if not mapping:
            mapping = match_by_attributes(
                generated_values,
                reference_values,
                generated_zone_id,
                reference_zone_id,
                ["cooling_system.type", "heating_system.type"],
            )

    elif match_type == "Terminals":
        mapping = match_terminals_by_references(
            generated_values, reference_values, object_id_map
        )

    elif match_type == "Boilers":
        mapping = match_by_attributes(
            generated_values,
            reference_values,
            generated_zone_id,
            reference_zone_id,
            ["draft_type", "energy_source_type"],
        )

    elif match_type == "Chillers":
        mapping = match_by_attributes(
            generated_values,
            reference_values,
            generated_zone_id,
            reference_zone_id,
            ["compressor_type", "energy_source_type"],
        )

    elif match_type == "Heat Rejections":
        mapping = match_by_attributes(
            generated_values,
            reference_values,
            generated_zone_id,
            reference_zone_id,
            ["type", "fan_type", "fan_speed_control"],
        )

    elif match_type == "Loops":
        mapping = match_by_attributes(
            generated_values,
            reference_values,
            generated_zone_id,
            reference_zone_id,
            ["type", "child_loops"],
        )

    elif match_type == "Pumps":
        mapping = match_pumps_by_references(
            generated_values, reference_values, object_id_map
        )

    if not mapping:
        mapping = match_by_id(generated_values, reference_values)

    # TODO: Expand capabilities when length of mapping is less than length of generated_values -e.g. unmatched objects
    if len(mapping) < len(generated_values):
        if isinstance(generated_values, dict):
            unmatched_objects = [
                generated_object_id
                for generated_object_id in generated_values
                if generated_object_id not in mapping
            ]
        elif isinstance(generated_values, list):
            unmatched_objects = [
                generated_object.get("id")
                for generated_object in generated_values
                if generated_object.get("id") not in mapping
            ]
        else:
            raise TypeError(
                f"Unsupported type for generated_values: {type(generated_values)}"
            )
        print(f"Unmatched {match_type} objects: {','.join(unmatched_objects)}")

    return mapping


def match_by_id(generated_values, reference_values):
    """Matches generated and reference objects by ID."""
    mapping, used_ids = {}, set()
    for generated_object in generated_values:
        best_match = find_best_match(
            generated_object.get("id"), [ref.get("id") for ref in reference_values]
        )
        if best_match and best_match not in used_ids:
            mapping[generated_object.get("id")] = best_match
            used_ids.add(best_match)
    return mapping


def match_by_attributes(
    generated_values, reference_values, generated_zone_id, reference_zone_id, attrs
):
    """Matches generated and reference objects based on specified attributes."""
    mapping = {}
    used_reference_ids = set()

    for generated_object in generated_values:
        best_match = get_best_match_attrs(
            generated_object,
            reference_values,
            attrs,
            generated_zone_id,
            reference_zone_id,
            used_reference_ids,
        )
        if best_match:
            mapping[generated_object.get("id")] = best_match.get("id")
            used_reference_ids.add(best_match.get("id"))

    return mapping


def match_by_attributes_with_excess_generated(
    generated_values, reference_values, attrs
):
    """Matches generated and reference objects based on specified attributes.

    Handles cases where generated list is longer than reference list.
    Each reference object is used at most once. Unmatched generated objects are excluded.
    """
    all_matches = []

    # Generate all possible (gen_id, ref_id, score) tuples
    for gen_obj in generated_values:
        gen_id = gen_obj.get("id")
        for ref_obj in reference_values:
            ref_id = ref_obj.get("id")
            score = sum(compare_attributes(gen_obj, ref_obj, attr) for attr in attrs)
            all_matches.append((gen_id, ref_id, score))

    # Sort all potential matches by descending score
    all_matches.sort(key=lambda x: -x[2])

    mapping = {}
    used_gen_ids = set()
    used_ref_ids = set()

    # Greedily select highest-scoring matches without reusing any IDs
    for gen_id, ref_id, score in all_matches:
        if gen_id not in used_gen_ids and ref_id not in used_ref_ids:
            mapping[gen_id] = ref_id
            used_gen_ids.add(gen_id)
            used_ref_ids.add(ref_id)

    return mapping


def match_constructions_by_surfaces_assigned(generated_values, reference_values):
    # Convert to list-of-dict format with `id` key for compatibility
    generated_list = [
        {"id": generated_id, **generated_data}
        for generated_id, generated_data in generated_values.items()
    ]
    reference_list = [
        {"id": reference_id, **reference_data}
        for reference_id, reference_data in reference_values.items()
    ]

    # Attributes to compare (numeric + counts)
    attrs = [
        "exterior_walls",
        "rooves",
        "below_grade_surfaces",
        "interior_surfaces",
        "primary_layers_length",
        "framing_layers_length",
        "u_factor",
        "c_factor",
        "f_factor",
    ]

    return match_by_attributes_with_excess_generated(
        generated_list,
        reference_list,
        attrs=attrs,
    )


def match_sys_by_zones_served(generated_values, reference_values, object_id_map):
    mapping = {}

    # reference map: frozenset of reference zones -> hvac id
    reference_zones_map = {
        frozenset(zone["id"] for zone in data["zones_list"]): ref_hvac_id
        for ref_hvac_id, data in reference_values.items()
    }

    # match each generated hvac
    for gen_hvac_id, gen_data in generated_values.items():
        generated_zones = gen_data["zones_list"]

        # convert generated zone ids to reference zone ids using zone map
        corresponding_reference_zones = [
            object_id_map.get(zone["id"]) for zone in generated_zones
        ]

        if None in corresponding_reference_zones:
            # tell us which reference zone is missing
            print(
                f"[WARN] Some zones for HVAC {gen_hvac_id} were not mapped: {', '.join([generated_zone['id'] for generated_zone in generated_zones])} -> {corresponding_reference_zones}"
            )
            continue

        key = frozenset(corresponding_reference_zones)

        if key in reference_zones_map:
            mapping[gen_hvac_id] = reference_zones_map[key]
        else:
            print(
                f"[WARN] No HVAC match found in reference for system serving zones {corresponding_reference_zones}"
            )

    return mapping


def match_terminals_by_references(generated_values, reference_values, object_id_map):
    """Matches generated and reference terminal objects based on references to the HVAC systems that serve them."""
    mapping = {}
    used_reference_ids = set()

    for generated_object in generated_values:
        generated_hvac_id = generated_object.get(
            "served_by_heating_ventilating_air_conditioning_system"
        )
        best_match = None

        if generated_hvac_id:
            reference_hvac_id = object_id_map.get(generated_hvac_id)
            if reference_hvac_id:
                best_match = next(
                    (
                        terminal
                        for terminal in reference_values
                        if terminal.get("id") not in used_reference_ids
                        and terminal.get(
                            "served_by_heating_ventilating_air_conditioning_system"
                        )
                        == reference_hvac_id
                    ),
                    None,
                )

        if not best_match:
            best_match = get_best_match_attrs(
                generated_object,
                reference_values,
                [
                    "type",
                    "is_supply_ducted",
                    "heating_source",
                    "heating_capacity",
                    "cooling_capacity",
                    "primary_airflow",
                    "minimum_outdoor_airflow",
                ],
                None,
                None,
                used_reference_ids,
            )

        if best_match:
            mapping[generated_object.get("id")] = best_match.get("id")
            used_reference_ids.add(best_match.get("id"))

    return mapping


def match_pumps_by_references(generated_values, reference_values, object_id_map):
    """Match generated and reference pumps based on references to the loops that they serve."""
    mapping = {}
    for generated_object in generated_values:
        generated_loop_id = generated_object.get("loop_or_piping")
        if generated_loop_id:
            reference_loop_id = object_id_map.get(generated_loop_id)
            if reference_loop_id:
                best_match = next(
                    (
                        reference_value
                        for reference_value in reference_values
                        if reference_value.get("loop_or_piping") == reference_loop_id
                    ),
                    None,
                )
                if best_match:
                    mapping[generated_object.get("id")] = best_match.get("id")
                    reference_values.remove(best_match)

    return mapping


def get_best_match_attrs(
    target, candidates, attrs, generated_zone_id, reference_zone_id, used_reference_ids
):
    """Finds the best match for a target object based on specified attributes,
    prioritizing unused candidates when scores are tied.
    """
    best_match_found = None
    highest_qty_matched = -1

    for candidate in candidates:
        qty_matched = sum(
            compare_attributes(
                target, candidate, attr, generated_zone_id, reference_zone_id
            )
            for attr in attrs
        )

        if qty_matched > highest_qty_matched:
            highest_qty_matched = qty_matched
            best_match_found = candidate
        elif qty_matched == highest_qty_matched:
            if (
                best_match_found
                and best_match_found.get("id") in used_reference_ids
                and candidate.get("id") not in used_reference_ids
            ):
                best_match_found = candidate

    return best_match_found


def compare_values(
    value, reference_value, absolute_tolerance=None, relative_tolerance=None
):
    """Compares a generated value with a reference value based on the tolerance."""
    if isinstance(reference_value, str):
        return value == reference_value

    if isinstance(reference_value, bool):
        return value == reference_value

    if isinstance(reference_value, (int, float)) and absolute_tolerance:
        return math.isclose(value, reference_value, abs_tol=absolute_tolerance)
    elif isinstance(reference_value, (int, float)) and relative_tolerance:
        return math.isclose(value, reference_value, rel_tol=relative_tolerance)

    return False


def compare_attributes(
    target, candidate, attr, generated_zone_id=None, reference_zone_id=None
):
    """Compares attributes between two objects, with special rules for azimuth and area."""
    if attr not in target:
        return False

    target_value, candidate_value = target.get(attr), candidate.get(attr)
    if attr == "azimuth":
        return compare_azimuth(
            target,
            candidate,
            generated_zone_id,
            reference_zone_id,
            target_value,
            candidate_value,
        )

    elif attr == "area":
        return compare_values(target_value, candidate_value, 0.1)

    elif isinstance(target_value, list):
        candidate_length = len(candidate_value) if candidate_value else 0
        return len(target_value) == candidate_length

    elif isinstance(target_value, (int, float)):
        return compare_values(target_value, candidate_value, relative_tolerance=0.01)

    else:
        return target_value == candidate_value


def compare_azimuth(
    target,
    candidate,
    generated_zone_id,
    reference_zone_id,
    target_value,
    candidate_value,
):
    """Special comparison rule for azimuth attributes."""
    mismatched_wall_origin_adjacent_zone = (
        target.get("adjacent_zone") == generated_zone_id
    ) != (candidate.get("adjacent_zone") == reference_zone_id)
    if (
        not mismatched_wall_origin_adjacent_zone and target_value == candidate_value
    ) or (
        mismatched_wall_origin_adjacent_zone
        and abs(target_value - candidate_value) == 180
    ):
        return 1
    return 0


def compare_fan_power(generated_fans, expected_w_per_flow):
    """Compare the design electric power based on design airflow."""
    warnings = []
    errors = []

    for fan in generated_fans:
        design_flow = fan.get("design_airflow")
        design_power = fan.get("design_electric_power")
        if not design_flow:
            warnings.append(f"Missing design airflow for '{fan['id']}'")
            continue

        if not design_power:
            warnings.append(f"Missing design electric power for '{fan['id']}'")
            continue

        if not compare_values(design_power, expected_w_per_flow * design_flow, 1):
            errors.append(
                f"Value mismatch at '{fan['id']}'. Expected: {expected_w_per_flow * design_flow}; got: {design_power}"
            )
    return warnings, errors


def compare_pump_power(pump: dict, expected_w_per_flow: float):
    """Compare the design electric power based on design airflow."""
    warnings = []
    errors = []

    design_flow = pump.get("design_flow")
    design_power = pump.get("design_electric_power")
    if not design_flow:
        warnings.append(f"Missing design flow for '{pump['id']}'")
        return warnings, errors

    if not design_power:
        warnings.append(f"Missing design electric power for '{pump['id']}'")
        return warnings, errors

    if not compare_values(design_power, expected_w_per_flow * design_flow, 1):
        errors.append(
            f"Value mismatch at '{pump['id']}'. Expected: {expected_w_per_flow * design_flow}; got: {design_power}"
        )
    return warnings, errors


def define_surface_map(generated_zone, reference_zone, generated_json, reference_json):
    generated_zone_id = generated_zone["id"]
    reference_zone_id = reference_zone["id"]
    surface_map = {}
    errors = []

    surface_types = [
        ("Exterior Wall", {"classification": "WALL", "adjacent_to": "EXTERIOR"}),
        ("Interior Wall", {"classification": "WALL", "adjacent_to": "INTERIOR"}),
        ("Ground Floor", {"classification": "FLOOR", "adjacent_to": "GROUND"}),
        ("Roof", {"classification": "CEILING", "adjacent_to": "EXTERIOR"}),
    ]

    for surface_type, filters in surface_types:
        generated_surfaces = find_all_with_filters(
            "$.surfaces[*]", filters, generated_zone
        )
        reference_surfaces = find_all_with_filters(
            "$.surfaces[*]", filters, reference_zone
        )

        if surface_type == "Interior Wall":
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
                    reference_zone_id,
                    reference_json,
                )
            )

        local_surface_map, local_surface_map_errors = define_local_surface_map(
            generated_zone_id,
            reference_zone_id,
            surface_type,
            generated_surfaces,
            reference_surfaces,
        )

        surface_map.update(local_surface_map)
        errors.extend(local_surface_map_errors)

    return surface_map, errors


def define_local_surface_map(
    generated_zone_id,
    reference_zone_id,
    surface_type,
    generated_surfaces,
    reference_surfaces,
):
    errors = []
    local_surface_map = {}

    if len(generated_surfaces) != len(reference_surfaces):
        errors.append(
            f"{surface_type} surface count mismatch in zone id '{generated_zone_id}'. Expected: {len(reference_surfaces)}; got: {len(generated_surfaces)}"
        )
        return local_surface_map, errors

    elif len(generated_surfaces) == 1:
        local_surface_map[generated_surfaces[0]["id"]] = reference_surfaces[0]["id"]
        return local_surface_map, errors

    else:
        local_surface_map = get_mapping(
            "Surfaces",
            generated_surfaces,
            reference_surfaces,
            generated_zone_id=generated_zone_id,
            reference_zone_id=reference_zone_id,
        )
        return local_surface_map, errors


def define_local_subsurface_map(surface_map, generated_json, reference_json):
    errors = []
    subsurface_map = {}

    for generated_surface_id, reference_surface_id in surface_map.items():
        generated_surface = find_one(
            f"$.ruleset_model_descriptions[0].buildings[0].building_segments[0].zones[*].surfaces[?(@.id=='{generated_surface_id}')]",
            generated_json,
        )
        reference_surface = find_one(
            f"$.ruleset_model_descriptions[0].buildings[0].building_segments[0].zones[*].surfaces[?(@.id=='{reference_surface_id}')]",
            reference_json,
        )

        generated_subsurfaces = find_all(
            "$.subsurfaces[*]",
            generated_surface,
        )
        reference_subsurfaces = find_all(
            "$.subsurfaces[*]",
            reference_surface,
        )

        if len(generated_subsurfaces) != len(reference_subsurfaces):
            errors.append(
                f"Subsurface count mismatch in surface id '{generated_surface_id}'. Expected: {len(reference_subsurfaces)}; got: {len(generated_subsurfaces)}"
            )
            continue

        if len(generated_subsurfaces) == 1:
            subsurface_map[generated_subsurfaces[0]["id"]] = reference_subsurfaces[0][
                "id"
            ]
            continue

        else:
            local_subsurface_map = get_mapping(
                "Subsurfaces",
                generated_subsurfaces,
                reference_subsurfaces,
            )
            subsurface_map.update(local_subsurface_map)

    return subsurface_map, errors


def define_hvac_map(generated_json, reference_json, object_id_map):
    errors = []
    hvac_map = {}
    generated_rmd = generated_json.get("ruleset_model_descriptions", [{}])[0]
    reference_rmd = reference_json.get("ruleset_model_descriptions", [{}])[0]
    generated_hvacs = get_dict_of_zones_and_terminals_served_by_hvac_sys(generated_rmd)
    reference_hvacs = get_dict_of_zones_and_terminals_served_by_hvac_sys(reference_rmd)

    if len(generated_hvacs) != len(reference_hvacs):
        errors.append(
            f"HVAC system count mismatch. Expected: {len(reference_hvacs)}; got: {len(generated_hvacs)}"
        )
        return hvac_map, errors

    if len(generated_hvacs) == 1:
        generated_hvac_id, generated_hvac_data = next(iter(generated_hvacs.items()))
        reference_hvac_id, reference_hvac_data = next(iter(reference_hvacs.items()))
        hvac_map[generated_hvac_id] = reference_hvac_id
        return hvac_map, errors

    else:
        hvac_map = get_mapping(
            "HVAC Systems",
            generated_hvacs,
            reference_hvacs,
            object_id_map=object_id_map,
        )

    return hvac_map, errors


def define_terminal_map(object_id_map, generated_zone, reference_zone):
    errors = []
    terminal_map = {}

    generated_terminals = find_all(
        "$.terminals[*]",
        generated_zone,
    )
    reference_terminals = find_all(
        "$.terminals[*]",
        reference_zone,
    )

    generated_zone_id = generated_zone.get("id")

    if len(generated_terminals) != len(reference_terminals):
        errors.append(
            f"Terminal count mismatch in zone id '{generated_zone_id}'. Expected: {len(reference_terminals)}; got: {len(generated_terminals)}"
        )
        return terminal_map, errors

    if len(generated_terminals) == 1:
        terminal_map[generated_terminals[0]["id"]] = reference_terminals[0]["id"]
        return terminal_map, errors

    else:
        terminal_map = get_mapping(
            "Terminals",
            generated_terminals,
            reference_terminals,
            generated_zone_id=generated_zone_id,
            reference_zone_id=reference_zone["id"],
            object_id_map=object_id_map,
        )
    return terminal_map, errors


def define_construction_map(generated_json, reference_json, object_id_map):
    errors = []
    construction_map = {}

    generated_constructions = get_dict_of_surfaces_with_construction_assigned(
        generated_json
    )
    reference_constructions = get_dict_of_surfaces_with_construction_assigned(
        reference_json
    )

    if (
        len(generated_constructions) == len(reference_constructions)
        and len(generated_constructions) == 1
    ):
        generated_hvac_id, generated_hvac_data = next(
            iter(generated_constructions.items())
        )
        reference_hvac_id, reference_hvac_data = next(
            iter(reference_constructions.items())
        )
        construction_map[generated_hvac_id] = reference_hvac_id
        return construction_map, errors

    else:
        construction_map = get_mapping(
            "Constructions",
            generated_constructions,
            reference_constructions,
            object_id_map=object_id_map,
        )

    return construction_map, errors


def define_materials_map(generated_json, reference_json, object_id_map):
    errors = []
    materials_map = {}

    generated_materials = find_all(
        "$.ruleset_model_descriptions[0].materials[*]", generated_json
    )
    reference_materials = find_all(
        "$.ruleset_model_descriptions[0].materials[*]", reference_json
    )

    primary_layer_ids = find_all(
        "$.ruleset_model_descriptions[0].constructions[*].primary_layers[*]",
        generated_json,
    )
    framing_layer_ids = find_all(
        "$.ruleset_model_descriptions[0].constructions[*].framing_layers[*]",
        generated_json,
    )

    # Combine both lists into a set for faster lookup
    referenced_ids = set(primary_layer_ids + framing_layer_ids)

    # Filter generated_materials to only include those whose id is referenced in primary_layer_ids or framing_layer_ids
    filtered_generated_materials = [
        mat for mat in generated_materials if mat.get("id") in referenced_ids
    ]

    if (
        len(filtered_generated_materials) == len(reference_materials)
        and len(filtered_generated_materials) == 1
    ):
        generated_material_data = filtered_generated_materials[0]
        reference_material_data = reference_materials[0]
        materials_map[generated_material_data["id"]] = reference_material_data["id"]
        return materials_map, errors

    else:
        materials_map = get_mapping(
            "Materials",
            filtered_generated_materials,
            reference_materials,
            object_id_map=object_id_map,
        )

    return materials_map, errors


def define_boiler_map(generated_json, reference_json, object_id_map):
    errors = []
    boiler_map = {}

    generated_boilers = find_all(
        "$.ruleset_model_descriptions[0].boilers[*]",
        generated_json,
    )
    reference_boilers = find_all(
        "$.ruleset_model_descriptions[0].boilers[*]",
        reference_json,
    )

    if len(generated_boilers) != len(reference_boilers):
        errors.append(
            f"Boiler count mismatch. Expected: {len(reference_boilers)}; got: {len(generated_boilers)}"
        )
        return boiler_map, errors

    if len(generated_boilers) == 1:
        generated_boiler_data = generated_boilers[0]
        reference_boiler_data = reference_boilers[0]
        boiler_map[generated_boiler_data["id"]] = reference_boiler_data["id"]
        return boiler_map, errors

    else:
        boiler_map = get_mapping(
            "Boilers",
            generated_boilers,
            reference_boilers,
            object_id_map=object_id_map,
        )

    return boiler_map, errors


def define_chiller_map(generated_json, reference_json, object_id_map):
    errors = []
    chiller_map = {}

    generated_chillers = find_all(
        "$.ruleset_model_descriptions[0].chillers[*]",
        generated_json,
    )
    reference_chillers = find_all(
        "$.ruleset_model_descriptions[0].chillers[*]",
        reference_json,
    )

    if len(generated_chillers) != len(reference_chillers):
        errors.append(
            f"Chiller count mismatch. Expected: {len(reference_chillers)}; got: {len(generated_chillers)}"
        )
        return chiller_map, errors

    if len(generated_chillers) == 1:
        generated_chiller_data = generated_chillers[0]
        reference_chiller_data = reference_chillers[0]
        chiller_map[generated_chiller_data["id"]] = reference_chiller_data["id"]
        return chiller_map, errors

    else:
        chiller_map = get_mapping(
            "Chillers",
            generated_chillers,
            reference_chillers,
            object_id_map=object_id_map,
        )

    return chiller_map, errors


def define_heat_rejection_map(generated_json, reference_json, object_id_map):
    errors = []
    heat_rejection_map = {}

    generated_heat_rejections = find_all(
        "$.ruleset_model_descriptions[0].heat_rejections[*]",
        generated_json,
    )
    reference_heat_rejections = find_all(
        "$.ruleset_model_descriptions[0].heat_rejections[*]",
        reference_json,
    )

    if len(generated_heat_rejections) != len(reference_heat_rejections):
        errors.append(
            f"Heat Rejection count mismatch. Expected: {len(reference_heat_rejections)}; got: {len(generated_heat_rejections)}"
        )
        return heat_rejection_map, errors

    if len(generated_heat_rejections) == 1:
        generated_heat_rejection_data = generated_heat_rejections[0]
        reference_heat_rejection_data = reference_heat_rejections[0]
        heat_rejection_map[
            generated_heat_rejection_data["id"]
        ] = reference_heat_rejection_data["id"]
        return heat_rejection_map, errors

    else:
        heat_rejection_map = get_mapping(
            "Heat Rejections",
            generated_heat_rejections,
            reference_heat_rejections,
            object_id_map=object_id_map,
        )

    return heat_rejection_map, errors


def define_loop_map(generated_json, reference_json, object_id_map):
    errors = []
    loop_map = {}

    generated_loops = find_all(
        "$.ruleset_model_descriptions[0].fluid_loops[*]",
        generated_json,
    )
    generated_loops.extend(
        find_all(
            "$.ruleset_model_descriptions[0].fluid_loops[*].child_loops[*]",
            generated_json,
        )
    )
    reference_loops = find_all(
        "$.ruleset_model_descriptions[0].fluid_loops[*]",
        reference_json,
    )
    reference_loops.extend(
        find_all(
            "$.ruleset_model_descriptions[0].fluid_loops[*].child_loops[*]",
            reference_json,
        )
    )

    if len(generated_loops) != len(reference_loops):
        errors.append(
            f"Loop count mismatch. Expected: {len(reference_loops)}; got: {len(generated_loops)}"
        )
        return loop_map, errors

    if len(generated_loops) == 1:
        generated_loop_data = generated_loops[0]
        reference_loop_data = reference_loops[0]
        loop_map[generated_loop_data["id"]] = reference_loop_data["id"]
        return loop_map, errors

    else:
        loop_map = get_mapping(
            "Loops",
            generated_loops,
            reference_loops,
            object_id_map=object_id_map,
        )

    return loop_map, errors


def define_pump_map(generated_json, reference_json, object_id_map):
    errors = []
    pump_map = {}

    generated_pumps = find_all(
        "$.ruleset_model_descriptions[0].pumps[*]",
        generated_json,
    )
    reference_pumps = find_all(
        "$.ruleset_model_descriptions[0].pumps[*]",
        reference_json,
    )

    if len(generated_pumps) != len(reference_pumps):
        errors.append(
            f"Pump count mismatch. Expected: {len(reference_pumps)}; got: {len(generated_pumps)}"
        )
        return pump_map, errors

    if len(generated_pumps) == 1:
        generated_pump_data = generated_pumps[0]
        reference_pump_data = reference_pumps[0]
        pump_map[generated_pump_data["id"]] = reference_pump_data["id"]
        return pump_map, errors

    else:
        pump_map = get_mapping(
            "Pumps",
            generated_pumps,
            reference_pumps,
            object_id_map=object_id_map,
        )

    return pump_map, errors


def map_objects(generated_json, reference_json):
    warnings = []
    errors = []

    generated_zones = get_zones_from_json(generated_json)
    reference_zones = get_zones_from_json(reference_json)

    # Define a map for Zones. ! Maps for other objects will depend on this map !
    object_id_map = get_mapping("Zones", generated_zones, reference_zones)

    if len(object_id_map) != len(reference_zones):
        errors.append(
            f"""Could not match zones between the generated and reference files. Try to better align your modeled zone names with the correct answer file's zone naming conventions.\n{chr(10).join(f"- {zone['id']}" for zone in reference_zones)}"""
        )  # chr(10) is a newline character
        # Return early if zones could not be matched
        return object_id_map, warnings, errors

    # Define maps for HVAC systems
    hvac_map, hvac_map_errors = define_hvac_map(
        generated_json, reference_json, object_id_map
    )
    object_id_map.update(hvac_map)
    errors.extend(hvac_map_errors)

    reference_zone_ids = [zone["id"] for zone in reference_zones]

    for i, generated_zone in enumerate(generated_zones):
        generated_zone_id = generated_zone["id"]
        reference_zone_id = object_id_map[generated_zone_id]
        reference_zone = reference_zones[reference_zone_ids.index(reference_zone_id)]

        # Define maps for surfaces
        surface_map, surface_map_errors = define_surface_map(
            generated_zone, reference_zone, generated_json, reference_json
        )
        object_id_map.update(surface_map)
        errors.extend(surface_map_errors)

        # Define maps for subsurfaces
        subsurface_map, subsurface_map_errors = define_local_subsurface_map(
            surface_map, generated_json, reference_json
        )
        object_id_map.update(subsurface_map)
        errors.extend(subsurface_map_errors)

        # Define maps for terminals
        terminal_map, terminal_map_errors = define_terminal_map(
            object_id_map,
            generated_zone,
            reference_zone,
        )
        object_id_map.update(terminal_map)
        errors.extend(terminal_map_errors)

    construction_map, construction_map_errors = define_construction_map(
        generated_json, reference_json, object_id_map
    )
    object_id_map.update(construction_map)
    errors.extend(construction_map_errors)

    materials_map, materials_map_errors = define_materials_map(
        generated_json, reference_json, object_id_map
    )
    object_id_map.update(materials_map)
    errors.extend(materials_map_errors)

    boiler_map, boiler_map_errors = define_boiler_map(
        generated_json, reference_json, object_id_map
    )
    object_id_map.update(boiler_map)
    errors.extend(boiler_map_errors)

    chiller_map, chiller_map_errors = define_chiller_map(
        generated_json, reference_json, object_id_map
    )
    object_id_map.update(chiller_map)
    errors.extend(chiller_map_errors)

    heat_rejection_map, heat_rejection_map_errors = define_heat_rejection_map(
        generated_json, reference_json, object_id_map
    )
    object_id_map.update(heat_rejection_map)
    errors.extend(heat_rejection_map_errors)

    loop_map, loop_map_errors = define_loop_map(
        generated_json, reference_json, object_id_map
    )
    object_id_map.update(loop_map)
    errors.extend(loop_map_errors)

    pump_map, pump_map_errors = define_pump_map(
        generated_json, reference_json, object_id_map
    )
    object_id_map.update(pump_map)
    errors.extend(pump_map_errors)

    return object_id_map, warnings, errors


def handle_special_cases(
    path_spec, object_id_map, generated_json, reference_json, specification_test
):
    warnings = []
    errors = []

    json_key_path = path_spec["json-key-path"]
    special_case = path_spec["special-case"]
    compare_value = path_spec.get("compare-value", True)
    tolerance = path_spec.get("tolerance", 0)

    specification_test["evaluation_criteria"] = (
        EvaluationCriteriaOptions.VALUE.value
        if compare_value
        else EvaluationCriteriaOptions.PRESENT.value
    )

    # Handle Special Case for design electric power based on design airflow (which is not a specified value)
    if special_case == "W/cfm":
        special_case_value = path_spec["special-case-value"]

        generated_supply_fans = [
            fan
            for sys_fans in find_all(
                "$.ruleset_model_descriptions[*].buildings[*].building_segments[*].heating_ventilating_air_conditioning_systems[*].fan_system.supply_fans",
                generated_json,
            )
            for fan in sys_fans
        ]
        compare_fan_power_warnings, compare_fan_power_errors = compare_fan_power(
            generated_supply_fans, special_case_value
        )
        if compare_fan_power_warnings:
            warnings.extend(compare_fan_power_warnings)
        if compare_fan_power_errors:
            errors.extend(compare_fan_power_errors)

    # Handle Special Case for design electric power based on design airflow (which is not a specified value)
    elif special_case == "W/GPM":
        special_case_value_dict = path_spec["special-case-value"]
        special_case_value = None

        generated_pumps = find_all(
            "$.ruleset_model_descriptions[*].pumps[*]",
            generated_json,
        )

        for pump in generated_pumps:
            pump_type = "primary"
            pump_id = pump.get("id")
            loop_id = pump.get("loop_or_piping")
            loop = find_all_with_field_value(
                "$.ruleset_model_descriptions[*].fluid_loops[*]",
                "id",
                loop_id,
                generated_json,
            )

            if not loop:
                pump_type = "secondary"
                loop = find_all_with_field_value(
                    "$.ruleset_model_descriptions[*].fluid_loops[*].child_loops[*]",
                    "id",
                    loop_id,
                    generated_json,
                )

            if not loop:
                errors.append(
                    f"Could not find loop with id '{loop_id}' for pump '{pump_id}'"
                )
                continue

            loop = loop[0]
            loop_type = loop.get("type")

            if loop_type == "COOLING" and pump_type == "primary":
                special_case_value = special_case_value_dict["PCHW"]
            elif loop_type == "COOLING" and pump_type == "secondary":
                special_case_value = special_case_value_dict["SCHW"]
            elif loop_type == "HEATING":
                special_case_value = special_case_value_dict["HW"]
            elif loop_type == "CONDENSER":
                special_case_value = special_case_value_dict["CW"]

            compare_pump_power_warnings, compare_pump_power_errors = compare_pump_power(
                pump, special_case_value
            )
            # Test mismatch if there are warnings from compare_pump_power
            if compare_pump_power_warnings:
                notes = ""
                for warn in compare_pump_power_warnings:
                    notes += f"{warn}\n"
                    warnings.extend(
                        f"Warning at {json_key_path.split('.')[-1]}: {warn}"
                    )
                add_test_result(
                    specification_test,
                    pump_id,
                    None,
                    TestOutcomeOptions.DIFFER.value,
                )
            if compare_pump_power_errors:
                errors.extend(
                    f"Error at {json_key_path.split('.')[-1]}: {err}"
                    for err in compare_pump_power_errors
                )

            # If no warnings or errors are produced from comparison, add MATCH test result
            if not compare_pump_power_warnings and not compare_pump_power_errors:
                # No reference ID since we are comparing the generated value to a predetermined special case value
                add_test_result(
                    specification_test,
                    pump_id,
                    None,
                    TestOutcomeOptions.MATCH.value,
                )

    # Handle Special Case for interior wall azimuths (which may be opposite due to the adjacent zone)
    elif special_case == "azimuth":
        aligned_generated_values = {}
        aligned_reference_values = {}

        generated_zones = get_zones_from_json(generated_json)

        generated_surfaces = find_all(
            json_key_path[
                : json_key_path.index("].", json_key_path.index("surfaces")) + 1
            ],
            generated_json,
        )

        # Iterate through the generated surfaces to populate data for each surface individually, ensuring correct alignment via object mapping
        for generated_surface in generated_surfaces:
            generated_surface_id = generated_surface["id"]
            reference_surface_id = object_id_map.get(generated_surface_id)

            if not reference_surface_id:
                errors.append(
                    f"Could not map '{generated_surface_id}' to a reference surface"
                )
                continue

            aligned_reference_surface = find_one(
                json_key_path[
                    : json_key_path.index("].", json_key_path.index("surfaces")) + 1
                ]
                + f"[?(@.id == '{reference_surface_id}')]",
                reference_json,
                None,
            )

            if not aligned_reference_surface:
                errors.append(
                    f"Could not find reference surface with id '{reference_surface_id}'"
                )
                continue

            generated_parent_zone = next(
                zone
                for zone in generated_zones
                if any(
                    surface["id"] == generated_surface_id
                    for surface in zone.get("surfaces", [])
                )
            )
            generated_parent_zone_id = generated_parent_zone["id"]
            reference_parent_zone_id = object_id_map.get(generated_parent_zone_id)

            generated_value = generated_surface.get(json_key_path.split(".")[-1])
            aligned_generated_values[generated_surface_id] = generated_value
            # Extract values from aligned surfaces using the specified key path
            if "surfaces[?(@" in json_key_path:
                aligned_reference_value = find_one(
                    json_key_path.replace(
                        "surfaces[?(",
                        f"surfaces[?(@.id == '{reference_surface_id}' & ",
                    ),
                    reference_json,
                    None,
                )
            else:
                aligned_reference_value = find_one(
                    json_key_path.replace(
                        "surfaces[*]",
                        f"surfaces[?(@.id == '{reference_surface_id}')]",
                    ),
                    reference_json,
                    None,
                )
            aligned_reference_values[generated_surface_id] = aligned_reference_value

            mismatched_wall_origin_adjacent_zone = (
                aligned_reference_surface.get("adjacent_zone")
                == reference_parent_zone_id
            ) != (generated_surface.get("adjacent_zone") == generated_parent_zone_id)
            if not (
                (
                    not mismatched_wall_origin_adjacent_zone
                    and aligned_reference_value == generated_value
                )
                or (
                    mismatched_wall_origin_adjacent_zone
                    and (aligned_reference_value + 180) % 360 == generated_value
                )
            ):
                expected_value = (
                    aligned_reference_value
                    if not mismatched_wall_origin_adjacent_zone
                    else (aligned_reference_value + 180) % 360
                )

                errors.append(
                    f"Value mismatch at '{generated_surface_id}' for key '{json_key_path.split('.')[-1]}': Expected '{expected_value}', got '{generated_value}'"
                )

        if all(value is None for value in aligned_generated_values.values()):
            notes = f"Missing key {json_key_path.split('.')[-1]}"
            add_test_result(
                specification_test,
                None,
                None,
                TestOutcomeOptions.NOT_IMPLEMENTED.value,
            )
            warnings.append(notes)
        else:
            add_test_result(
                specification_test,
                None,
                None,
                TestOutcomeOptions.MATCH.value,
            )

    elif special_case == "operation_lower_limit":
        sequence = path_spec.get("special-case-value", {}).get("sequence")

        if not sequence:
            raise ValueError(
                "Special case value for operation upper limit must include a controls sequence."
            )

        if sequence == "staged":
            generated_boilers = find_all(
                json_key_path[
                    : json_key_path.index("].", json_key_path.index("boilers")) + 1
                ],
                generated_json,
            )
            is_staged = True
            expected_lower_limit = 0.0

            # Sort by operation_lower_limit
            sorted_boilers = sorted(
                generated_boilers,
                key=lambda b: b.get("operation_lower_limit", float("inf")),
            )

            for boiler in sorted_boilers:
                boiler_id = boiler.get("id")
                lower_limit = boiler.get("operation_lower_limit", 0)
                rated_capacity = boiler.get("rated_capacity", 0)

                if not compare_values(lower_limit, expected_lower_limit, tolerance):
                    notes = f"{boiler_id} operation lower limit incorrect for staged operation. Expected: {expected_lower_limit}; got: {lower_limit}"
                    add_test_result(
                        specification_test,
                        boiler_id,
                        None,
                        TestOutcomeOptions.DIFFER.value,
                    )
                    warnings.append(notes)
                    is_staged = False
                else:
                    # Correct answer is not dependent on a reference value, so there is no reference ID
                    add_test_result(
                        specification_test,
                        boiler_id,
                        None,
                        TestOutcomeOptions.MATCH.value,
                    )

                expected_lower_limit += rated_capacity

            if not is_staged:
                warnings.append(
                    "Boilers are not staged based on operation lower limits."
                )

        else:
            raise ValueError(
                f"Logic for operation lower limit special case is not implemented for the '{sequence}' sequence."
            )

    elif special_case == "operation_upper_limit":
        sequence = path_spec.get("special-case-value", {}).get("sequence")

        if not sequence:
            raise ValueError(
                "Special case value for operation upper limit must include a controls sequence."
            )

        if sequence == "staged":
            generated_boilers = find_all(
                json_key_path[
                    : json_key_path.index("].", json_key_path.index("boilers")) + 1
                ],
                generated_json,
            )
            is_staged = True

            # Create list of (boiler, capacity) and sort by operation_upper_limit
            boilers_with_capacity = [
                (boiler, boiler.get("rated_capacity", 0))
                for boiler in generated_boilers
            ]
            sorted_boilers = sorted(
                boilers_with_capacity,
                key=lambda pair: pair[0].get("operation_upper_limit", float("inf")),
            )

            expected_upper_limit = 0.0
            for boiler, capacity in sorted_boilers:
                boiler_id = boiler.get("id")
                expected_upper_limit += capacity
                actual_upper_limit = boiler.get("operation_upper_limit", 0)

                if not compare_values(
                    actual_upper_limit, expected_upper_limit, tolerance
                ):
                    notes = f"{boiler_id} operation upper limit incorrect for staged operation. Expected: {expected_upper_limit}; got: {actual_upper_limit}"
                    add_test_result(
                        specification_test,
                        boiler_id,
                        None,
                        TestOutcomeOptions.DIFFER.value,
                    )
                    warnings.append(notes)
                    is_staged = False
                else:
                    add_test_result(
                        specification_test,
                        boiler_id,
                        None,
                        TestOutcomeOptions.MATCH.value,
                    )

            if not is_staged:
                warnings.append(
                    "Boilers are not staged based on operation upper limits."
                )

        else:
            raise ValueError(
                f"Logic for operation lower limit special case is not implemented for the '{sequence}' sequence."
            )

    return warnings, errors


def handle_ordered_comparisons(
    path_spec, object_id_map, reference_json, generated_json, specification_test
):
    json_key_path = path_spec["json-key-path"]
    compare_value = path_spec.get("compare-value", True)

    specification_test["evaluation_criteria"] = (
        EvaluationCriteriaOptions.VALUE.value
        if compare_value
        else EvaluationCriteriaOptions.PRESENT.value
    )

    warnings = []
    errors = []

    # Handle comparison of data derived from zones which may not be in the same order as the reference zones
    if (
        "zones[" in json_key_path
        and "surfaces[" not in json_key_path
        and "terminals[" not in json_key_path
    ):
        aligned_generated_values = {}
        aligned_reference_values = {}

        generated_zones = get_zones_from_json(generated_json)
        generated_zone_ids = [zone["id"] for zone in generated_zones]

        # Populate data for each zone individually and ensure correct alignment via object mapping
        for generated_zone in generated_zones:
            generated_zone_id = generated_zone["id"]
            reference_zone_id = object_id_map[generated_zone_id]

            zone_data_path = json_key_path[
                (json_key_path.index("].", json_key_path.index("zones")) + 2) :
            ]
            generated_value = find_one(zone_data_path, generated_zone)
            aligned_generated_values[generated_zone_id] = generated_value
            # Extract values from aligned zones using the specified key path
            aligned_reference_value = find_one(
                json_key_path.replace(
                    "zones[*]", f"zones[?(@.id == '{reference_zone_id}')]"
                ),
                reference_json,
                None,
            )

            aligned_reference_values[generated_zone_id] = aligned_reference_value

        if all(value is None for value in aligned_generated_values.values()):
            notes = f"Missing key {json_key_path.split('.')[-1]}"
            add_test_result(
                specification_test,
                None,
                None,
                TestOutcomeOptions.NOT_IMPLEMENTED.value,
            )
            warnings.append(notes)
            return warnings, errors

        general_comparison_warnings, general_comparison_errors = compare_json_values(
            path_spec,
            aligned_generated_values,
            aligned_reference_values,
            generated_zone_ids,
            specification_test,
            object_id_map,
        )
        errors.extend(general_comparison_errors)

    elif "surfaces[" in json_key_path:
        # Handle comparison of data derived from surfaces which may not be in the same order as the reference surfaces
        aligned_generated_values = {}
        aligned_reference_values = {}

        # Populate data for each surface individually and ensure correct alignment via object mapping
        generated_surfaces = find_all(
            # Extract the key path for the surface (everything before surfaces[]. )
            json_key_path[
                : json_key_path.index("].", json_key_path.index("surfaces")) + 1
            ],
            generated_json,
        )
        generated_surface_ids = [surface["id"] for surface in generated_surfaces]

        for generated_surface in generated_surfaces:
            generated_surface_id = generated_surface["id"]
            reference_surface_id = object_id_map.get(generated_surface_id)

            # Extract the key path for the surface data (everything after surfaces[]. )
            generated_value = find_one(
                json_key_path[
                    json_key_path.index("].", json_key_path.index("surfaces")) + 2 :
                ],
                generated_surface,
            )
            aligned_generated_values[generated_surface_id] = generated_value

            # Extract values from aligned surfaces using the specified key path
            if "surfaces[?(@" in json_key_path:
                aligned_reference_value = find_one(
                    json_key_path.replace(
                        "surfaces[?(",
                        f"surfaces[?(@.id == '{reference_surface_id}' & ",
                    ),
                    reference_json,
                    None,
                )
            else:
                aligned_reference_value = find_one(
                    json_key_path.replace(
                        "surfaces[*]",
                        f"surfaces[?(@.id == '{reference_surface_id}')]",
                    ),
                    reference_json,
                    None,
                )

            aligned_reference_values[generated_surface_id] = aligned_reference_value

        if all(value is None for value in aligned_generated_values.values()):
            notes = f"Missing key {json_key_path.split('.')[-1]}"
            add_test_result(
                specification_test,
                None,
                None,
                TestOutcomeOptions.NOT_IMPLEMENTED.value,
            )
            warnings.append(notes)
            return warnings, errors

        general_comparison_warnings, general_comparison_errors = compare_json_values(
            path_spec,
            aligned_generated_values,
            aligned_reference_values,
            generated_surface_ids,
            specification_test,
            object_id_map,
        )
        warnings.extend(general_comparison_warnings)
        errors.extend(general_comparison_errors)

    elif "subsurfaces[" in json_key_path:
        # Handle comparison of data derived from subsurfaces which may not be in the same order as the reference subsurfaces
        aligned_generated_values = {}
        aligned_reference_values = {}

        # Populate data for each subsurface individually and ensure correct alignment via object mapping
        generated_subsurfaces = find_all(
            # Extract the key path for the subsurface (everything before subsurfaces[]. )
            json_key_path[
                : json_key_path.index("].", json_key_path.index("subsurfaces")) + 1
            ],
            generated_json,
        )
        generated_subsurface_ids = [
            subsurface["id"] for subsurface in generated_subsurfaces
        ]

        for generated_subsurface in generated_subsurfaces:
            generated_subsurface_id = generated_subsurface["id"]
            reference_subsurface_id = object_id_map.get(generated_subsurface_id)

            # Extract the key path for the subsurface data (everything after subsurfaces[]. )
            generated_value = find_one(
                json_key_path[
                    json_key_path.index("].", json_key_path.index("subsurfaces")) + 2 :
                ],
                generated_subsurface,
            )
            aligned_generated_values[generated_subsurface_id] = generated_value

            # Extract values from aligned subsurfaces using the specified key path
            if "subsurfaces[?(@" in json_key_path:
                aligned_reference_value = find_one(
                    json_key_path.replace(
                        "subsurfaces[?(",
                        f"subsurfaces[?(@.id == '{reference_subsurface_id}' & ",
                    ),
                    reference_json,
                    None,
                )
            else:
                aligned_reference_value = find_one(
                    json_key_path.replace(
                        "subsurfaces[*]",
                        f"subsurfaces[?(@.id == '{reference_subsurface_id}')]",
                    ),
                    reference_json,
                    None,
                )

            aligned_reference_values[generated_subsurface_id] = aligned_reference_value

        if all(value is None for value in aligned_generated_values.values()):
            notes = f"Missing key {json_key_path.split('.')[-1]}"
            add_test_result(
                specification_test,
                None,
                None,
                TestOutcomeOptions.NOT_IMPLEMENTED.value,
            )
            warnings.append(notes)
            return warnings, errors

        general_comparison_warnings, general_comparison_errors = compare_json_values(
            path_spec,
            aligned_generated_values,
            aligned_reference_values,
            generated_subsurface_ids,
            specification_test,
            object_id_map,
        )
        warnings.extend(general_comparison_warnings)
        errors.extend(general_comparison_errors)

    elif "terminals[" in json_key_path:
        # Handle comparison of data derived from surfaces which may not be in the same order as the reference surfaces
        aligned_generated_values = {}
        aligned_reference_values = {}

        # Populate data for each surface individually and ensure correct alignment via object mapping
        generated_terminals = find_all(
            # Extract the key path for the surface (everything before surfaces[]. )
            json_key_path[
                : json_key_path.index("].", json_key_path.index("terminals")) + 1
            ],
            generated_json,
        )
        generated_terminal_ids = [terminal["id"] for terminal in generated_terminals]

        for generated_terminal in generated_terminals:
            generated_terminal_id = generated_terminal["id"]
            reference_terminal_id = object_id_map.get(generated_terminal_id)

            # Extract the key path for the terminal data (everything after terminals[]. )
            generated_value = find_one(
                json_key_path[
                    json_key_path.index("].", json_key_path.index("terminals")) + 2 :
                ],
                generated_terminal,
            )
            aligned_generated_values[generated_terminal_id] = generated_value

            # Extract values from aligned terminals using the specified key path
            if "terminals[?(@" in json_key_path:
                aligned_reference_value = find_one(
                    json_key_path.replace(
                        "terminals[?(",
                        f'terminals[?(@.id=="{reference_terminal_id}" & ',
                    ),
                    reference_json,
                    None,
                )
            else:
                aligned_reference_value = find_one(
                    json_key_path.replace(
                        "terminals[*]",
                        f"terminals[?(@.id == '{reference_terminal_id}')]",
                    ),
                    reference_json,
                    None,
                )

            aligned_reference_values[generated_terminal_id] = aligned_reference_value

        if all(value is None for value in aligned_generated_values.values()):
            notes = f"Missing key {json_key_path.split('.')[-1]}"
            add_test_result(
                specification_test,
                None,
                None,
                TestOutcomeOptions.NOT_IMPLEMENTED.value,
            )
            warnings.append(notes)
            return warnings, errors

        general_comparison_warnings, general_comparison_errors = compare_json_values(
            path_spec,
            aligned_generated_values,
            aligned_reference_values,
            generated_terminal_ids,
            specification_test,
            object_id_map,
        )
        warnings.extend(general_comparison_warnings)
        errors.extend(general_comparison_errors)

    elif "constructions[" in json_key_path:
        aligned_generated_values = {}
        aligned_reference_values = {}

        generated_constructions = find_all(
            json_key_path[
                : json_key_path.index("].", json_key_path.index("constructions")) + 1
            ],
            generated_json,
        )
        generated_construction_ids = [
            construction["id"] for construction in generated_constructions
        ]

        for generated_construction in generated_constructions:
            generated_construction_id = generated_construction["id"]
            reference_construction_id = object_id_map.get(generated_construction_id)

            if isinstance(reference_construction_id, dict):
                reference_construction_id = reference_construction_id.get("id")

            if not reference_construction_id:
                continue

            construction_data_path = json_key_path[
                json_key_path.index("].", json_key_path.index("constructions")) + 2 :
            ]
            generated_value = find_one(construction_data_path, generated_construction)
            aligned_generated_values[generated_construction_id] = generated_value

            aligned_reference_value = find_one(
                json_key_path.replace(
                    "constructions[*]",
                    f"constructions[?(@.id == '{reference_construction_id}')]",
                ),
                reference_json,
                None,
            )

            aligned_reference_values[
                generated_construction_id
            ] = aligned_reference_value

        if all(value is None for value in aligned_generated_values.values()):
            notes = f"Missing key {json_key_path.split('.')[-1]}"
            add_test_result(
                specification_test,
                None,
                None,
                TestOutcomeOptions.NOT_IMPLEMENTED.value,
            )
            warnings.append(notes)
            return warnings, errors

        general_comparison_warnings, general_comparison_errors = compare_json_values(
            path_spec,
            aligned_generated_values,
            aligned_reference_values,
            generated_construction_ids,
            specification_test,
            object_id_map,
        )
        errors.extend(general_comparison_errors)

    elif "materials[" in json_key_path:
        aligned_generated_values = {}
        aligned_reference_values = {}

        generated_materials = find_all(
            json_key_path[
                : json_key_path.index("].", json_key_path.index("materials")) + 1
            ],
            generated_json,
        )
        generated_material_ids = [material["id"] for material in generated_materials]

        for generated_material in generated_materials:
            generated_material_id = generated_material["id"]
            reference_material_id = object_id_map.get(generated_material_id)

            if isinstance(reference_material_id, dict):
                reference_material_id = reference_material_id.get("id")

            if not reference_material_id:
                continue

            material_data_path = json_key_path[
                json_key_path.index("].", json_key_path.index("materials")) + 2 :
            ]
            generated_value = find_one(material_data_path, generated_material)
            aligned_generated_values[generated_material_id] = generated_value

            aligned_reference_value = find_one(
                json_key_path.replace(
                    "materials[*]",
                    f"materials[?(@.id == '{reference_material_id}')]",
                ),
                reference_json,
                None,
            )

            aligned_reference_values[generated_material_id] = aligned_reference_value

        if all(value is None for value in aligned_generated_values.values()):
            notes = f"Missing key {json_key_path.split('.')[-1]}"
            add_test_result(
                specification_test,
                None,
                None,
                TestOutcomeOptions.NOT_IMPLEMENTED.value,
            )
            warnings.append(notes)
            return warnings, errors

        general_comparison_warnings, general_comparison_errors = compare_json_values(
            path_spec,
            aligned_generated_values,
            aligned_reference_values,
            generated_material_ids,
            specification_test,
            object_id_map,
        )
        errors.extend(general_comparison_errors)

    elif "heating_ventilating_air_conditioning_systems[" in json_key_path:
        aligned_generated_values = {}
        aligned_reference_values = {}

        generated_hvacs = find_all(
            json_key_path[
                : json_key_path.index(
                    "].",
                    json_key_path.index("heating_ventilating_air_conditioning_systems"),
                )
                + 1
            ],
            generated_json,
        )
        generated_hvac_ids = [hvac["id"] for hvac in generated_hvacs]

        # Populate data for each zone individually and ensure correct alignment via object mapping
        for generated_hvac in generated_hvacs:
            generated_hvac_id = generated_hvac["id"]
            reference_hvac_id = object_id_map.get(generated_hvac_id)

            if not reference_hvac_id:
                continue

            hvac_data_path = json_key_path[
                json_key_path.index(
                    "].",
                    json_key_path.index("heating_ventilating_air_conditioning_systems"),
                )
                + 2 :
            ]
            generated_value = find_one(hvac_data_path, generated_hvac)
            aligned_generated_values[generated_hvac_id] = generated_value
            # Extract values from aligned zones using the specified key path
            aligned_reference_value = find_one(
                json_key_path.replace(
                    "heating_ventilating_air_conditioning_systems[*]",
                    f"heating_ventilating_air_conditioning_systems[?(@.id == '{reference_hvac_id}')]",
                ),
                reference_json,
                None,
            )

            aligned_reference_values[generated_hvac_id] = aligned_reference_value

        if all(value is None for value in aligned_generated_values.values()):
            notes = f"Missing key {json_key_path.split('.')[-1]}"
            add_test_result(
                specification_test,
                None,
                None,
                TestOutcomeOptions.NOT_IMPLEMENTED.value,
            )
            warnings.append(notes)
            return warnings, errors

        general_comparison_warnings, general_comparison_errors = compare_json_values(
            path_spec,
            aligned_generated_values,
            aligned_reference_values,
            generated_hvac_ids,
            specification_test,
            object_id_map,
        )
        errors.extend(general_comparison_errors)

    elif "boilers[" in json_key_path:
        aligned_generated_values = {}
        aligned_reference_values = {}

        generated_boilers = find_all(
            json_key_path[
                : json_key_path.index("].", json_key_path.index("boilers")) + 1
            ],
            generated_json,
        )
        generated_boiler_ids = [boiler["id"] for boiler in generated_boilers]

        for generated_boiler in generated_boilers:
            generated_boiler_id = generated_boiler["id"]
            reference_boiler_id = object_id_map.get(generated_boiler_id)

            if not reference_boiler_id:
                continue

            boiler_data_path = json_key_path[
                json_key_path.index("].", json_key_path.index("boilers")) + 2 :
            ]
            generated_value = find_one(boiler_data_path, generated_boiler)
            aligned_generated_values[generated_boiler_id] = generated_value

            aligned_reference_value = find_one(
                json_key_path.replace(
                    "boilers[*]",
                    f"boilers[?(@.id == '{reference_boiler_id}')]",
                ),
                reference_json,
                None,
            )

            aligned_reference_values[generated_boiler_id] = aligned_reference_value

        if all(value is None for value in aligned_generated_values.values()):
            notes = f"Missing key {json_key_path.split('.')[-1]}"
            add_test_result(
                specification_test,
                None,
                None,
                TestOutcomeOptions.NOT_IMPLEMENTED.value,
            )
            warnings.append(notes)
            return warnings, errors

        general_comparison_warnings, general_comparison_errors = compare_json_values(
            path_spec,
            aligned_generated_values,
            aligned_reference_values,
            generated_boiler_ids,
            specification_test,
            object_id_map,
        )
        errors.extend(general_comparison_errors)

    elif "chillers[" in json_key_path:
        aligned_generated_values = {}
        aligned_reference_values = {}

        generated_chillers = find_all(
            json_key_path[
                : json_key_path.index("].", json_key_path.index("chillers")) + 1
            ],
            generated_json,
        )
        generated_chiller_ids = [chiller["id"] for chiller in generated_chillers]

        for generated_chiller in generated_chillers:
            generated_chiller_id = generated_chiller["id"]
            reference_chiller_id = object_id_map.get(generated_chiller_id)

            if not reference_chiller_id:
                continue

            chiller_data_path = json_key_path[
                json_key_path.index("].", json_key_path.index("chillers")) + 2 :
            ]
            generated_value = find_one(chiller_data_path, generated_chiller)
            aligned_generated_values[generated_chiller_id] = generated_value

            aligned_reference_value = find_one(
                json_key_path.replace(
                    "chillers[*]",
                    f"chillers[?(@.id == '{reference_chiller_id}')]",
                ),
                reference_json,
                None,
            )

            aligned_reference_values[generated_chiller_id] = aligned_reference_value

        if all(value is None for value in aligned_generated_values.values()):
            notes = f"Missing key {json_key_path.split('.')[-1]}"
            add_test_result(
                specification_test,
                None,
                None,
                TestOutcomeOptions.NOT_IMPLEMENTED.value,
            )
            warnings.append(notes)
            return warnings, errors

        general_comparison_warnings, general_comparison_errors = compare_json_values(
            path_spec,
            aligned_generated_values,
            aligned_reference_values,
            generated_chiller_ids,
            specification_test,
            object_id_map,
        )
        errors.extend(general_comparison_errors)

    elif "heat_rejections[" in json_key_path:
        aligned_generated_values = {}
        aligned_reference_values = {}

        generated_heat_rejections = find_all(
            json_key_path[
                : json_key_path.index("].", json_key_path.index("heat_rejections")) + 1
            ],
            generated_json,
        )
        generated_heat_rejection_ids = [
            heat_rejection["id"] for heat_rejection in generated_heat_rejections
        ]

        for generated_heat_rejection in generated_heat_rejections:
            generated_heat_rejection_id = generated_heat_rejection["id"]
            reference_heat_rejection_id = object_id_map.get(generated_heat_rejection_id)

            if not reference_heat_rejection_id:
                continue

            heat_rejection_data_path = json_key_path[
                json_key_path.index("].", json_key_path.index("heat_rejections")) + 2 :
            ]
            generated_value = find_one(
                heat_rejection_data_path, generated_heat_rejection
            )
            aligned_generated_values[generated_heat_rejection_id] = generated_value

            aligned_reference_value = find_one(
                json_key_path.replace(
                    "heat_rejections[*]",
                    f"heat_rejections[?(@.id == '{reference_heat_rejection_id}')]",
                ),
                reference_json,
                None,
            )

            aligned_reference_values[
                generated_heat_rejection_id
            ] = aligned_reference_value

        if all(value is None for value in aligned_generated_values.values()):
            notes = f"Missing key {json_key_path.split('.')[-1]}"
            add_test_result(
                specification_test,
                None,
                None,
                TestOutcomeOptions.NOT_IMPLEMENTED.value,
            )
            warnings.append(notes)
            return warnings, errors

        general_comparison_warnings, general_comparison_errors = compare_json_values(
            path_spec,
            aligned_generated_values,
            aligned_reference_values,
            generated_heat_rejection_ids,
            specification_test,
            object_id_map,
        )
        errors.extend(general_comparison_errors)

    elif "fluid_loops[" in json_key_path:
        aligned_generated_values = {}
        aligned_reference_values = {}

        generated_fluid_loops = find_all(
            json_key_path[
                : json_key_path.index("].", json_key_path.index("fluid_loops")) + 1
            ],
            generated_json,
        )
        generated_fluid_loop_ids = [
            fluid_loop["id"] for fluid_loop in generated_fluid_loops
        ]

        for generated_fluid_loop in generated_fluid_loops:
            generated_fluid_loop_id = generated_fluid_loop["id"]
            reference_fluid_loop_id = object_id_map.get(generated_fluid_loop_id)

            if not reference_fluid_loop_id:
                continue

            fluid_loop_data_path = json_key_path[
                json_key_path.index("].", json_key_path.index("fluid_loops")) + 2 :
            ]
            generated_value = find_one(fluid_loop_data_path, generated_fluid_loop)
            aligned_generated_values[generated_fluid_loop_id] = generated_value

            aligned_reference_value = find_one(
                json_key_path.replace(
                    "fluid_loops[*]",
                    f"fluid_loops[?(@.id == '{reference_fluid_loop_id}')]",
                ),
                reference_json,
                None,
            )

            aligned_reference_values[generated_fluid_loop_id] = aligned_reference_value

        if all(value is None for value in aligned_generated_values.values()):
            notes = f"Missing key {json_key_path.split('.')[-1]}"
            add_test_result(
                specification_test,
                None,
                None,
                TestOutcomeOptions.NOT_IMPLEMENTED.value,
            )
            warnings.append(notes)
            return warnings, errors

        general_comparison_warnings, general_comparison_errors = compare_json_values(
            path_spec,
            aligned_generated_values,
            aligned_reference_values,
            generated_fluid_loop_ids,
            specification_test,
            object_id_map,
        )
        errors.extend(general_comparison_errors)

    elif "pumps[" in json_key_path:
        aligned_generated_values = {}
        aligned_reference_values = {}

        generated_pumps = find_all(
            json_key_path[
                : json_key_path.index("].", json_key_path.index("pumps")) + 1
            ],
            generated_json,
        )
        generated_pump_ids = [pump["id"] for pump in generated_pumps]

        for generated_pump in generated_pumps:
            generated_pump_id = generated_pump["id"]
            reference_pump_id = object_id_map.get(generated_pump_id)

            if isinstance(reference_pump_id, dict):
                reference_pump_id = reference_pump_id.get("id")

            if not reference_pump_id:
                continue

            pump_data_path = json_key_path[
                json_key_path.index("].", json_key_path.index("pumps")) + 2 :
            ]
            generated_value = find_one(pump_data_path, generated_pump)
            aligned_generated_values[generated_pump_id] = generated_value

            aligned_reference_value = find_one(
                json_key_path.replace(
                    "pumps[*]",
                    f"pumps[?(@.id == '{reference_pump_id}')]",
                ),
                reference_json,
                None,
            )

            aligned_reference_values[generated_pump_id] = aligned_reference_value

        if all(value is None for value in aligned_generated_values.values()):
            notes = f"Missing key {json_key_path.split('.')[-1]}"
            add_test_result(
                specification_test,
                None,
                None,
                TestOutcomeOptions.NOT_IMPLEMENTED.value,
            )
            warnings.append(notes)
            return warnings, errors

        general_comparison_warnings, general_comparison_errors = compare_json_values(
            path_spec,
            aligned_generated_values,
            aligned_reference_values,
            generated_pump_ids,
            specification_test,
            object_id_map,
        )
        errors.extend(general_comparison_errors)

    return warnings, errors


def handle_unordered_comparisons(
    path_spec, reference_json, generated_json, specification_test, object_id_map
):
    json_key_path = path_spec["json-key-path"]
    compare_value = path_spec.get("compare-value", True)

    specification_test["evaluation_criteria"] = (
        EvaluationCriteriaOptions.VALUE.value
        if compare_value
        else EvaluationCriteriaOptions.PRESENT.value
    )

    warnings = []
    errors = []
    # The order will be the same for the generated and reference values, or the order does not matter in the tests
    if ".".join(json_key_path.split(".")[:-1]) == "$":
        generated_value_parents = [generated_json]
    else:
        generated_value_parents = find_all(
            ".".join(json_key_path.split(".")[:-1]), generated_json
        )
    generated_value_parent_ids = [
        # Important to use get() here to avoid key errors where objects have no ID such as weather
        value.get("id")
        for value in generated_value_parents
    ]
    generated_values = find_all(json_key_path, generated_json)
    generated_values = {index: value for index, value in enumerate(generated_values)}
    reference_values = find_all(json_key_path, reference_json)
    reference_values = {index: value for index, value in enumerate(reference_values)}

    if all(value is None for value in generated_values):
        notes = f"Missing key {json_key_path.split('.')[-1]}"
        add_test_result(
            specification_test,
            None,
            None,
            TestOutcomeOptions.NOT_IMPLEMENTED.value,
        )
        warnings.append(notes)
        return warnings, errors

    general_comparison_warnings, general_comparison_errors = compare_json_values(
        path_spec,
        generated_values,
        reference_values,
        generated_value_parent_ids,
        specification_test,
        object_id_map,
    )
    warnings.extend(general_comparison_warnings)
    errors.extend(general_comparison_errors)

    return warnings, errors


def run_file_comparison(
    spec_file, generated_json_file, reference_json_file, test_case_report
):
    """Compares generated and reference JSON files according to the spec."""
    spec = load_json_file(spec_file)
    json_test_key_paths = spec.get("json-test-key-paths", [])

    generated_json = load_json_file(generated_json_file)
    reference_json = load_json_file(reference_json_file)

    warnings = []
    errors = []

    object_id_map, map_warnings, map_errors = map_objects(
        generated_json, reference_json
    )
    warnings.extend(map_warnings)
    errors.extend(map_errors)
    if not object_id_map:
        return warnings, errors

    # Once maps have been defined, iterate through the test specs
    for path_spec in json_test_key_paths:
        json_key_path = path_spec["json-key-path"]
        special_case = path_spec.get("special-case")

        # Add specification test to the report
        specification_test = add_specification_test(test_case_report, json_key_path)

        # Handle any cases that require special logic
        if special_case:
            special_case_warnings, special_case_errors = handle_special_cases(
                path_spec,
                object_id_map,
                generated_json,
                reference_json,
                specification_test,
            )
            warnings.extend(special_case_warnings)
            errors.extend(special_case_errors)

        # Begin the General Comparison Methodology
        else:

            # Handle comparison of data derived from objects which may not be in the same order as the reference objects
            if any(
                group in json_key_path
                for group in [
                    "constructions[",
                    "materials[",
                    "zones[",
                    "surfaces[",
                    "subsurfaces[",
                    "terminals[",
                    "heating_ventilating_air_conditioning_systems[",
                    "boilers[",
                    "chillers[",
                    "heat_rejections[",
                    "fluid_loops[",
                    "pumps[",
                ]
            ):
                (
                    ordered_comparison_warnings,
                    ordered_comparison_errors,
                ) = handle_ordered_comparisons(
                    path_spec,
                    object_id_map,
                    reference_json,
                    generated_json,
                    specification_test,
                )
                warnings.extend(ordered_comparison_warnings)
                errors.extend(ordered_comparison_errors)

            # Handle comparison of data that is not dependent on order
            else:
                (
                    unordered_comparison_warnings,
                    unordered_comparison_errors,
                ) = handle_unordered_comparisons(
                    path_spec,
                    reference_json,
                    generated_json,
                    specification_test,
                    object_id_map,
                )
                warnings.extend(unordered_comparison_warnings)
                errors.extend(unordered_comparison_errors)

    return warnings, errors


def run_comparison_for_all_tests(test_dir: Path):
    """Runs JSON comparison for all test cases in the test directory."""
    reference_dir = test_dir / "Correct Answer RPDs"
    spec_dir = test_dir / "Test Specifications"

    total_errors = 0

    for test_case_dir in test_dir.iterdir():
        test = test_case_dir.name
        # Only recognize directories starting with "E-" or "F-" as test cases
        if test_case_dir.is_dir() and (test.startswith("E-") or test.startswith("F-")):
            # if os.path.isdir(test_dir) and (test == "E-1"):

            generated_json_file = next(
                (f for f in test_case_dir.iterdir() if f.suffix == ".rpd"), None
            )
            spec_file = spec_dir / f"{test} spec.json"
            reference_json_file = reference_dir / f"{test}.rpd"

            if (
                generated_json_file.is_file()
                and spec_file.is_file()
                and generated_json_file.is_file()
                and reference_json_file.is_file()
            ):

                test_case_report = add_test_case_report(
                    test_case_dir, generated_json_file.name
                )
                print(f"Running comparison for {test}...")
                warnings, errors = run_file_comparison(
                    spec_file,
                    generated_json_file,
                    reference_json_file,
                    test_case_report,
                )
                print_results(test, warnings, errors)
                total_errors += len(errors)

            else:
                print(
                    f"Skipping {test} because it does not contain the required files."
                )
                continue

    save_to_json_file()

    if total_errors > 0:
        sys.exit(1)


def print_results(test, warnings, errors):
    """Prints the comparison results."""
    if warnings:
        print(
            f"""----------------------------
    Warnings for {test}:
----------------------------"""
        )
        for warning in warnings:
            print(f"{warning}")
    if errors:
        print(
            f"""----------------------------
    Errors for {test}:
----------------------------"""
        )
        for error in errors:
            print(f"{error}")


def save_to_json_file():
    file_path = "rpd_tests.json"

    print(f"\nSaving results to {file_path}...")
    with open(file_path, "w") as test_output_file:
        json.dump(results_data, test_output_file, indent=4)


if __name__ == "__main__":
    test_directory = Path(__file__).resolve().parent

    CONFIG_DATA = {
        "generation_software_name": "Karpman Consulting RPD Generator",
        "generation_software_version": "1.0.0",
        "modeling_software_name": "eQUEST/DOE2.3",
        "modeling_software_version": "3.65.7175",
        "schema_version": "0.1.4",
        "ruleset_name": "ASHRAE Standard 90.1-2019, Performance Rating Method",
        "ruleset_checking_specification_name": "ASHRAE Standard 90.1-2019, Performance Rating Method",
    }
    results_data.update(CONFIG_DATA)
    run_comparison_for_all_tests(test_directory)
