from typing import Literal

from pint import Quantity
from rpd_generator.utilities.jsonpath_utils import find_all, find_one
from rpd_generator.utilities.pint_utils import ZERO


def get_zone_peak_internal_load_floor_area_dict(
    rmd: dict, zone: dict
) -> dict[Literal["peak", "area"], Quantity]:
    """
    Finds the peak coincident internal loads of a zone and returns the value with a load unit.
    The function returns a dict giving 2 values: {"peak":total peak (load unit) in the zone, "area":total zone area} the
    total peak is the internal non-coincident peak loads in all spaces in the zone

    The function does not raise exception for missing values rather it applies default values.

    Parameters
    ----------
    rmd: dict
    A dictionary representing a RuleModelInstance object as defined by the ASHRAE229 schema
    zone: dict
    A dictionary representing a Zone data group as defined by the ASHRAE229 schema

    Returns
    -------
    result: dict
    a dictionary that contains two keys, peak, and area.
    """
    zone_area = ZERO.AREA
    zone_load = ZERO.POWER

    for space in find_all("$.spaces[*]", zone):
        space_area = space.get("floor_area", ZERO.AREA)
        zone_area += space_area
        for light in find_all("$.interior_lighting[*]", space):
            # default value
            lighting_max_schedule_fraction = 1.0
            if light.get("lighting_multiplier_schedule"):
                lighting_multiplier_schedule = find_one(
                    f'$.schedules[?(@.id=="{light["lighting_multiplier_schedule"]}")]',
                    rmd,
                )
                lighting_max_schedule_fraction = max(
                    lighting_multiplier_schedule["hourly_cooling_design_day"]
                )

            zone_load += (
                light.get("power_per_area", ZERO.POWER_PER_AREA)
                * space_area
                * lighting_max_schedule_fraction
            )

        for equipment in find_all("$.miscellaneous_equipment[*]", space):
            # default value
            equipment_max_schedule_fraction = 1.0
            if equipment.get("multiplier_schedule"):
                equipment_multiplier_schedule = find_one(
                    f'$.schedules[?(@.id=="{equipment["multiplier_schedule"]}")]', rmd
                )
                equipment_max_schedule_fraction = max(
                    equipment_multiplier_schedule["hourly_cooling_design_day"]
                )

            zone_load += (
                equipment.get("power", ZERO.POWER) * equipment_max_schedule_fraction
            )

        # allows no occupants data in a zone
        occupant_max_schedule_fraction = 1.0
        if space.get("occupant_multiplier_schedule"):
            occupant_multiplier_schedule = find_one(
                f'$.schedules[?(@.id=="{space["occupant_multiplier_schedule"]}")]', rmd
            )
            occupant_max_schedule_fraction = max(
                occupant_multiplier_schedule["hourly_cooling_design_day"]
            )
        zone_load += (
            space.get("occupant_sensible_heat_gain", ZERO.POWER)
            + space.get("occupant_latent_heat_gain", ZERO.POWER)
        ) * occupant_max_schedule_fraction

    return {"peak": zone_load, "area": zone_area}
