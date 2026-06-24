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
from rpd_generator.utilities.ashrae9012019.baseline_systems.baseline_hvac_sub_functions.is_hvac_sys_cooling_type_none_or_non_mechanical import (
    is_hvac_sys_cooling_type_none_or_non_mechanical,
)
from rpd_generator.utilities.ashrae9012019.baseline_systems.baseline_hvac_sub_functions.is_hvac_sys_fan_sys_cv import (
    is_hvac_sys_fan_sys_cv,
)
from rpd_generator.utilities.ashrae9012019.baseline_systems.baseline_hvac_sub_functions.is_hvac_sys_heating_type_furnace import (
    is_hvac_sys_heating_type_furnace,
)
from rpd_generator.utilities.ashrae9012019.baseline_systems.baseline_system_util import (
    HVAC_SYS,
)
from rpd_generator.utilities.ashrae9012019.baseline_systems.is_baseline_system_9b import (
    is_baseline_system_9b,
)
from rpd_generator.schema.schema_enums import SchemaEnums
from rpd_generator.utilities.ashrae9012019.baseline_systems.baseline_hvac_sub_functions.does_hvac_sys_have_component import (
    has_preheat_system,
)

HEATING_SYSTEM = SchemaEnums.schema_enums["HeatingSystemOptions"]


def is_baseline_system_9(
    hvac,
    terminals_list,
    zones_list,
    purchased_cooling_loop_id_list,
    purchased_heating_loop_id_list,
):
    """
    Get either Sys-9, Sys-9b, or Not_Sys_9 string output which indicates whether the HVAC system is ASHRAE 90.1 2019 Appendix G system 9 (Heating and Ventilation) or system 9b (system 9 with purchased heating).

    Parameters
    ----------
    hvac: dict
    The id of the hvac system to evaluate.
    terminals_list: list
    list of terminals associated with the HVAC system to be evaluated. These are sent to this function from the master get_baseline_system_types function.
    zones_list: list
    list of zones associated with the HVAC system to be evaluated. These are sent to this function from the master get_baseline_system_types function.
    purchased_cooling_loop_id_list: list
    list of purchased cooling loop ids in the model.
    purchased_heating_loop_id_list: list
    list of purchased heating loop ids in the model.

    Returns
    -------
    The function returns either Sys-9, Sys-9b, or Not_Sys_9 string output which indicates whether the HVAC system is ASHRAE 90.1 2019 Appendix G system 9 (Heating and Ventilation) or system 9b (system 9 with purchased heating).
    """

    baseline_system_type = HVAC_SYS.UNMATCHED

    if is_baseline_system_9b(
        hvac,
        terminals_list,
        zones_list,
        purchased_cooling_loop_id_list,
        purchased_heating_loop_id_list,
    ):
        baseline_system_type = HVAC_SYS.SYS_9B
    else:
        # if preheat system DOESN'T exist, has_required_sys=True, else, False
        has_required_sys = not has_preheat_system(hvac)

        are_sys_data_matched = (
            # short-circuit the logic if no required data is found.
            has_required_sys
            # sub functions handles missing required sys, and return False.
            and is_hvac_sys_fan_sys_cv(hvac)
            and does_hvac_sys_serve_single_zone(zones_list)
            and does_each_zone_have_only_one_terminal(zones_list)
            and are_all_terminal_heat_sources_none_or_null(terminals_list)
            and are_all_terminal_cool_sources_none_or_null(terminals_list)
            and are_all_terminal_fans_null(terminals_list)
            and are_all_terminal_types_cav(terminals_list)
            and is_hvac_sys_cooling_type_none_or_non_mechanical(hvac)
            and is_hvac_sys_heating_type_furnace(hvac)
        )

        if are_sys_data_matched:
            baseline_system_type = HVAC_SYS.SYS_9

    return baseline_system_type


def diagnose_baseline_system_9(
    hvac,
    terminals_list,
    zones_list,
    purchased_cooling_loop_id_list,
    purchased_heating_loop_id_list,
):
    """
    Diagnostic wrapper for is_baseline_system_9 (Heating & Ventilation).
    Mirrors logic exactly and exposes all failure points and branch decisions.
    """

    diagnostics = {}
    branch = {}

    # -------------------------------------------------
    # Sys-9B override check (evaluated first by design)
    # -------------------------------------------------
    branch["passes_sys_9b"] = is_baseline_system_9b(
        hvac,
        terminals_list,
        zones_list,
        purchased_cooling_loop_id_list,
        purchased_heating_loop_id_list,
    )

    if branch["passes_sys_9b"]:
        return {
            "expected_system": "SYS_9",
            "matched_system": HVAC_SYS.SYS_9B,
            "passed": True,
            "failed_checks": [],
            "diagnostics": {},
            "branch_info": branch,
        }

    # -------------------------------------------------
    # Sys-9 base eligibility
    # -------------------------------------------------

    diagnostics["has_no_preheat_system"] = not has_preheat_system(hvac)
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
    diagnostics["cooling_none_or_non_mechanical"] = (
        is_hvac_sys_cooling_type_none_or_non_mechanical(hvac)
    )
    diagnostics["heating_type_furnace"] = is_hvac_sys_heating_type_furnace(hvac)

    passed_core = all(diagnostics.values())

    matched_system = HVAC_SYS.SYS_9 if passed_core else HVAC_SYS.UNMATCHED

    failed_checks = [k for k, ok in diagnostics.items() if not ok]

    return {
        "expected_system": "SYS_9",
        "matched_system": matched_system,
        "passed": matched_system != HVAC_SYS.UNMATCHED,
        "failed_checks": failed_checks,
        "diagnostics": diagnostics,
        "branch_info": branch,
    }
