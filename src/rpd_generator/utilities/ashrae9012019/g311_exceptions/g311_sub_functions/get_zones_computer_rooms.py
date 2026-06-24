from typing import Literal

from pint import Quantity
from rpd_generator.utilities.ashrae9012019.g311_exceptions.g311_sub_functions.is_space_a_computer_room import (
    is_space_a_computer_room,
)
from rpd_generator.schema.schema_enums import SchemaEnums
from rpd_generator.utilities.jsonpath_utils import find_all
from rpd_generator.utilities.pint_utils import ZERO
from rpd_generator.schema.schema_utils import get_q

LightingSpaceOptions2019ASHRAE901TG37 = SchemaEnums.schema_enums[
    "LightingSpaceOptions2019ASHRAE901TG37"
]


def get_zone_computer_rooms(
    rmd: dict,
) -> dict[
    str,
    dict[
        Literal["total_zone_floor_area", "zone_computer_room_floor_area", "zone"],
        Quantity,
    ],
]:
    """
    Returns a dictionary with the zones that have at least one computer room space associated with them in the rmd as the keys.
    The values associated with each key are in a dict form. The dict associated with each key contains the computer room
    floor area as the first item and the total zone floor area as the second item.

    Parameters
    ----------
    rmd dict
        A dictionary representing a RuleModelDescription object as defined by the ASHRAE229 schema

    Returns
    -------
    zones_with_computer_room_dict
        A dictionary with the zones that have at least one computer room space associated with them in the rmd as the keys.
        The values associated with each key are in a dict form. The dict associated with each key contains the computer room
        floor area as the first item and the total zone floor area as the second item.
    """

    zone_with_computer_room_dict = {}
    for zone in find_all("$.buildings[*].building_segments[*].zones[*]", rmd):
        zone_has_computer_room_check = any(
            [
                is_space_a_computer_room(rmd, space)
                for space in find_all("$.spaces[*]", zone)
            ]
        )

        if zone_has_computer_room_check:
            zone_with_computer_room_dict[zone["id"]] = {
                "zone_computer_room_floor_area": sum(
                    [
                        get_q(space, "floor_area", ZERO.AREA)
                        for space in find_all("$.spaces[*]", zone)
                        if is_space_a_computer_room(rmd, space)
                    ],
                    ZERO.AREA,
                ),
                "total_zone_floor_area": sum(
                    [
                        get_q(space, "floor_area", ZERO.AREA)
                        for space in find_all("$.spaces[*]", zone)
                    ],
                    ZERO.AREA,
                ),
                "zone": zone,
            }

    return zone_with_computer_room_dict
