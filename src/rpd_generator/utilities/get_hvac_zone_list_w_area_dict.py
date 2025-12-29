from typing import TypedDict

from rpd_generator.utilities.jsonpath_utils import find_all


class HVACZoneListArea(TypedDict):
    total_area: float
    zones_list: list[str]


def get_hvac_zone_list_w_area_by_rmd_dict(rmd: dict) -> dict[str, HVACZoneListArea]:
    """
    RMD version of the get_hvac_zone_list_w_area_dict function

    Parameters
    ----------
    rmd dict
        A dictionary representing a ruleset model description as defined by the ASHRAE229 schema

    Returns
    -------
    dict
        A dictionary of the form
        {
            <hvac_system id>: {
                "zones_list": [<zones served by the hvac system>],
                "total_area": <total area served by the hvac system>
            }
        }
    """
    hvac_zone_list_w_area_dict = {}

    for building in rmd.get("buildings", []):
        hvac_zone_list_w_area_dict.update(get_hvac_zone_list_w_area_dict(building))

    return hvac_zone_list_w_area_dict


def get_hvac_zone_list_w_area_dict(building: dict) -> dict[str, HVACZoneListArea]:
    hvac_zone_list_w_area_dict: dict[str, HVACZoneListArea] = {}

    # Cache zones once
    for building_segment in building.get("building_segments", []):
        for zone in building_segment.get("zones", []):

            terminals = zone.get("terminals")
            # Note: None and [] are falsey; zone.terminals is optional
            if not terminals:
                continue

            # Cache spaces and zone area once
            spaces = zone.get("spaces", [])
            zone_area = sum((space.get("floor_area", 0) for space in spaces), 0)
            assert zone_area > 0, f"zone:{zone['id']} has zero floor area"

            zone_id = zone["id"]

            for terminal in terminals:
                hvac_sys_id = terminal.get(
                    "served_by_heating_ventilating_air_conditioning_system"
                )
                if hvac_sys_id is None:
                    continue

                hvac_entry = hvac_zone_list_w_area_dict.get(hvac_sys_id)
                if hvac_entry is None:
                    hvac_entry = {
                        "zones_list": [],
                        "total_area": 0,
                    }
                    hvac_zone_list_w_area_dict[hvac_sys_id] = hvac_entry

                # Prevent double counting
                if zone_id not in hvac_entry["zones_list"]:
                    hvac_entry["zones_list"].append(zone_id)
                    hvac_entry["total_area"] += zone_area

                assert (
                    hvac_entry["total_area"] > 0
                ), f"terminal:{terminal['id']} serves zero floor area"

    return hvac_zone_list_w_area_dict
