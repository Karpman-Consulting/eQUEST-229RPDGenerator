from rpd_generator.utilities.ashrae9012019.baseline_systems.baseline_hvac_sub_functions.are_all_terminal_cool_sources_none_or_null import (
    are_all_terminal_cool_sources_none_or_null,
)
from rpd_generator.utilities.ashrae9012019.baseline_systems.baseline_hvac_sub_functions.are_all_terminal_fan_configs_parallel import (
    are_all_terminal_fan_configs_parallel,
)
from rpd_generator.utilities.ashrae9012019.baseline_systems.baseline_hvac_sub_functions.are_all_terminal_heat_sources_electric import (
    are_all_terminal_heat_sources_electric,
)
from rpd_generator.utilities.ashrae9012019.baseline_systems.baseline_hvac_sub_functions.are_all_terminal_heat_sources_hot_water import (
    are_all_terminal_heat_sources_hot_water,
)
from rpd_generator.utilities.ashrae9012019.baseline_systems.baseline_hvac_sub_functions.are_all_terminal_heating_loops_purchased_heating import (
    are_all_terminal_heating_loops_purchased_heating,
)
from rpd_generator.utilities.ashrae9012019.baseline_systems.baseline_hvac_sub_functions.are_all_terminal_types_vav import (
    are_all_terminal_types_vav,
)
from rpd_generator.utilities.ashrae9012019.baseline_systems.baseline_hvac_sub_functions.do_all_terminals_have_one_fan import (
    do_all_terminals_have_one_fan,
)
from rpd_generator.utilities.ashrae9012019.baseline_systems.baseline_hvac_sub_functions.does_each_zone_have_only_one_terminal import (
    does_each_zone_have_only_one_terminal,
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
from rpd_generator.utilities.ashrae9012019.baseline_systems.baseline_hvac_sub_functions.is_hvac_sys_preheat_fluid_loop_purchased_heating import (
    is_hvac_sys_preheat_fluid_loop_purchased_heating,
)
from rpd_generator.utilities.ashrae9012019.baseline_systems.baseline_hvac_sub_functions.is_hvac_sys_preheating_type_elec_resistance import (
    is_hvac_sys_preheating_type_elec_resistance,
)
from rpd_generator.utilities.ashrae9012019.baseline_systems.baseline_hvac_sub_functions.is_hvac_sys_preheating_type_fluid_loop import (
    is_hvac_sys_preheating_type_fluid_loop,
)
from rpd_generator.utilities.ashrae9012019.baseline_systems.baseline_system_util import (
    HVAC_SYS,
)
from rpd_generator.schema.schema_enums import SchemaEnums
from rpd_generator.utilities.ashrae9012019.baseline_systems.baseline_hvac_sub_functions.does_hvac_sys_have_component import (
    has_heating_system,
    has_preheat_system,
)

HEATING_SYSTEM = SchemaEnums.schema_enums["HeatingSystemOptions"]


def is_baseline_system_8(
    hvac,
    terminals_list,
    zones_list,
    chiller_loop_id_list,
    purchased_cooling_loop_id_list,
    purchased_heating_loop_id_list,
):
    """
    Get either Sys-8, Sys-8a, Sys-8b, Sys-8c, or Not_Sys_8 string output which indicates whether the HVAC system is ASHRAE 90.1 2019 Appendix G system 8 (VAV with Parallel Fan-Powered Boxes and Reheat), system 8a (system 8 with purchased CHW), system 8b (system 8 with purchased heating), or 8c (system 8 with purchased heating and purchased chilled water).

    Parameters
    ----------
    hvac: dict
    The HVAC system to evaluate.
    terminals_list: list
    list of terminals associated with the HVAC system to be evaluated. These are sent to this function from the master get_baseline_system_types function.
    zones_list: list
    list of zones associated with the HVAC system to be evaluated. These are sent to this function from the master get_baseline_system_types function.
    chiller_loop_id_list: list
    list of chiller loop ids associated with the building model. These are sent to this function from the master get_baseline_system_types function.
    purchased_cooling_loop_id_list: list
    list of purchased chilled water loop ids associated with the building model. These are sent to this function from the master get_baseline_system_types function.
    purchased_heating_loop_id_list: list
    list of purchased heating loop ids associated with the building model. These are sent to this function from the master get_baseline_system_types function.

    Returns
    -------
    The function returns either Sys-8, Sys-8a, Sys-8b, Sys-8c, or Not_Sys_8 string output which indicates whether the HVAC system is ASHRAE 90.1 2019 Appendix G system 8 (VAV with Parallel Fan-Powered Boxes and Reheat ), system 8a (system 8 with purchased CHW), system 8b (system 8 with purchased heating), or 8c (system 8 with purchased heating and purchased chilled water).
    """

    baseline_system_type = HVAC_SYS.UNMATCHED

    # check if the hvac system has the required sub systems for system type 8
    # If heating system DOESN'T exist and preheat system exists, has_required_sys=True, else, False
    has_required_sys = not has_heating_system(hvac) and has_preheat_system(hvac)

    are_sys_data_matched = (
        # short-circuit the logic if no required data is found.
        has_required_sys
        # sub functions handles missing required sys, and return False.
        and is_hvac_sys_cooling_type_fluid_loop(hvac)
        and is_hvac_sys_fan_sys_vsd(hvac)
        and does_each_zone_have_only_one_terminal(zones_list)
        and are_all_terminal_cool_sources_none_or_null(terminals_list)
        and do_all_terminals_have_one_fan(terminals_list)
        and are_all_terminal_types_vav(terminals_list)
        and are_all_terminal_fan_configs_parallel(terminals_list)
    )

    if are_sys_data_matched:
        if is_hvac_sys_preheating_type_elec_resistance(
            hvac
        ) and are_all_terminal_heat_sources_electric(terminals_list):
            if is_hvac_sys_fluid_loop_attached_to_chiller(hvac, chiller_loop_id_list):
                baseline_system_type = HVAC_SYS.SYS_8
            elif is_hvac_sys_fluid_loop_purchased_chw(
                hvac, purchased_cooling_loop_id_list
            ):
                baseline_system_type = HVAC_SYS.SYS_8A
        elif is_hvac_sys_preheating_type_fluid_loop(hvac):
            if (
                is_hvac_sys_preheat_fluid_loop_purchased_heating(
                    hvac, purchased_heating_loop_id_list
                )
                and are_all_terminal_heat_sources_hot_water(terminals_list)
                and are_all_terminal_heating_loops_purchased_heating(
                    terminals_list, purchased_heating_loop_id_list
                )
            ):
                if is_hvac_sys_fluid_loop_attached_to_chiller(
                    hvac, chiller_loop_id_list
                ):
                    baseline_system_type = HVAC_SYS.SYS_8B
                elif is_hvac_sys_fluid_loop_purchased_chw(
                    hvac, purchased_cooling_loop_id_list
                ):
                    baseline_system_type = HVAC_SYS.SYS_8C

    return baseline_system_type
