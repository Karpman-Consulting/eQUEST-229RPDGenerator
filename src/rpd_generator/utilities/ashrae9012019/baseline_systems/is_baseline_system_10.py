from rpd_generator.utilities.ashrae9012019.baseline_systems.baseline_hvac_sub_functions.are_all_terminal_cool_sources_none_or_null import (
    are_all_terminal_cool_sources_none_or_null,
)
from rpd_generator.utilities.ashrae9012019.baseline_systems.baseline_hvac_sub_functions.are_all_terminal_fans_null import (
    are_all_terminal_fans_null,
)
from rpd_generator.utilities.ashrae9012019.baseline_systems.baseline_hvac_sub_functions.are_all_terminal_heat_sources_electric import (
    are_all_terminal_heat_sources_electric,
)
from rpd_generator.utilities.ashrae9012019.baseline_systems.baseline_hvac_sub_functions.are_all_terminal_heat_sources_none_or_null import (
    are_all_terminal_heat_sources_none_or_null,
)
from rpd_generator.utilities.ashrae9012019.baseline_systems.baseline_hvac_sub_functions.are_all_terminal_types_cav import (
    are_all_terminal_types_cav,
)
from rpd_generator.utilities.ashrae9012019.baseline_systems.baseline_hvac_sub_functions.are_all_terminal_types_cav_with_none_equal_to_null import (
    are_all_terminal_types_cav_with_none_equal_to_null,
)
from rpd_generator.utilities.ashrae9012019.baseline_systems.baseline_hvac_sub_functions.do_all_terminals_have_one_fan import (
    do_all_terminals_have_one_fan,
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
from rpd_generator.utilities.ashrae9012019.baseline_systems.baseline_hvac_sub_functions.is_hvac_sys_heating_type_elec_resistance import (
    is_hvac_sys_heating_type_elec_resistance,
)
from rpd_generator.utilities.ashrae9012019.baseline_systems.baseline_system_util import (
    HVAC_SYS,
)
from rpd_generator.schema.schema_enums import SchemaEnums
from rpd_generator.utilities.ashrae9012019.baseline_systems.baseline_hvac_sub_functions.does_hvac_sys_have_component import (
    has_fan_system,
    has_heating_system,
    has_preheat_system,
)

HEATING_SYSTEM = SchemaEnums.schema_enums["HeatingSystemOptions"]


def is_baseline_system_10(hvac, terminals_list, zones_list):
    """
    Get either Sys-10 or Not_Sys_10 string output which indicates whether the HVAC system is ASHRAE 90.1 2019 Appendix G system 10 (Heating and Ventilation with electric heating).

    Parameters
    ----------
    hvac: dict
    The HVAC system to evaluate.
    terminals_list: list
    list of terminals associated with the HVAC system to be evaluated. These are sent to this function from the master get_baseline_system_types function.
    zones_list: list
    list of zones associated with the HVAC system to be evaluated. These are sent to this function from the master get_baseline_system_types function.

    Returns
    -------
    The function returns either Sys-10 or Not_Sys_10 string output which indicates whether the HVAC system is ASHRAE 90.1 2019 Appendix G system 10 (Heating and Ventilation with electric heating).
    """

    baseline_system_type = HVAC_SYS.UNMATCHED

    # check if the hvac system has the required sub systems for system type 10
    # if preheat, heating, and fan systems DON'T exist, has_required_sys=True, else, False
    has_required_sys = not (
        has_preheat_system(hvac) or has_heating_system(hvac) or has_fan_system(hvac)
    )

    are_sys_10_data_matched = (
        # short-circuit the logic if no required data is found.
        has_required_sys
        # sub functions handles missing required sys, and return False.
        and is_hvac_sys_cooling_type_none_or_non_mechanical(hvac)
        and does_each_zone_have_only_one_terminal(zones_list)
        and are_all_terminal_heat_sources_electric(terminals_list)
        and are_all_terminal_cool_sources_none_or_null(terminals_list)
        and do_all_terminals_have_one_fan(terminals_list)
        and are_all_terminal_types_cav_with_none_equal_to_null(terminals_list)
    )

    if are_sys_10_data_matched:
        baseline_system_type = HVAC_SYS.SYS_10
        return baseline_system_type

    # When the first logic of are_sys_10_data_matched is false
    # if preheat system DOESN'T exist and heating/fan systems exist, has_required_sys=True, else, False
    has_required_sys = (
        not has_preheat_system(hvac)
        and has_heating_system(hvac)
        and has_fan_system(hvac)
    )

    are_sys_10_data_matched = (
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
        and is_hvac_sys_heating_type_elec_resistance(hvac)
    )

    if are_sys_10_data_matched:
        baseline_system_type = HVAC_SYS.SYS_10

    return baseline_system_type
