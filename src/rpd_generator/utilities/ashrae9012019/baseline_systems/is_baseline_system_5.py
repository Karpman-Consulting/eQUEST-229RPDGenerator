from rpd_generator.utilities.ashrae9012019.baseline_systems.baseline_hvac_sub_functions.are_all_terminal_cool_sources_none_or_null import (
    are_all_terminal_cool_sources_none_or_null,
)
from rpd_generator.utilities.ashrae9012019.baseline_systems.baseline_hvac_sub_functions.are_all_terminal_fans_null import (
    are_all_terminal_fans_null,
)
from rpd_generator.utilities.ashrae9012019.baseline_systems.baseline_hvac_sub_functions.are_all_terminal_heat_sources_hot_water import (
    are_all_terminal_heat_sources_hot_water,
)
from rpd_generator.utilities.ashrae9012019.baseline_systems.baseline_hvac_sub_functions.are_all_terminal_heating_loops_attached_to_boiler import (
    are_all_terminal_heating_loops_attached_to_boiler,
)
from rpd_generator.utilities.ashrae9012019.baseline_systems.baseline_hvac_sub_functions.are_all_terminal_heating_loops_purchased_heating import (
    are_all_terminal_heating_loops_purchased_heating,
)
from rpd_generator.utilities.ashrae9012019.baseline_systems.baseline_hvac_sub_functions.are_all_terminal_types_vav import (
    are_all_terminal_types_vav,
)
from rpd_generator.utilities.ashrae9012019.baseline_systems.baseline_hvac_sub_functions.does_each_zone_have_only_one_terminal import (
    does_each_zone_have_only_one_terminal,
)
from rpd_generator.utilities.ashrae9012019.baseline_systems.baseline_hvac_sub_functions.is_hvac_sys_cooling_type_dx import (
    is_hvac_sys_cooling_type_dx,
)
from rpd_generator.utilities.ashrae9012019.baseline_systems.baseline_hvac_sub_functions.is_hvac_sys_fan_sys_vsd import (
    is_hvac_sys_fan_sys_vsd,
)
from rpd_generator.utilities.ashrae9012019.baseline_systems.baseline_hvac_sub_functions.is_hvac_sys_preheat_fluid_loop_attached_to_boiler import (
    is_hvac_sys_preheat_fluid_loop_attached_to_boiler,
)
from rpd_generator.utilities.ashrae9012019.baseline_systems.baseline_hvac_sub_functions.is_hvac_sys_preheat_fluid_loop_purchased_heating import (
    is_hvac_sys_preheat_fluid_loop_purchased_heating,
)
from rpd_generator.utilities.ashrae9012019.baseline_systems.baseline_hvac_sub_functions.is_hvac_sys_preheating_type_fluid_loop import (
    is_hvac_sys_preheating_type_fluid_loop,
)
from rpd_generator.utilities.ashrae9012019.baseline_systems.baseline_system_util import (
    HVAC_SYS,
)
from rpd_generator.schema.schema_enums import SchemaEnums
from rpd_generator.utilities.ashrae9012019.baseline_systems.baseline_hvac_sub_functions.does_hvac_sys_have_component import (
    has_cooling_system,
    has_heating_system,
    has_preheat_system,
)

HEATING_SYSTEM = SchemaEnums.schema_enums["HeatingSystemOptions"]
COOLING_SYSTEM = SchemaEnums.schema_enums["CoolingSystemOptions"]


def is_baseline_system_5(
    hvac,
    terminals_list,
    zones_list,
    boiler_loop_id_list,
    purchased_heating_loop_id_list,
):
    """
    Get either Sys-5, Sys-5b, or Not_Sys_5 string output which indicates whether the HVAC system is ASHRAE 90.1 2019 Appendix G system 5 (Package VAV with Reheat) or system 5b (system 5 with purchased heating).

    Parameters
    ----------
    hvac: dict
    The HVAC system to evaluate.
    terminals_list: list
    list of terminals associated with the HVAC system to be evaluated. These are sent to this function from the master get_baseline_system_types function.
    zones_list: list
    list of zones associated with the HVAC system to be evaluated. These are sent to this function from the master get_baseline_system_types function.
    boiler_loop_id_list: list
    list of boiler loop IDs in the model.
    purchased_heating_loop_id_list: list
    list of purchased heating loop IDs in the model.

    Returns
    -------
    The function returns either Sys-5, Sys-5b, or Not_Sys_5 string output which indicates whether the HVAC system is ASHRAE 90.1 2019 Appendix G system 5 (Package VAV with Reheat) or system 5b (system 5 with purchased heating).
    """

    baseline_system_type = HVAC_SYS.UNMATCHED

    # check if the hvac system has the required sub systems for system type 5
    # if heating system DOESN'T exist and preheat/cooling systems exist,  has_required_sys=True, else, False
    has_required_sys = (
        has_preheat_system(hvac)
        and not has_heating_system(hvac)
        and has_cooling_system(hvac)
    )

    are_sys_data_matched = (
        # short-circuit the logic if no required data is found.
        has_required_sys
        # sub functions handles missing required sys, and return False.
        and is_hvac_sys_preheating_type_fluid_loop(hvac)
        and is_hvac_sys_cooling_type_dx(hvac)
        and is_hvac_sys_fan_sys_vsd(hvac)
        and does_each_zone_have_only_one_terminal(zones_list)
        and are_all_terminal_heat_sources_hot_water(terminals_list)
        and are_all_terminal_cool_sources_none_or_null(terminals_list)
        and are_all_terminal_fans_null(terminals_list)
        and are_all_terminal_types_vav(terminals_list)
    )
    if are_sys_data_matched:
        if is_hvac_sys_preheat_fluid_loop_attached_to_boiler(
            hvac, boiler_loop_id_list
        ) and are_all_terminal_heating_loops_attached_to_boiler(
            terminals_list, boiler_loop_id_list
        ):
            baseline_system_type = HVAC_SYS.SYS_5
        elif is_hvac_sys_preheat_fluid_loop_purchased_heating(
            hvac, purchased_heating_loop_id_list
        ) and are_all_terminal_heating_loops_purchased_heating(
            terminals_list, purchased_heating_loop_id_list
        ):
            baseline_system_type = HVAC_SYS.SYS_5B

    return baseline_system_type


