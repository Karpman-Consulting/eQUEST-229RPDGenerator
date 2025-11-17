from pint import Quantity
from rpd_generator.utilities.ashrae9012019.data_fns.table_lighting_to_hvac_bat_map_fns import (
    space_lighting_to_hvac_bat,
)
from rpd_generator.utilities.jsonpath_utils import find_all


def get_zone_hvac_bat_dict(zone: dict) -> dict[str, Quantity]:
    """
    Get a dictionary of the HVAC_BAT and areas for a given zone.
        - used to verify the correct type of HVAC baseline system (or systems)
        - The function looks at the space lighting type.

    Parameters
    ----------
    zone: dict
        A dictionary representing a zone data group as defined by the ASHRAE229 schema

    Returns
    -------
    zone_hvac_bat_dict dict A dict for the zone that saves the HVAC_BAT as keys and the areas as the
    values. Example: {OTHER_NON_RESIDENTIAL: 500, PUBLIC_ASSEMBLY: 2000}

    """
    zone_hvac_bat_dict = dict()
    for space in find_all("$.spaces[*]", zone):
        # set default to None to not fail the data retrieving (space could have no lighting space type)
        space_hvac_bat = space_lighting_to_hvac_bat(
            space.get("lighting_space_type", "NONE")
        )
        # Default missing floor area to ZERO Area
        zone_hvac_bat_dict[space_hvac_bat] = zone_hvac_bat_dict.get(
            space_hvac_bat, 0
        ) + space.get("floor_area", 0)
    return zone_hvac_bat_dict
