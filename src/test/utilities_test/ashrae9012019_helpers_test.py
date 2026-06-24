import pytest

from rpd_generator.schema.schema_enums import SchemaEnums
from rpd_generator.utilities.ashrae9012019.baseline_system_type_compare import (
    baseline_system_type_compare,
)
from rpd_generator.utilities.ashrae9012019.baseline_systems.baseline_system_util import (
    HVAC_SYS,
)
from rpd_generator.utilities.ashrae9012019.is_cz_0_to_3a_bool import (
    is_cz_0_to_3a_bool,
)


CLIMATE_ZONES = SchemaEnums.schema_enums["ClimateZoneOptions2019ASHRAE901"]


@pytest.mark.parametrize(
    "climate_zone",
    [
        CLIMATE_ZONES.CZ0A,
        CLIMATE_ZONES.CZ1B,
        CLIMATE_ZONES.CZ3A,
    ],
)
def test_is_cz_0_to_3a_bool_returns_true_for_applicable_zones(climate_zone):
    assert is_cz_0_to_3a_bool(climate_zone) is True


@pytest.mark.parametrize("climate_zone", [CLIMATE_ZONES.CZ3B, CLIMATE_ZONES.CZ4A])
def test_is_cz_0_to_3a_bool_returns_false_for_other_zones(climate_zone):
    assert is_cz_0_to_3a_bool(climate_zone) is False


def test_baseline_system_type_compare_requires_exact_match_by_default():
    assert baseline_system_type_compare(HVAC_SYS.SYS_8, HVAC_SYS.SYS_8) is True
    assert baseline_system_type_compare(HVAC_SYS.SYS_8A, HVAC_SYS.SYS_8) is False


def test_baseline_system_type_compare_accepts_family_match_when_requested():
    assert (
        baseline_system_type_compare(HVAC_SYS.SYS_8A, HVAC_SYS.SYS_8, exact_match=False)
        is True
    )


def test_baseline_system_type_compare_rejects_unknown_system_types():
    with pytest.raises(AssertionError, match="does not match any baseline"):
        baseline_system_type_compare("Sys-404", HVAC_SYS.SYS_8)

    with pytest.raises(AssertionError, match="does not match any primary baseline"):
        baseline_system_type_compare(HVAC_SYS.SYS_8, HVAC_SYS.SYS_8A)
