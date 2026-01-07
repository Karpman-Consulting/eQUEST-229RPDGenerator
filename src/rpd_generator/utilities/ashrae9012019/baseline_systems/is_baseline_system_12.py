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
from rpd_generator.utilities.ashrae9012019.baseline_systems.baseline_hvac_sub_functions.is_hvac_sys_fluid_loop_attached_to_boiler import (
    is_hvac_sys_fluid_loop_attached_to_boiler,
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


def is_baseline_system_12(
    hvac,
    terminals_list,
    zones_list,
    chiller_loop_id_list,
    boiler_loop_id_list,
    purchased_cooling_loop_id_list,
    purchased_heating_loop_id_list,
):
    """
    Get either Sys-12, Sys-12a, Sys-12b, Sys-12c, or Not_Sys_12 string output which indicates whether the HVAC system is ASHRAE 90.1 2019 Appendix G system 12 (Single Zone Constant Volume System
    with CHW and HW), system 12a (system 12 with purchased CHW), system 12b (system 12 with purchased heating), system 12c (system 12 with purchased CHW and purchased HW).

    Parameters
    ----------
    hvac: dict
    The HVAC system to evaluate.
    terminals_list: list
    List of terminals associated with the HVAC system to be evaluated. These are sent to this function from the mater get_baseline_system_types function.
    zones_list: list
    List of zones associated with the HVAC system to be evaluated. These are sent to this function from the mater get_baseline_system_types function.
    chiller_loop_id_list: list
    list of chiller loop ids in the model.
    boiler_loop_id_list: list
    list of boiler loop ids in the model.
    purchased_cooling_loop_id_list: list
    list of purchased cooling loop ids in the model.
    purchased_heating_loop_id_list: list
    list of purchased heating loop ids in the model.

    Returns
    -------
    The function returns either Sys-12, Sys-12a, Sys-12b, Sys-12c, or Not_Sys_12 string output which indicates whether the HVAC system is ASHRAE 90.1 2019 Appendix G system 12 (Single Zone Constant Volume System
    with CHW and HW), system 12a (system 12 with purchased CHW), system 12b (system 12 with purchased heating), system 12c (system 12 with purchased CHW and purchased HW).
    """

    baseline_system_type = HVAC_SYS.UNMATCHED

    # check if the hvac system has the required sub systems for system type 12
    # if preheat system DOESN'T exist, has_required_sys=True, else, False
    has_required_sys = not has_preheat_system(hvac)

    are_sys_data_matched = (
        # short-circuit the logic if no required data is found.
        has_required_sys
        # sub functions handles missing required sys, and return False.
        and is_hvac_sys_heating_type_fluid_loop(hvac)
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
            if is_hvac_sys_fluid_loop_attached_to_boiler(hvac, boiler_loop_id_list):
                baseline_system_type = HVAC_SYS.SYS_12
            elif is_hvac_sys_fluid_loop_purchased_heating(
                hvac, purchased_heating_loop_id_list
            ):
                baseline_system_type = HVAC_SYS.SYS_12B
        elif is_hvac_sys_fluid_loop_purchased_chw(
            hvac, purchased_cooling_loop_id_list
        ) and is_hvac_sys_fluid_loop_attached_to_boiler(hvac, boiler_loop_id_list):
            baseline_system_type = HVAC_SYS.SYS_12A

    return baseline_system_type


def diagnose_baseline_system_12(
    hvac,
    terminals_list,
    zones_list,
    chiller_loop_id_list,
    boiler_loop_id_list,
    purchased_cooling_loop_id_list,
    purchased_heating_loop_id_list,
):
    """
    Diagnostic wrapper for is_baseline_system_12
    (Single-Zone Constant Volume with CHW and HW).

    Mirrors logic exactly and exposes all failure points and branch decisions.
    """

    diagnostics = {}

    # Required system existence
    diagnostics["has_no_preheat_system"] = not has_preheat_system(hvac)

    # Core eligibility checks
    diagnostics["heating_type_fluid_loop"] = is_hvac_sys_heating_type_fluid_loop(hvac)
    diagnostics["cooling_type_fluid_loop"] = is_hvac_sys_cooling_type_fluid_loop(hvac)
    diagnostics["fan_system_cv"] = is_hvac_sys_fan_sys_cv(hvac)
    diagnostics["serves_single_zone"] = does_hvac_sys_serve_single_zone(zones_list)
    diagnostics["one_terminal_per_zone"] = does_each_zone_have_only_one_terminal(
        zones_list
    )
    diagnostics[
        "no_terminal_heat_sources"
    ] = are_all_terminal_heat_sources_none_or_null(terminals_list)
    diagnostics[
        "no_terminal_cool_sources"
    ] = are_all_terminal_cool_sources_none_or_null(terminals_list)
    diagnostics["no_terminal_fans"] = are_all_terminal_fans_null(terminals_list)
    diagnostics["terminal_types_cav"] = are_all_terminal_types_cav(terminals_list)

    passed_core = all(diagnostics.values())

    # Branch diagnostics
    branch = {}

    branch[
        "cooling_loop_attached_to_chiller"
    ] = is_hvac_sys_fluid_loop_attached_to_chiller(hvac, chiller_loop_id_list)
    branch["cooling_loop_purchased_chw"] = is_hvac_sys_fluid_loop_purchased_chw(
        hvac, purchased_cooling_loop_id_list
    )

    branch[
        "heating_loop_attached_to_boiler"
    ] = is_hvac_sys_fluid_loop_attached_to_boiler(hvac, boiler_loop_id_list)
    branch["heating_loop_purchased_heating"] = is_hvac_sys_fluid_loop_purchased_heating(
        hvac, purchased_heating_loop_id_list
    )

    matched_system = HVAC_SYS.UNMATCHED

    if passed_core:
        if branch["cooling_loop_attached_to_chiller"]:
            if branch["heating_loop_attached_to_boiler"]:
                matched_system = HVAC_SYS.SYS_12
            elif branch["heating_loop_purchased_heating"]:
                matched_system = HVAC_SYS.SYS_12B
        elif (
            branch["cooling_loop_purchased_chw"]
            and branch["heating_loop_attached_to_boiler"]
        ):
            matched_system = HVAC_SYS.SYS_12A

    passed = matched_system != HVAC_SYS.UNMATCHED

    failed_checks = [k for k, ok in diagnostics.items() if not ok]

    return {
        "expected_system": "SYS_12",
        "matched_system": matched_system,
        "passed": passed,
        "failed_checks": failed_checks,
        "diagnostics": diagnostics,
        "branch_info": branch,
    }
