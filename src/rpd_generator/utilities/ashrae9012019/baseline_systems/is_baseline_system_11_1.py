from rpd_generator.utilities.ashrae9012019.baseline_systems.baseline_hvac_sub_functions.are_all_terminal_cool_sources_none_or_null import (
    are_all_terminal_cool_sources_none_or_null,
)
from rpd_generator.utilities.ashrae9012019.baseline_systems.baseline_hvac_sub_functions.are_all_terminal_fans_null import (
    are_all_terminal_fans_null,
)
from rpd_generator.utilities.ashrae9012019.baseline_systems.baseline_hvac_sub_functions.are_all_terminal_heat_sources_none_or_null import (
    are_all_terminal_heat_sources_none_or_null,
)
from rpd_generator.utilities.ashrae9012019.baseline_systems.baseline_hvac_sub_functions.are_all_terminal_types_vav import (
    are_all_terminal_types_vav,
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
from rpd_generator.utilities.ashrae9012019.baseline_systems.baseline_hvac_sub_functions.is_hvac_sys_fan_sys_vsd import (
    is_hvac_sys_fan_sys_vsd,
)
from rpd_generator.utilities.ashrae9012019.baseline_systems.baseline_hvac_sub_functions.is_hvac_sys_fluid_loop_attached_to_chiller import (
    is_hvac_sys_fluid_loop_attached_to_chiller,
)
from rpd_generator.utilities.ashrae9012019.baseline_systems.baseline_hvac_sub_functions.is_hvac_sys_fluid_loop_purchased_chw import (
    is_hvac_sys_fluid_loop_purchased_chw,
)
from rpd_generator.utilities.ashrae9012019.baseline_systems.baseline_hvac_sub_functions.is_hvac_sys_fluid_loop_purchased_heating import (
    is_hvac_sys_fluid_loop_purchased_heating,
)
from rpd_generator.utilities.ashrae9012019.baseline_systems.baseline_hvac_sub_functions.is_hvac_sys_heating_type_elec_resistance import (
    is_hvac_sys_heating_type_elec_resistance,
)
from rpd_generator.utilities.ashrae9012019.baseline_systems.baseline_hvac_sub_functions.is_hvac_sys_heating_type_fluid_loop import (
    is_hvac_sys_heating_type_fluid_loop,
)
from rpd_generator.utilities.ashrae9012019.baseline_systems.baseline_system_util import (
    HVAC_SYS,
)
from rpd_generator.schema.schema_enums import SchemaEnums
from rpd_generator.utilities.ashrae9012019.baseline_systems.baseline_hvac_sub_functions.does_hvac_sys_have_component import (
    has_preheat_system,
)

HEATING_SYSTEM = SchemaEnums.schema_enums["HeatingSystemOptions"]


def is_baseline_system_11_1(
    hvac,
    terminals_list,
    zones_list,
    chiller_loop_id_list,
    purchased_cooling_loop_id_list,
    purchased_heating_loop_id_list,
):
    """
    Get either Sys-11.1, Sys-11.1a, Sys-11b, Sys-11c, or Not_Sys_11.1 string output which indicates whether the HVAC
    system is ASHRAE 90.1 2019 Appendix G system 11.1 (Single Zone VAV System with Electric Resistance Heating),
    system 11.1a (system 11.1 with purchased CHW), system 11b (system 11.1 with purchased heating), or system 11c (
    system 11.1 with purchased CHW and purchased heating).

    Parameters
    ----------
    hvac: dict
    The HVAC system to evaluate.
    terminals_list: list
    list of terminals associated with the HVAC system to be evaluated. These are sent to this function from the master get_baseline_system_types function.
    zones_list:
    list of zones associated with the HVAC system to be evaluated. These are sent to this function from the master get_baseline_system_types function.
    chiller_loop_id_list: list
    list of chiller loop ids in the building model. These are sent to this function from the master get_baseline_system_types function.
    purchased_cooling_loop_id_list: list
    list of purchased cooling loop ids in the building model. These are sent to this function from the master get_baseline_system_types function.
    purchased_heating_loop_id_list: list
    list of purchased heating loop ids in the building model. These are sent to this function from the master get_baseline_system_types function.

    Returns
    -------
    The function returns either Sys-11.1, Sys-11.1a, Sys-11b, Sys-11c, or Not_Sys_11.1 string output
    which indicates whether the HVAC system is ASHRAE 90.1 2019 Appendix G system 11.1 (Single Zone VAV System with
    Electric Resistance Heating), system 11.1a (system 11.1 with purchased CHW), system 11b (system 11.1 with
    purchased heating), or system 11c (system 11.1 with purchased CHW and purchased heating).
    """
    baseline_system_type = HVAC_SYS.UNMATCHED

    # check if the hvac system has the required sub systems for system type 11.1
    # if preheat system DOESN'T exist, has_required_sys=True, else, False
    has_required_sys = not has_preheat_system(hvac)

    are_sys_data_matched = (
        # short-circuit the logic if no required data is found.
        has_required_sys
        # sub functions handles missing required sys, and return False.
        and is_hvac_sys_cooling_type_fluid_loop(hvac)
        and is_hvac_sys_fan_sys_vsd(hvac)
        and does_hvac_sys_serve_single_zone(zones_list)
        and does_each_zone_have_only_one_terminal(zones_list)
        and are_all_terminal_cool_sources_none_or_null(terminals_list)
        and are_all_terminal_heat_sources_none_or_null(terminals_list)
        and are_all_terminal_fans_null(terminals_list)
        and are_all_terminal_types_vav(terminals_list)
    )

    if are_sys_data_matched:
        if is_hvac_sys_heating_type_elec_resistance(hvac):
            if is_hvac_sys_fluid_loop_attached_to_chiller(hvac, chiller_loop_id_list):
                baseline_system_type = HVAC_SYS.SYS_11_1
            elif is_hvac_sys_fluid_loop_purchased_chw(
                hvac, purchased_cooling_loop_id_list
            ):
                baseline_system_type = HVAC_SYS.SYS_11_1A
        elif is_hvac_sys_heating_type_fluid_loop(
            hvac
        ) and is_hvac_sys_fluid_loop_purchased_heating(
            hvac, purchased_heating_loop_id_list
        ):
            if is_hvac_sys_fluid_loop_attached_to_chiller(hvac, chiller_loop_id_list):
                baseline_system_type = HVAC_SYS.SYS_11_1B
            elif is_hvac_sys_fluid_loop_purchased_chw(
                hvac, purchased_cooling_loop_id_list
            ):
                baseline_system_type = HVAC_SYS.SYS_11_1C

    return baseline_system_type


def diagnose_baseline_system_11_1(
    hvac,
    terminals_list,
    zones_list,
    chiller_loop_id_list,
    purchased_cooling_loop_id_list,
    purchased_heating_loop_id_list,
):
    """
    Diagnostic wrapper for is_baseline_system_11_1
    (Single-Zone VAV with Electric Resistance Heating).
    Mirrors logic exactly and exposes all failure points and branch decisions.
    """

    diagnostics = {}

    # Required system existence
    diagnostics["has_no_preheat_system"] = not has_preheat_system(hvac)

    # Core eligibility checks
    diagnostics["cooling_type_fluid_loop"] = is_hvac_sys_cooling_type_fluid_loop(hvac)
    diagnostics["fan_system_vsd"] = is_hvac_sys_fan_sys_vsd(hvac)
    diagnostics["serves_single_zone"] = does_hvac_sys_serve_single_zone(zones_list)
    diagnostics["one_terminal_per_zone"] = does_each_zone_have_only_one_terminal(
        zones_list
    )
    diagnostics[
        "no_terminal_cool_sources"
    ] = are_all_terminal_cool_sources_none_or_null(terminals_list)
    diagnostics[
        "no_terminal_heat_sources"
    ] = are_all_terminal_heat_sources_none_or_null(terminals_list)
    diagnostics["no_terminal_fans"] = are_all_terminal_fans_null(terminals_list)
    diagnostics["terminal_types_vav"] = are_all_terminal_types_vav(terminals_list)

    passed_core = all(diagnostics.values())

    # Branch diagnostics
    branch = {}

    branch[
        "heating_type_electric_resistance"
    ] = is_hvac_sys_heating_type_elec_resistance(hvac)
    branch["heating_type_fluid_loop"] = is_hvac_sys_heating_type_fluid_loop(hvac)
    branch["heating_loop_purchased_heating"] = is_hvac_sys_fluid_loop_purchased_heating(
        hvac, purchased_heating_loop_id_list
    )

    branch[
        "cooling_loop_attached_to_chiller"
    ] = is_hvac_sys_fluid_loop_attached_to_chiller(hvac, chiller_loop_id_list)
    branch["cooling_loop_purchased_chw"] = is_hvac_sys_fluid_loop_purchased_chw(
        hvac, purchased_cooling_loop_id_list
    )

    matched_system = HVAC_SYS.UNMATCHED

    if passed_core:
        # Electric resistance heating branch
        if branch["heating_type_electric_resistance"]:
            if branch["cooling_loop_attached_to_chiller"]:
                matched_system = HVAC_SYS.SYS_11_1
            elif branch["cooling_loop_purchased_chw"]:
                matched_system = HVAC_SYS.SYS_11_1A

        # Fluid-loop heating branch
        elif (
            branch["heating_type_fluid_loop"]
            and branch["heating_loop_purchased_heating"]
        ):
            if branch["cooling_loop_attached_to_chiller"]:
                matched_system = HVAC_SYS.SYS_11_1B
            elif branch["cooling_loop_purchased_chw"]:
                matched_system = HVAC_SYS.SYS_11_1C

    passed = matched_system != HVAC_SYS.UNMATCHED

    failed_checks = [k for k, ok in diagnostics.items() if not ok]

    return {
        "expected_system": "SYS_11_1",
        "matched_system": matched_system,
        "passed": passed,
        "failed_checks": failed_checks,
        "diagnostics": diagnostics,
        "branch_info": branch,
    }
