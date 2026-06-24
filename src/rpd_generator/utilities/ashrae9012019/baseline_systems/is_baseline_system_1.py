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
from rpd_generator.utilities.ashrae9012019.baseline_systems.baseline_hvac_sub_functions.is_hvac_sys_fluid_loop_attached_to_boiler import (
    is_hvac_sys_fluid_loop_attached_to_boiler,
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
from rpd_generator.utilities.ashrae9012019.baseline_systems.is_baseline_system_1_a import (
    is_baseline_system_1_a,
)
from rpd_generator.utilities.ashrae9012019.baseline_systems.is_baseline_system_1_c import (
    is_baseline_system_1_c,
)
from rpd_generator.schema.schema_enums import SchemaEnums
from rpd_generator.utilities.ashrae9012019.baseline_systems.baseline_hvac_sub_functions.does_hvac_sys_have_component import (
    has_preheat_system,
)

HEATING_SYSTEM = SchemaEnums.schema_enums["HeatingSystemOptions"]


def is_baseline_system_1(
    hvac,
    terminals_list,
    zones_list,
    boiler_loop_id_list,
    purchased_cooling_loop_id_list,
    purchased_heating_loop_id_list,
):
    """
    Get either Sys-1, Sys-1a, Sys-1b, Sys-1c, or Not_Sys_1 string output which indicates whether the HVAC system is
    ASHRAE 90.1 2019 Appendix G system 1 (PTAC), system 1a (system 1 with purchased CHW), system 1b (system 1 with
    purchased heating), system 1c (system 1 with purchased CHW and purchased HW).

    Parameters
    ----------
    hvac: dict
    The HVAC system to evaluate.
    terminals_list: List<Dict>
    list of terminals associated with the HVAC system to be evaluated. These are sent to this function from the master get_baseline_system_types function.
    zones_list: List<Dict>
    list of zones associated with the HVAC system to be evaluated. These are sent to this function from the master get_baseline_system_types function.
    boiler_loop_id_list: List[str]
    List of fluid loop ids that are connected to boilers in the building model.
    purchased_cooling_loop_id_list: List[str]
    List of fluid loop ids that are purchased cooling loops in the building model.
    purchased_heating_loop_id_list: List[str]
    List of fluid loop ids that are purchased heating loops in the building model.

    Returns
    -------
    The function returns either Sys-1, Sys-1a, Sys-1b, Sys-1c, or Not_Sys_1 string output which indicates
    whether the HVAC system is ASHRAE 90.1 2019 Appendix G system 1 (PTAC), system 1a (system 1 with purchased CHW),
    system 1b (system 1 with purchased heating), system 1c (system 1 with purchased CHW and purchased HW). -------

    """

    baseline_system_type = HVAC_SYS.UNMATCHED

    if is_baseline_system_1_c(
        hvac,
        terminals_list,
        zones_list,
        purchased_cooling_loop_id_list,
        purchased_heating_loop_id_list,
    ):
        baseline_system_type = HVAC_SYS.SYS_1C
    elif is_baseline_system_1_a(
        hvac,
        terminals_list,
        zones_list,
        boiler_loop_id_list,
        purchased_cooling_loop_id_list,
    ):
        baseline_system_type = HVAC_SYS.SYS_1A
    else:
        # check if the hvac system has the required sub systems for system type 1
        # if preheat system DOESN'T exist, has_required_sys=True, else, False
        has_required_sys = not has_preheat_system(hvac)

        are_sys_data_matched = (
            # short-circuit the logic if no required data is found.
            has_required_sys
            # sub functions handles missing required sys, and return False.
            and is_hvac_sys_heating_type_fluid_loop(hvac)
            and is_hvac_sys_fan_sys_cv(hvac)
            and does_hvac_sys_serve_single_zone(zones_list)
            and does_each_zone_have_only_one_terminal(zones_list)
            and are_all_terminal_heat_sources_none_or_null(terminals_list)
            and are_all_terminal_cool_sources_none_or_null(terminals_list)
            and are_all_terminal_fans_null(terminals_list)
            and are_all_terminal_types_cav(terminals_list)
            and is_hvac_sys_cooling_type_dx(hvac)
        )
        if are_sys_data_matched:
            if is_hvac_sys_fluid_loop_attached_to_boiler(hvac, boiler_loop_id_list):
                baseline_system_type = HVAC_SYS.SYS_1
            elif is_hvac_sys_fluid_loop_purchased_heating(
                hvac, purchased_heating_loop_id_list
            ) and not are_all_terminal_supplies_ducted(terminals_list):
                baseline_system_type = HVAC_SYS.SYS_1B
    return baseline_system_type


def diagnose_baseline_system_1(
    hvac,
    terminals_list,
    zones_list,
    boiler_loop_id_list,
    purchased_cooling_loop_id_list,
    purchased_heating_loop_id_list,
):
    diagnostics = {}

    diagnostics["has_no_preheat_system"] = not has_preheat_system(hvac)
    diagnostics["heating_type_fluid_loop"] = is_hvac_sys_heating_type_fluid_loop(hvac)
    diagnostics["fan_system_cv"] = is_hvac_sys_fan_sys_cv(hvac)
    diagnostics["single_zone"] = does_hvac_sys_serve_single_zone(zones_list)
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
    diagnostics["terminal_type_cav"] = are_all_terminal_types_cav(terminals_list)
    diagnostics["cooling_type_dx"] = is_hvac_sys_cooling_type_dx(hvac)

    boiler_attached = is_hvac_sys_fluid_loop_attached_to_boiler(
        hvac, boiler_loop_id_list
    )

    purchased_heating = is_hvac_sys_fluid_loop_purchased_heating(
        hvac, purchased_heating_loop_id_list
    )

    supplies_ducted = are_all_terminal_supplies_ducted(terminals_list)

    passed_core = all(diagnostics.values())

    if passed_core and boiler_attached:
        system = HVAC_SYS.SYS_1
    elif passed_core and purchased_heating and not supplies_ducted:
        system = HVAC_SYS.SYS_1B
    else:
        system = HVAC_SYS.UNMATCHED

    failed_checks = [k for k, v in diagnostics.items() if not v]

    return {
        "expected_system": "SYS_1",
        "matched_system": system,
        "passed": system != HVAC_SYS.UNMATCHED,
        "failed_checks": failed_checks,
        "diagnostics": diagnostics,
        "branch_info": {
            "boiler_attached": boiler_attached,
            "purchased_heating": purchased_heating,
            "supplies_ducted": supplies_ducted,
        },
    }
