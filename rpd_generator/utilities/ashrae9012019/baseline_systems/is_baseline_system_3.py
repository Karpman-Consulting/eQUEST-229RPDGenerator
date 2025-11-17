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
from rpd_generator.utilities.ashrae9012019.baseline_systems.baseline_hvac_sub_functions.is_hvac_sys_cooling_type_fluid_loop import (
    is_hvac_sys_cooling_type_fluid_loop,
)
from rpd_generator.utilities.ashrae9012019.baseline_systems.baseline_hvac_sub_functions.is_hvac_sys_fan_sys_cv import (
    is_hvac_sys_fan_sys_cv,
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
from rpd_generator.utilities.ashrae9012019.baseline_systems.baseline_hvac_sub_functions.is_hvac_sys_heating_type_furnace import (
    is_hvac_sys_heating_type_furnace,
)
from rpd_generator.utilities.ashrae9012019.baseline_systems.baseline_system_util import (
    HVAC_SYS,
)
from rpd_generator.schema.schema_enums import SchemaEnums
from rpd_generator.utilities.ashrae9012019.baseline_systems.baseline_hvac_sub_functions.does_hvac_sys_have_component import (
    has_preheat_system,
)

HEATING_SYSTEM = SchemaEnums.schema_enums["HeatingSystemOptions"]


def is_baseline_system_3(
    hvac,
    terminals_list,
    zones_list,
    purchased_cooling_loop_id_list,
    purchased_heating_loop_id_list,
):
    """
    Get either Sys-3, Sys-3a, Sys-3b, Sys-3c, or Not_Sys_3 string output which indicates whether the HVAC system is ASHRAE 90.1 2019 Appendix G system 3 (PSZ), system 3a (system 3 with purchased CHW),
    system 3b (system 3 with purchased heating), system 3c (system 3 with purchased CHW and purchased HW).

    Parameters
    ----------
    hvac: dict
    The HVAC system to evaluate.
    terminals_list: list
    list of terminals associated with the HVAC system to be evaluated. These are sent to this function from the master get_baseline_system_types function.
    zones_list: list
    list of zones associated with the HVAC system to be evaluated. These are sent to this function from the master get_baseline_system_types function.
    purchased_cooling_loop_id_list: list
    list of purchased cooling loop ids associated with the HVAC system to be evaluated. These are sent to this function from the master get_baseline_system_types function.
    purchased_heating_loop_id_list: list
    list of purchased heating loop ids associated with the HVAC system to be evaluated. These are sent to this function from the master get_baseline_system_types function.

    Returns
    -------
    The function returns either Sys-3, Sys-3a, Sys-3b, Sys-3c, or Not_Sys_3 string output which indicates whether the HVAC system is ASHRAE 90.1 2019 Appendix G system 3 (PSZ),
    system 3a (system 3 with purchased CHW), system 3b (system 3 with purchased heating), system 3c (system 3 with purchased CHW and purchased HW).
    """
    baseline_system_type = HVAC_SYS.UNMATCHED

    # check if the hvac system has the required sub systems for system type 3
    # if preheat DOESN'T exist, has_required_sys=True, else, False
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
        and are_all_terminal_supplies_ducted(terminals_list)
    )

    if are_sys_data_matched:
        if is_hvac_sys_cooling_type_dx(hvac):
            if is_hvac_sys_heating_type_furnace(hvac):
                baseline_system_type = HVAC_SYS.SYS_3
            elif is_hvac_sys_heating_type_fluid_loop(
                hvac
            ) and is_hvac_sys_fluid_loop_purchased_heating(
                hvac, purchased_heating_loop_id_list
            ):
                baseline_system_type = HVAC_SYS.SYS_3B
        elif is_hvac_sys_cooling_type_fluid_loop(
            hvac
        ) and is_hvac_sys_fluid_loop_purchased_chw(
            hvac, purchased_cooling_loop_id_list
        ):
            if is_hvac_sys_heating_type_furnace(hvac):
                baseline_system_type = HVAC_SYS.SYS_3A
            elif is_hvac_sys_fluid_loop_purchased_heating(
                hvac, purchased_heating_loop_id_list
            ):
                baseline_system_type = HVAC_SYS.SYS_3C

    return baseline_system_type
