import pytest

from rpd_generator.config import Config
from rpd_generator.utilities.pint_utils import (
    CalcQ,
    UNIT_SYSTEM,
    calcq_to_q,
    calcq_to_str,
)
from rpd_generator.utilities.unit_converter import try_convert_units

ureg = Config.ureg


def test_calcq_to_q_recursively_replaces_calcq_without_mutating_original():
    original = {
        "length": CalcQ("length", 2 * ureg("ft")),
        "items": [CalcQ("area", 3 * ureg("ft2")), "unchanged"],
    }

    converted = calcq_to_q(original)

    assert converted["length"] == 2 * ureg("ft")
    assert converted["items"][0] == 3 * ureg("ft2")
    assert original["length"].q_type == "length"


def test_calcq_to_str_recursively_formats_values_for_requested_unit_system():
    original = {
        "length": CalcQ("length", 2 * ureg("ft")),
        "area": CalcQ("area", 1 * ureg("m2")),
        "none": CalcQ("length", None),
    }

    converted = calcq_to_str(UNIT_SYSTEM.IP, original)

    assert converted["length"] == "2 ft"
    assert converted["area"].endswith(" ft2")
    assert converted["none"] is None


def test_try_convert_units_returns_converted_float_for_numeric_values():
    assert try_convert_units(1, "ft", "inch") == pytest.approx(12)


def test_try_convert_units_returns_none_for_incompatible_or_non_numeric_values():
    assert try_convert_units(1, "ft", "Btu") is None
    assert try_convert_units("1", "ft", "inch") is None
