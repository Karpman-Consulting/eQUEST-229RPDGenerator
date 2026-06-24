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
from rpd_generator.utilities.ashrae9012019.baseline_systems.baseline_hvac_sub_functions.is_hvac_sys_fluid_loop_attached_to_boiler import (
    is_hvac_sys_fluid_loop_attached_to_boiler,
)
from rpd_generator.utilities.ashrae9012019.baseline_systems.baseline_hvac_sub_functions.is_hvac_sys_fluid_loop_attached_to_chiller import (
    is_hvac_sys_fluid_loop_attached_to_chiller,
)
from rpd_generator.utilities.ashrae9012019.baseline_systems.baseline_hvac_sub_functions.is_hvac_sys_fluid_loop_purchased_chw import (
    is_hvac_sys_fluid_loop_purchased_chw,
)
from rpd_generator.utilities.ashrae9012019.baseline_systems.baseline_system_util import (
    HVAC_SYS,
)
from rpd_generator.schema.schema_enums import SchemaEnums
from rpd_generator.utilities.ashrae9012019.baseline_systems.baseline_hvac_sub_functions.does_hvac_sys_have_component import (
    has_preheat_system,
)

HEATING_SYSTEM = SchemaEnums.schema_enums["HeatingSystemOptions"]


def is_baseline_system_11_2(
    hvac,
    terminals_list,
    zones_list,
    boiler_loop_id_list,
    chiller_loop_id_list,
    purchased_cooling_loop_id_list,
):
    """
    Get either Sys-11.2, Sys-11.2a or Not_Sys_11.2 string output which indicates whether the HVAC system is ASHRAE
    90.1 2019 Appendix G system 11.2 (Single Zone VAV System with Hot Water Heating (Boiler)) or system 11.2a (system
    11.2 with purchased CHW).

    Parameters
    ----------
    hvac: dict
    The HVAC system to evaluate.
    terminals_list: List<Dict>
    list of terminals associated with the HVAC system to be evaluated. These are sent to this function from the master get_baseline_system_types function.
    zones_list: List<Dict>
    list of zones associated with the HVAC system to be evaluated. These are sent to this function from the master get_baseline_system_types function.
    boiler_loop_id_list: List<string>
    list of boiler loop ids in the model.
    chiller_loop_id_list: List<string>
    list of chiller loop ids in the model.
    purchased_cooling_loop_id_list: List<string>
    list of purchased cooling loop ids in the model.

    Returns
    -------
    string
    The function returns either Sys-11.2, Sys-11.2a or Not_Sys string output which indicates
    whether the HVAC system is ASHRAE 90.1 2019 Appendix G 11.2 (Single Zone VAV System with Hot Water Heating (
    Boiler)) or system 11.2a (system 11.2 with purchased CHW). -------
    """
    baseline_system_type = HVAC_SYS.UNMATCHED

    # check if the hvac system has the required sub systems for system type 11.2
    # if preheat system DOESN'T exist, has_required_sys=True, else, False
    has_required_sys = not has_preheat_system(hvac)

    are_sys_data_matched = (
        has_required_sys
        and is_hvac_sys_cooling_type_fluid_loop(hvac)
        and is_hvac_sys_fan_sys_vsd(hvac)
        and does_hvac_sys_serve_single_zone(zones_list)
        and does_each_zone_have_only_one_terminal(zones_list)
        and are_all_terminal_cool_sources_none_or_null(terminals_list)
        and are_all_terminal_heat_sources_none_or_null(terminals_list)
        and are_all_terminal_fans_null(terminals_list)
        and are_all_terminal_types_vav(terminals_list)
    )

    if are_sys_data_matched and is_hvac_sys_fluid_loop_attached_to_boiler(
        hvac, boiler_loop_id_list
    ):
        if is_hvac_sys_fluid_loop_attached_to_chiller(hvac, chiller_loop_id_list):
            baseline_system_type = HVAC_SYS.SYS_11_2
        elif is_hvac_sys_fluid_loop_purchased_chw(hvac, purchased_cooling_loop_id_list):
            baseline_system_type = HVAC_SYS.SYS_11_2A

    return baseline_system_type


def diagnose_baseline_system_11_2(
    hvac,
    terminals_list,
    zones_list,
    boiler_loop_id_list,
    chiller_loop_id_list,
    purchased_cooling_loop_id_list,
):
    """
    Diagnostic wrapper for is_baseline_system_11_2
    (Single-Zone VAV with Hot Water Heating).

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
    diagnostics["no_terminal_cool_sources"] = (
        are_all_terminal_cool_sources_none_or_null(terminals_list)
    )
    diagnostics["no_terminal_heat_sources"] = (
        are_all_terminal_heat_sources_none_or_null(terminals_list)
    )
    diagnostics["no_terminal_fans"] = are_all_terminal_fans_null(terminals_list)
    diagnostics["terminal_types_vav"] = are_all_terminal_types_vav(terminals_list)

    passed_core = all(diagnostics.values())

    # Branch diagnostics
    branch = {}

    branch["heating_loop_attached_to_boiler"] = (
        is_hvac_sys_fluid_loop_attached_to_boiler(hvac, boiler_loop_id_list)
    )
    branch["cooling_loop_attached_to_chiller"] = (
        is_hvac_sys_fluid_loop_attached_to_chiller(hvac, chiller_loop_id_list)
    )
    branch["cooling_loop_purchased_chw"] = is_hvac_sys_fluid_loop_purchased_chw(
        hvac, purchased_cooling_loop_id_list
    )

    matched_system = HVAC_SYS.UNMATCHED

    if passed_core and branch["heating_loop_attached_to_boiler"]:
        if branch["cooling_loop_attached_to_chiller"]:
            matched_system = HVAC_SYS.SYS_11_2
        elif branch["cooling_loop_purchased_chw"]:
            matched_system = HVAC_SYS.SYS_11_2A

    passed = matched_system != HVAC_SYS.UNMATCHED

    failed_checks = [k for k, ok in diagnostics.items() if not ok]

    return {
        "expected_system": "SYS_11_2",
        "matched_system": matched_system,
        "passed": passed,
        "failed_checks": failed_checks,
        "diagnostics": diagnostics,
        "branch_info": branch,
    }