def diagnose_baseline_system_5(
    hvac,
    terminals_list,
    zones_list,
    boiler_loop_id_list,
    purchased_heating_loop_id_list,
):
    """
    Diagnostic wrapper for is_baseline_system_5 (Packaged VAV w/ Reheat).
    Mirrors logic exactly and exposes all failure points and branch decisions.
    """

    diagnostics = {}

    # Required system existence
    diagnostics["has_preheat_system"] = has_preheat_system(hvac)
    diagnostics["has_no_heating_system"] = not has_heating_system(hvac)
    diagnostics["has_cooling_system"] = has_cooling_system(hvac)

    has_required_sys = (
        diagnostics["has_preheat_system"]
        and diagnostics["has_no_heating_system"]
        and diagnostics["has_cooling_system"]
    )

    diagnostics["has_required_sys"] = has_required_sys

    # Core eligibility checks
    diagnostics["preheat_type_fluid_loop"] = is_hvac_sys_preheating_type_fluid_loop(
        hvac
    )
    diagnostics["cooling_type_dx"] = is_hvac_sys_cooling_type_dx(hvac)
    diagnostics["fan_system_vsd"] = is_hvac_sys_fan_sys_vsd(hvac)
    diagnostics["one_terminal_per_zone"] = does_each_zone_have_only_one_terminal(
        zones_list
    )
    diagnostics["terminal_heat_sources_hot_water"] = (
        are_all_terminal_heat_sources_hot_water(terminals_list)
    )
    diagnostics["no_terminal_cool_sources"] = (
        are_all_terminal_cool_sources_none_or_null(terminals_list)
    )
    diagnostics["no_terminal_fans"] = are_all_terminal_fans_null(terminals_list)
    diagnostics["terminal_types_vav"] = are_all_terminal_types_vav(terminals_list)

    passed_core = all(
        diagnostics[k]
        for k in [
            "has_required_sys",
            "preheat_type_fluid_loop",
            "cooling_type_dx",
            "fan_system_vsd",
            "one_terminal_per_zone",
            "terminal_heat_sources_hot_water",
            "no_terminal_cool_sources",
            "no_terminal_fans",
            "terminal_types_vav",
        ]
    )

    # Branch diagnostics
    branch = {}

    branch["preheat_loop_attached_to_boiler"] = (
        is_hvac_sys_preheat_fluid_loop_attached_to_boiler(hvac, boiler_loop_id_list)
    )
    branch["terminal_loops_attached_to_boiler"] = (
        are_all_terminal_heating_loops_attached_to_boiler(
            terminals_list, boiler_loop_id_list
        )
    )

    branch["preheat_loop_purchased_heating"] = (
        is_hvac_sys_preheat_fluid_loop_purchased_heating(
            hvac, purchased_heating_loop_id_list
        )
    )
    branch["terminal_loops_purchased_heating"] = (
        are_all_terminal_heating_loops_purchased_heating(
            terminals_list, purchased_heating_loop_id_list
        )
    )

    matched_system = HVAC_SYS.UNMATCHED

    if passed_core:
        if (
            branch["preheat_loop_attached_to_boiler"]
            and branch["terminal_loops_attached_to_boiler"]
        ):
            matched_system = HVAC_SYS.SYS_5
        elif (
            branch["preheat_loop_purchased_heating"]
            and branch["terminal_loops_purchased_heating"]
        ):
            matched_system = HVAC_SYS.SYS_5B

    passed = matched_system != HVAC_SYS.UNMATCHED

    failed_checks = [k for k, ok in diagnostics.items() if not ok]

    return {
        "expected_system": "SYS_5",
        "matched_system": matched_system,
        "passed": passed,
        "failed_checks": failed_checks,
        "diagnostics": diagnostics,
        "branch_info": branch,
    }
