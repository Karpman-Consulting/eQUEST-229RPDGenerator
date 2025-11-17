from typing import TypedDict
from rpd_generator.utilities.jsonpath_utils import find_all


class ZonesTerminalsServedByHVACSys(TypedDict):
    terminals_list: list[dict]
    zones_list: list[dict]


def get_dict_of_zones_and_terminals_served_by_hvac_sys(
    rmd: dict,
) -> dict[str, ZonesTerminalsServedByHVACSys]:
    """
    Returns a dictionary of zones and terminal unit IDs associated with each HVAC system in the RMD.

    Parameters
    ----------
    rmd: dict
    A dictionary representing a RuleModelDescription object as defined by the ASHRAE229 schema

    Returns ------- dict: a dictionary of zones and terminal unit IDs associated with each HVAC system in the RMD,
    {hvac_system_1.id: {"zones_list": [zone_1.id, zone_2.id, zone_3.id], "terminals_list": [terminal_1.id,
    terminal_2.id, terminal_3.id]}, hvac_system_2.id: {"zones_list": [zone_4.id, zone_9.id, zone_30.id],
    "terminals_list": [terminal_10.id, terminal_20.id, terminal_30.id]}}
    """
    dict_of_zones_and_terminal_units_served_by_hvac_sys = {}

    for zone in find_all(
        "$.buildings[*].building_segments[*].zones[*]",
        rmd,
    ):
        for terminal in find_all("$.terminals[*]", zone):
            hvac_sys_id = terminal.get(
                "served_by_heating_ventilating_air_conditioning_system"
            )
            if not hvac_sys_id:
                continue

            if hvac_sys_id not in dict_of_zones_and_terminal_units_served_by_hvac_sys:
                dict_of_zones_and_terminal_units_served_by_hvac_sys[hvac_sys_id] = {
                    "zones_list": [],
                    "terminals_list": [],
                }

            # Get lists
            zones_list = dict_of_zones_and_terminal_units_served_by_hvac_sys[
                hvac_sys_id
            ]["zones_list"]
            terminals_list = dict_of_zones_and_terminal_units_served_by_hvac_sys[
                hvac_sys_id
            ]["terminals_list"]

            # Append zone object (avoid duplicates)
            if zone not in zones_list:
                zones_list.append(zone)

            # Append terminal object (avoid duplicates)
            if terminal not in terminals_list:
                terminals_list.append(terminal)

    return dict_of_zones_and_terminal_units_served_by_hvac_sys
