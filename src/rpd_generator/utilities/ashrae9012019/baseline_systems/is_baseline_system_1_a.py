from rpd_generator.utilities.ashrae9012019.baseline_systems.baseline_hvac_sub_functions.are_all_terminal_chw_loops_purchased_cooling import (
    are_all_terminal_chw_loops_purchased_cooling,
)
from rpd_generator.utilities.ashrae9012019.baseline_systems.baseline_hvac_sub_functions.are_all_terminal_cool_sources_chilled_water import (
    are_all_terminal_cool_sources_chilled_water,
)
from rpd_generator.utilities.ashrae9012019.baseline_systems.baseline_hvac_sub_functions.are_all_terminal_heat_sources_hot_water import (
    are_all_terminal_heat_sources_hot_water,
)
from rpd_generator.utilities.ashrae9012019.baseline_systems.baseline_hvac_sub_functions.are_all_terminal_heating_loops_attached_to_boiler import (
    are_all_terminal_heating_loops_attached_to_boiler,
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
from rpd_generator.utilities.ashrae9012019.baseline_systems.baseline_hvac_sub_functions.is_hvac_sys_cooling_type_none import (
    is_hvac_sys_cooling_type_none,
)
from rpd_generator.schema.schema_enums import SchemaEnums
from rpd_generator.utilities.ashrae9012019.baseline_systems.baseline_hvac_sub_functions.does_hvac_sys_have_component import (
    has_fan_system,
    has_heating_system,
    has_preheat_system,
)

HEATING_SYSTEM = SchemaEnums.schema_enums["HeatingSystemOptions"]


def is_baseline_system_1_a(
    hvac,
    terminals_list,
    zones_list,
    boiler_loop_id_list,
    purchased_cooling_loop_id_list,
):
    """
    Returns true or false to whether the baseline system type is 1a (system 1 with purchased CHW and HW served by a boiler).

    Parameters
    ----------
    hvac: dict
    The HVAC system to evaluate.
    terminals_list: List<Dict>
    list of terminals associated with the HVAC system to be evaluated. These are sent to this function from the is_baseline_system_1 function.
    zones_list: List<Dict>
    list of zones associated with the HVAC system to be evaluated. TThese are sent to this function from the is_baseline_system_1 function.
    boiler_loop_id_list: List[str]
    list of boiler loop IDs associated with the HVAC system to be evaluated. These are sent to this function from the is_baseline_system_1 function.
    purchased_cooling_loop_id_list: List[str]
    list of purchased cooling loop IDs associated with the HVAC system to be evaluated. These are sent to this function from the is_baseline_system_1 function.

    Returns
    -------
    true or false to whether the baseline system type is 1a (system 1 with purchased CHW and HW served by a boiler).
    """

    # check if the hvac system has the required sub systems for system type 1a
    # if preheat, heating, and fan systems DON'T exist, has_required_sys=True, else, False
    has_required_sys = not (
        has_preheat_system(hvac) and has_heating_system(hvac) and has_fan_system(hvac)
    )

    return (
        # short-circuit the logic if no required data is found.
        has_required_sys
        # sub functions handles missing required sys, and return False.
        and is_hvac_sys_cooling_type_none(hvac)
        and does_each_zone_have_only_one_terminal(zones_list)
        and are_all_terminal_heat_sources_hot_water(terminals_list)
        and are_all_terminal_cool_sources_chilled_water(terminals_list)
        and do_all_terminals_have_one_fan(terminals_list)
        and are_all_terminal_types_cav_with_none_equal_to_null(terminals_list)
        and are_all_terminal_heating_loops_attached_to_boiler(
            terminals_list, boiler_loop_id_list
        )
        and are_all_terminal_chw_loops_purchased_cooling(
            terminals_list, purchased_cooling_loop_id_list
        )
    )


def diagnose_baseline_system_1_a(
    hvac,
    terminals_list,
    zones_list,
    boiler_loop_id_list,
    purchased_cooling_loop_id_list,
):
    diagnostics = {}

    diagnostics["has_no_preheat_heating_fan_systems"] = not (
        has_preheat_system(hvac) and has_heating_system(hvac) and has_fan_system(hvac)
    )
    diagnostics["cooling_type_none"] = is_hvac_sys_cooling_type_none(hvac)
    diagnostics["one_terminal_per_zone"] = does_each_zone_have_only_one_terminal(
        zones_list
    )
    diagnostics["terminal_heat_sources_hw"] = are_all_terminal_heat_sources_hot_water(
        terminals_list
    )
    diagnostics["terminal_cool_sources_chw"] = (
        are_all_terminal_cool_sources_chilled_water(terminals_list)
    )
    diagnostics["terminals_have_one_fan"] = do_all_terminals_have_one_fan(
        terminals_list
    )
    diagnostics["terminal_types_cav"] = (
        are_all_terminal_types_cav_with_none_equal_to_null(terminals_list)
    )
    diagnostics["terminal_heating_loops_attached_to_boiler"] = (
        are_all_terminal_heating_loops_attached_to_boiler(
            terminals_list, boiler_loop_id_list
        )
    )
    diagnostics["terminal_chw_loops_purchased"] = (
        are_all_terminal_chw_loops_purchased_cooling(
            terminals_list, purchased_cooling_loop_id_list
        )
    )

    passed = all(diagnostics.values())

    return {
        "expected_system": "Sys-1a",
        "passed": passed,
        "diagnostics": diagnostics,
    }
