import pytest

from rpd_generator.config import Config
from rpd_generator.schema import schema_utils
from rpd_generator.schema.schema_utils import (
    clean_schema_units,
    find_schema_unit_for_json_path,
    get_q,
    quantify_only_needed_rmds,
    quantify_rmd,
    return_json_schema_reference,
)


ureg = Config.ureg


@pytest.fixture(autouse=True)
def clear_schema_utils_caches():
    schema_utils._CLEAN_UNIT_CACHE.clear()
    yield
    schema_utils._CLEAN_UNIT_CACHE.clear()


@pytest.mark.parametrize(
    ("schema_units", "expected"),
    [
        ("ft", "ft"),
        ("Btu/h-ft2-F", "Btu/(h*ft2*F)"),
        ("W/m2-K", "W/(m2*K)"),
    ],
)
def test_clean_schema_units_converts_hyphenated_denominators(schema_units, expected):
    assert clean_schema_units(schema_units) == expected
    assert schema_utils._CLEAN_UNIT_CACHE[schema_units] == expected


def test_return_json_schema_reference_handles_array_item_ref():
    obj = {
        "properties": {
            "zones": {
                "type": "array",
                "items": {"$ref": "ASHRAE229.schema.json#/definitions/Zone"},
            }
        }
    }

    assert return_json_schema_reference(obj, "zones") == "Zone"


def test_return_json_schema_reference_handles_array_item_one_of_ref():
    obj = {
        "properties": {
            "systems": {
                "type": "array",
                "items": {
                    "oneOf": [
                        {
                            "$ref": "ASHRAE229.schema.json#/definitions/HeatingVentilatingAirConditioningSystem"
                        }
                    ]
                },
            }
        }
    }

    assert (
        return_json_schema_reference(obj, "systems")
        == "HeatingVentilatingAirConditioningSystem"
    )


def test_return_json_schema_reference_handles_direct_ref():
    obj = {"properties": {"fan": {"$ref": "ASHRAE229.schema.json#/definitions/Fan"}}}

    assert return_json_schema_reference(obj, "fan") == "Fan"


def test_return_json_schema_reference_preserves_supported_secondary_schema_ref():
    ref = "Output2019ASHRAE901.schema.json#/definitions/RuleOutcome"
    obj = {"properties": {"outcome": {"oneOf": [{"$ref": ref}]}}}

    assert return_json_schema_reference(obj, "outcome") == ref


def test_return_json_schema_reference_rejects_unknown_secondary_schema():
    obj = {
        "properties": {
            "outcome": {
                "oneOf": [{"$ref": "Unknown.schema.json#/definitions/RuleOutcome"}]
            }
        }
    }

    with pytest.raises(ValueError, match="Secondary schema 'Unknown.schema.json'"):
        return_json_schema_reference(obj, "outcome")


def test_return_json_schema_reference_rejects_properties_without_reference():
    obj = {"properties": {"name": {"type": "string"}}}

    with pytest.raises(ValueError, match="No \\$ref found"):
        return_json_schema_reference(obj, "name")


def test_find_schema_unit_for_json_path_reads_primary_schema_units():
    assert (
        find_schema_unit_for_json_path(
            [
                "ruleset_model_descriptions",
                "buildings",
                "building_segments",
                "zones",
                "spaces",
                "floor_area",
            ]
        )
        == "m2"
    )


def test_get_q_returns_quantities_or_default_units():
    default = 0 * ureg("ft2")
    quantity = 3 * ureg("m2")

    assert get_q({}, "floor_area", default) == default
    assert get_q({"floor_area": quantity}, "floor_area", default) == quantity
    assert get_q({"floor_area": 10}, "floor_area", default) == 10 * ureg("ft2")
    assert get_q({"floor_area": "large"}, "floor_area", default) == default


def test_deprecated_quantify_helpers_are_no_ops():
    rpd = {"ruleset_model_descriptions": []}
    rmd = {"id": "RMD-1"}

    assert quantify_only_needed_rmds(rpd, {"Space"}) is rpd
    assert quantify_rmd(rmd) is rmd
