from rpd_generator.utilities.ashrae9012019.baseline_systems.baseline_hvac_sub_functions.are_all_terminal_cool_sources_none_or_null import (
    are_all_terminal_cool_sources_none_or_null,
)
from rpd_generator.utilities.ashrae9012019.baseline_systems.baseline_hvac_sub_functions.are_all_terminal_fans_null import (
    are_all_terminal_fans_null,
)
from rpd_generator.utilities.ashrae9012019.baseline_systems.baseline_hvac_sub_functions.are_all_terminal_heat_sources_none_or_null import (
    are_all_terminal_heat_sources_none_or_null,
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
from rpd_generator.utilities.ashrae9012019.baseline_systems.baseline_hvac_sub_functions.is_hvac_sys_cooling_type_fluid_loop import (
    is_hvac_sys_cooling_type_fluid_loop,
)
from rpd_generator.utilities.ashrae9012019.baseline_systems.baseline_hvac_sub_functions.is_hvac_sys_fan_sys_cv import (
    is_hvac_sys_fan_sys_cv,
)
from rpd_generator.utilities.ashrae9012019.baseline_systems.baseline_hvac_sub_functions.is_hvac_sys_fluid_loop_attached_to_chiller import (
    is_hvac_sys_fluid_loop_attached_to_chiller,
)
from rpd_generator.utilities.ashrae9012019.baseline_systems.baseline_hvac_sub_functions.is_hvac_sys_fluid_loop_purchased_chw import (
    is_hvac_sys_fluid_loop_purchased_chw,
)
from rpd_generator.utilities.ashrae9012019.baseline_systems.baseline_hvac_sub_functions.is_hvac_sys_heating_type_elec_resistance import (
    is_hvac_sys_heating_type_elec_resistance,
)
from rpd_generator.utilities.ashrae9012019.baseline_systems.baseline_system_util import (
    HVAC_SYS,
)
from rpd_generator.schema.schema_enums import SchemaEnums
from rpd_generator.utilities.ashrae9012019.baseline_systems.baseline_hvac_sub_functions.does_hvac_sys_have_component import (
    has_preheat_system,
)

HEATING_SYSTEM = SchemaEnums.schema_enums["HeatingSystemOptions"]


def is_baseline_system_13(
    hvac,
    terminals_list,
    zones_list,
    chiller_loop_id_list,
    purchased_cooling_loop_id_list,
):
    """
    Get either Sys-13, Sys-13a, or Not_Sys_13 string output which indicates whether the HVAC system is ASHRAE 90.1 2019 Appendix G system 13
    (Single Zone Constant Volume System with CHW and Electric Resistance) or system 13a (system 13 with purchased CHW).

    Parameters
    ----------
    hvac: dict
    The HVAC system to evaluate.
    terminals_list: list
    List of terminals associated with the HVAC system to be evaluated. These are sent to this function from the mater get_baseline_system_types function.
    zones_list: list
    list of zones associated with the HVAC system to be evaluated. These are sent to this function from the mater get_baseline_system_types function.
    chiller_loop_id_list: List<string>
    list of chiller loop ids in the model.
    purchased_cooling_loop_id_list: List<string>
    list of purchased cooling loop ids in the model.

    Returns
    -------
    The function returns either Sys-13, Sys-13a, or Not_Sys_13 string output which indicates whether the HVAC system is ASHRAE 90.1 2019 Appendix G system 13 (Single Zone Constant Volume System with CHW and Electric Resistance) or system 13a (system 13 with purchased CHW).
    """

    baseline_system_type = HVAC_SYS.UNMATCHED

    # check if the hvac system has the required sub systems for system type 13
    # if preheat system DOESN'T exist, has_required_sys=True, else, False
    has_required_sys = not has_preheat_system(hvac)

    are_sys_data_matched = (
        # short-circuit the logic if no required data is found.
        has_required_sys
        # sub functions handles missing required sys, and return False.
        and is_hvac_sys_heating_type_elec_resistance(hvac)
        and is_hvac_sys_cooling_type_fluid_loop(hvac)
        and is_hvac_sys_fan_sys_cv(hvac)
        and does_hvac_sys_serve_single_zone(zones_list)
        and does_each_zone_have_only_one_terminal(zones_list)
        and are_all_terminal_heat_sources_none_or_null(terminals_list)
        and are_all_terminal_cool_sources_none_or_null(terminals_list)
        and are_all_terminal_fans_null(terminals_list)
        and are_all_terminal_types_cav(terminals_list)
    )

    if are_sys_data_matched:
        if is_hvac_sys_fluid_loop_attached_to_chiller(hvac, chiller_loop_id_list):
            baseline_system_type = HVAC_SYS.SYS_13
        elif is_hvac_sys_fluid_loop_purchased_chw(hvac, purchased_cooling_loop_id_list):
            baseline_system_type = HVAC_SYS.SYS_13A

    return baseline_system_type


def diagnose_baseline_system_13(
    hvac,
    terminals_list,
    zones_list,
    chiller_loop_id_list,
    purchased_cooling_loop_id_list,
):
    """
    Diagnostic wrapper for is_baseline_system_13
    (Single-Zone CV with CHW and Electric Resistance Heating).

    Mirrors logic exactly and exposes all failure points and branch decisions.
    """

    diagnostics = {}

    # Required system existence
    diagnostics["has_no_preheat_system"] = not has_preheat_system(hvac)

    # Core eligibility checks
    diagnostics["heating_type_elec_resistance"] = (
        is_hvac_sys_heating_type_elec_resistance(hvac)
    )
    diagnostics["cooling_type_fluid_loop"] = is_hvac_sys_cooling_type_fluid_loop(hvac)
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
    diagnostics["terminal_types_cav"] = are_all_terminal_types_cav(terminals_list)

    passed_core = all(diagnostics.values())

    # Branch diagnostics
    branch = {}

    branch["cooling_loop_attached_to_chiller"] = (
        is_hvac_sys_fluid_loop_attached_to_chiller(hvac, chiller_loop_id_list)
    )
    branch["cooling_loop_purchased_chw"] = is_hvac_sys_fluid_loop_purchased_chw(
        hvac, purchased_cooling_loop_id_list
    )

    matched_system = HVAC_SYS.UNMATCHED

    if passed_core:
        if branch["cooling_loop_attached_to_chiller"]:
            matched_system = HVAC_SYS.SYS_13
        elif branch["cooling_loop_purchased_chw"]:
            matched_system = HVAC_SYS.SYS_13A

    passed = matched_system != HVAC_SYS.UNMATCHED

    failed_checks = [k for k, ok in diagnostics.items() if not ok]

    return {
        "expected_system": "SYS_13",
        "matched_system": matched_system,
        "passed": passed,
        "failed_checks": failed_checks,
        "diagnostics": diagnostics,
        "branch_info": branch,
    }
