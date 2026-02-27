import json
import os
import re
from pint import Quantity

from rpd_generator.config import Config

# ------------------------------------------------------------------------------
# Global caches (SAFE)
# ------------------------------------------------------------------------------
_SCHEMA_CACHE: dict[str, dict] = {}
_CLEAN_UNIT_CACHE: dict[str, str] = {}


# ------------------------------------------------------------------------------
# Schema helpers
# ------------------------------------------------------------------------------


def get_schema_definitions_dictionary():
    """Cached load of ASHRAE229 schema definitions."""
    cache_key = "ASHRAE229.schema.json"

    if cache_key in _SCHEMA_CACHE:
        return _SCHEMA_CACHE[cache_key]

    file_dir = os.path.dirname(__file__)
    json_schema_path = os.path.join(file_dir, cache_key)

    with open(json_schema_path) as f:
        schema_dictionary = json.load(f)["definitions"]

    _SCHEMA_CACHE[cache_key] = schema_dictionary
    return schema_dictionary


def get_secondary_schema_root_dictionary(secondary_json_string):
    """Cached load of secondary schema definitions."""
    if secondary_json_string in _SCHEMA_CACHE:
        return _SCHEMA_CACHE[secondary_json_string]

    file_dir = os.path.dirname(__file__)
    json_schema_path = os.path.join(file_dir, secondary_json_string)

    with open(json_schema_path) as f:
        schema_dictionary = json.load(f)["definitions"]

    _SCHEMA_CACHE[secondary_json_string] = schema_dictionary
    return schema_dictionary


def clean_schema_units(schema_unit_str: str) -> str:
    """Clean schema units into Pint-compatible form (cached)."""
    cached = _CLEAN_UNIT_CACHE.get(schema_unit_str)
    if cached is not None:
        return cached

    cleaned = schema_unit_str
    if "-" in schema_unit_str:
        parts = schema_unit_str.split("/")
        for i, part in enumerate(parts):
            if "-" in part:
                parts[i] = "(" + re.sub("-", "*", part) + ")"
        cleaned = "/".join(parts)

    _CLEAN_UNIT_CACHE[schema_unit_str] = cleaned
    return cleaned


def return_json_schema_reference(object_dict, key):
    secondary_schema_files = ["Output2019ASHRAE901.schema.json"]
    properties_dict = object_dict["properties"][key]

    if "items" in properties_dict:
        if "$ref" in properties_dict["items"]:
            return properties_dict["items"]["$ref"].split("/")[-1]
        return properties_dict["items"]["oneOf"][0]["$ref"].split("/")[-1]

    if "$ref" in properties_dict:
        return properties_dict["$ref"].split("/")[-1]

    if "oneOf" in properties_dict:
        ref = properties_dict["oneOf"][0]["$ref"]
        secondary_json = ref.split("#")[0]

        if secondary_json in secondary_schema_files:
            return ref
        if secondary_json == "ASHRAE229.schema.json":
            return ref.split("/")[-1]

        raise ValueError(f"Secondary schema '{secondary_json}' not found")

    raise ValueError(f"No $ref found for {properties_dict}")


def find_schema_unit_for_json_path(key_list):
    """Resolve units from schema for a JSON path."""
    root_key = "RulesetProjectDescription"
    secondary_schema_files = [Config.ACTIVE_RULESET_DICT.get("output_filename")]

    schema_dict = get_schema_definitions_dictionary()
    dict_ref = schema_dict[root_key]

    key_list_head = key_list[:-1]
    last_key = key_list[-1]

    for key in key_list_head:
        reference_string = return_json_schema_reference(dict_ref, key)

        if reference_string.split("#")[0] in secondary_schema_files:
            schema_dict = get_secondary_schema_root_dictionary(
                reference_string.split("#")[0]
            )
            root_key = reference_string.split("/")[-1].split(".")[0]
            dict_ref = schema_dict[root_key]
        else:
            dict_ref = schema_dict[reference_string]

    props = dict_ref.get("properties", {})
    if last_key in props and "units" in props[last_key]:
        return props[last_key]["units"]

    return None


# ------------------------------------------------------------------------------
# Quantification helpers
# ------------------------------------------------------------------------------


def get_q(obj: dict, key: str, default: Quantity) -> Quantity:
    """
    Get a value from a dictionary and return it as a Pint Quantity.
    If the value is already a Quantity, it's returned as is.
    If it's a number, the unit from 'default' is applied.
    """
    val = obj.get(key)
    if val is None:
        return default
    if isinstance(val, Quantity):
        return val
    if isinstance(val, (int, float)):
        return val * default.units
    return default


def quantify_only_needed_rmds(rpd: dict, needed_types: set[str]) -> dict:
    """
    Deprecated: No longer needed with on-the-fly quantification.
    Returns the original dictionary.
    """
    return rpd


def quantify_rmd(rmd):
    """
    Deprecated: No longer needed with on-the-fly quantification.
    Returns the original dictionary.
    """
    return rmd
