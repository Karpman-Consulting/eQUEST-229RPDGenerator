from typing import TypedDict

from pint import Quantity
from rpd_generator.utilities.jsonpath_utils import find_all
from rpd_generator.utilities.pint_utils import ZERO
from rpd_generator.schema.schema_utils import get_q


class HVACZoneListArea(TypedDict):
    total_area: Quantity
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
            zone_area = sum(
                (get_q(space, "floor_area", ZERO.AREA) for space in spaces), ZERO.AREA
            )
            assert zone_area > ZERO.AREA, f"zone:{zone['id']} has zero floor area"

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
                        "total_area": ZERO.AREA,
                    }
                    hvac_zone_list_w_area_dict[hvac_sys_id] = hvac_entry

                # Prevent double counting
                if zone_id not in hvac_entry["zones_list"]:
                    hvac_entry["zones_list"].append(zone_id)
                    hvac_entry["total_area"] += zone_area

                assert (
                    hvac_entry["total_area"] > ZERO.AREA
                ), f"terminal:{terminal['id']} serves zero floor area"

    return hvac_zone_list_w_area_dict
