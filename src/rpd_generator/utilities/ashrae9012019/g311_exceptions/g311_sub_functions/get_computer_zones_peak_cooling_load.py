from pint import Quantity
from rpd_generator.utilities.ashrae9012019.g311_exceptions.g311_sub_functions.get_zones_computer_rooms import (
    get_zone_computer_rooms,
)
from rpd_generator.utilities.get_zone_peak_internal_load_floor_area_dict import (
    get_zone_peak_internal_load_floor_area_dict,
)
from rpd_generator.utilities.pint_utils import ZERO


def get_computer_zones_peak_cooling_load(rmd: dict) -> Quantity:
    """
    Return peak load of computer zones in the building

    Parameters
    ----------
    rmd dict
        A dictionary representing a ruleset model description as defined by the ASHRAE229 schema

    Returns
    -------
    Peak load
    """
    computer_room_zones_dict = get_zone_computer_rooms(rmd)
    total_computer_peak_cooling_load = ZERO.POWER
    for computer_zone_id in computer_room_zones_dict:
        zone_peak_internal_load = get_zone_peak_internal_load_floor_area_dict(
            rmd, computer_room_zones_dict[computer_zone_id]["zone"]
        )["peak"]
        total_computer_peak_cooling_load += zone_peak_internal_load

    return total_computer_peak_cooling_load
