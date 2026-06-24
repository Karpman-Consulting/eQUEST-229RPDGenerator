from rpd_generator.utilities.ashrae9012019.baseline_systems.baseline_hvac_sub_functions.are_all_terminal_cool_sources_none_or_null import (
    are_all_terminal_cool_sources_none_or_null,
)
from rpd_generator.utilities.ashrae9012019.baseline_systems.baseline_hvac_sub_functions.are_all_terminal_fans_null import (
    are_all_terminal_fans_null,
)
from rpd_generator.utilities.ashrae9012019.baseline_systems.baseline_hvac_sub_functions.are_all_terminal_heat_sources_none_or_null import (
    are_all_terminal_heat_sources_none_or_null,
)
from rpd_generator.utilities.ashrae9012019.baseline_systems.baseline_hvac_sub_functions.are_all_terminal_supplies_ducted import (
    are_all_terminal_supplies_ducted,
)
from rpd_generator.utilities.ashrae9012019.baseline_systems.baseline_hvac_sub_functions.are_all_terminal_types_cav import (
    are_all_terminal_types_cav,
)
from rpd_generator.utilities.ashrae9012019.baseline_systems.baseline_hvac_sub_functions.does_each_zone_have_only_one_terminal import (
    does_each_zone_have_only_one_terminal,
)
from rpd_generator.utilities.ashrae9012019.baseline_systems.baseline_hvac_sub_functions.does_hvac_sys_serve_single_zone import (
    does_hvac_sys_serve_single_zone,
)
from rpd_generator.utilities.ashrae9012019.baseline_systems.baseline_hvac_sub_functions.is_hvac_sys_cooling_type_dx import (
    is_hvac_sys_cooling_type_dx,
)
from rpd_generator.utilities.ashrae9012019.baseline_systems.baseline_hvac_sub_functions.is_hvac_sys_fan_sys_cv import (
    is_hvac_sys_fan_sys_cv,
)
from rpd_generator.utilities.ashrae9012019.baseline_systems.baseline_hvac_sub_functions.is_hvac_sys_heating_type_heat_pump import (
    is_hvac_sys_heating_type_heat_pump,
)
from rpd_generator.utilities.ashrae9012019.baseline_systems.baseline_system_util import (
    HVAC_SYS,
)
from rpd_generator.schema.schema_enums import SchemaEnums
from rpd_generator.utilities.ashrae9012019.baseline_systems.baseline_hvac_sub_functions.does_hvac_sys_have_component import (
    has_preheat_system,
)

HEATING_SYSTEM = SchemaEnums.schema_enums["HeatingSystemOptions"]


def is_baseline_system_4(hvac, terminals_list, zones_list):
    """
    Get either Sys-4 or Not_Sys_4 string output which indicates whether the HVAC system is ASHRAE 90.1 2019 Appendix G system 4 (PSZ-HP).

    Parameters
    ----------
    hvac: dict
    The HVAC system to evaluate.
    terminals_list: list
    list of terminals associated with the HVAC system to be evaluated. These are sent to this function from the master get_baseline_system_types function.
    zones_list: list
    list of zones associated with the HVAC system to be evaluated. These are sent to this function from the master get_baseline_system_types function.

    Returns
    -------
    The function returns either Sys-4 or Not_Sys_4 string output which indicates whether the HVAC system is ASHRAE 90.1 2019 Appendix G system 4 (PSZ-HP).
    """

    # check if the hvac system has the required sub systems for system type 4
    # if preheat DOESN'T exist, has_required_sys=True, else, False
    has_required_sys = not has_preheat_system(hvac)

    are_sys_data_matched = (
        # short-circuit the logic if no required data is found.
        has_required_sys
        # sub functions handles missing required sys, and return False.
        and is_hvac_sys_heating_type_heat_pump(hvac)
        and is_hvac_sys_cooling_type_dx(hvac)
        and is_hvac_sys_fan_sys_cv(hvac)
        and does_hvac_sys_serve_single_zone(zones_list)
        and does_each_zone_have_only_one_terminal(zones_list)
        and are_all_terminal_heat_sources_none_or_null(terminals_list)
        and are_all_terminal_cool_sources_none_or_null(terminals_list)
        and are_all_terminal_fans_null(terminals_list)
        and are_all_terminal_supplies_ducted(terminals_list)
        and are_all_terminal_types_cav(terminals_list)
    )

    return HVAC_SYS.SYS_4 if are_sys_data_matched else HVAC_SYS.UNMATCHED


def diagnose_baseline_system_4(hvac, terminals_list, zones_list):
    """
    Diagnostic wrapper for is_baseline_system_4 (PSZ-HP).
    Mirrors logic exactly and reports which checks failed.
    """

    diagnostics = {}

    # Required system existence
    diagnostics["has_no_preheat_system"] = not has_preheat_system(hvac)

    # Core system checks (order preserved)
    diagnostics["heating_type_heat_pump"] = is_hvac_sys_heating_type_heat_pump(hvac)
    diagnostics["cooling_type_dx"] = is_hvac_sys_cooling_type_dx(hvac)
    diagnostics["fan_system_cv"] = is_hvac_sys_fan_sys_cv(hvac)
    diagnostics["serves_single_zone"] = does_hvac_sys_serve_single_zone(zones_list)
    diagnostics["one_terminal_per_zone"] = does_each_zone_have_only_one_terminal(
        zones_list
    )
    diagnostics["no_terminal_heat_sources"] = (
        are_all_terminal_heat_sources_none_or_null(terminals_list)
    )
    diagnostics["no_terminal_cool_sources"] = (
        are_all_terminal_cool_sources_none_or_null(terminals_list)
    )
    diagnostics["no_terminal_fans"] = are_all_terminal_fans_null(terminals_list)
    diagnostics["terminal_supplies_ducted"] = are_all_terminal_supplies_ducted(
        terminals_list
    )
    diagnostics["terminal_types_cav"] = are_all_terminal_types_cav(terminals_list)

    passed = all(diagnostics.values())

    matched_system = HVAC_SYS.SYS_4 if passed else HVAC_SYS.UNMATCHED

    failed_checks = [name for name, ok in diagnostics.items() if not ok]

    return {
        "expected_system": "SYS_4",
        "matched_system": matched_system,
        "passed": passed,
        "failed_checks": failed_checks,
        "diagnostics": diagnostics,
    }
