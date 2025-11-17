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


def is_baseline_system_7(
    hvac,
    terminals_list,
    zones_list,
    boiler_loop_id_list,
    purchased_heating_loop_id_list,
    chiller_loop_id_list,
    purchased_cooling_loop_id_list,
):
    """
    Get either Sys-7, Sys-7a, Sys-7b, Sys-7c or Not_Sys_7 string output which indicates whether the HVAC system is
    ASHRAE 90.1 2019 Appendix G system 7 (VAV with Reheat), system 7a (system 7 with purchased CHW), system 7b (
    system 7 with purchased heating), or system 7c (system 7 with purchased heating and purchased CHW).

    Parameters
    ----------
    hvac: dict
    The HVAC system to evaluate.
    terminals_list: List<Dict>,
    list of terminals associated with the HVAC system to be evaluated. These are sent to this function from the master get_baseline_system_types function.
    zones_list: List<Dict>,
    list of zones associated with the HVAC system to be evaluated. These are sent to this function from the master get_baseline_system_types function.
    boiler_loop_id_list: list
    list of boiler loop IDs in the model.
    purchased_heating_loop_id_list: list
    list of purchased heating loop IDs in the model.
    chiller_loop_id_list: list
    list of chiller loop IDs in the model.
    purchased_cooling_loop_id_list: list
    list of purchased chilled water loop IDs in the model.

    Returns
    -------
    The function returns either Sys-7, Sys-7a, Sys-7b, Sys-7c or Not_Sys_7 string output which indicates
    whether the HVAC system is ASHRAE 90.1 2019 Appendix G system 7 (VAV with Reheat), system 7a (system 7 with
    purchased CHW), system 7b (system 7 with purchased heating), pr system 7c (system 7 with purchased heating and
    purchased CHW). -------
    """
    baseline_system_type = HVAC_SYS.UNMATCHED

    # check if the hvac system has the required sub systems for system type 7
    # if heating system DOESN'T exist and preheat/cooling systems exist, has_required_sys=True, else, False.
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
        and is_hvac_sys_cooling_type_fluid_loop(hvac)
        and is_hvac_sys_fan_sys_vsd(hvac)
        and does_each_zone_have_only_one_terminal(zones_list)
        and are_all_terminal_heat_sources_hot_water(terminals_list)
        and are_all_terminal_cool_sources_none_or_null(terminals_list)
        and are_all_terminal_fans_null(terminals_list)
        and are_all_terminal_types_vav(terminals_list)
    )

    if are_sys_data_matched:
        # Confirm required data for Sys-7, now to decide which system type 7
        is_hvac_sys_fluid_loop_attached_to_chiller_flag = (
            is_hvac_sys_fluid_loop_attached_to_chiller(hvac, chiller_loop_id_list)
        )
        is_hvac_sys_fluid_loop_purchased_chw_flag = (
            is_hvac_sys_fluid_loop_purchased_chw(hvac, purchased_cooling_loop_id_list)
        )
        if is_hvac_sys_preheat_fluid_loop_attached_to_boiler(
            hvac, boiler_loop_id_list
        ) and are_all_terminal_heating_loops_attached_to_boiler(
            terminals_list, boiler_loop_id_list
        ):
            if is_hvac_sys_fluid_loop_attached_to_chiller_flag:
                baseline_system_type = HVAC_SYS.SYS_7
            elif is_hvac_sys_fluid_loop_purchased_chw_flag:
                baseline_system_type = HVAC_SYS.SYS_7A
        elif is_hvac_sys_preheat_fluid_loop_purchased_heating(
            hvac, purchased_heating_loop_id_list
        ) and are_all_terminal_heating_loops_purchased_heating(
            terminals_list, purchased_heating_loop_id_list
        ):
            if is_hvac_sys_fluid_loop_attached_to_chiller_flag:
                baseline_system_type = HVAC_SYS.SYS_7B
            elif is_hvac_sys_fluid_loop_purchased_chw_flag:
                baseline_system_type = HVAC_SYS.SYS_7C

    return baseline_system_type
