from typing import Literal

from pint import Quantity
from rpd_generator.utilities.jsonpath_utils import find_all, find_one


def get_zone_peak_internal_load_floor_area_dict(
    rmd: dict, zone: dict
) -> dict[Literal["peak", "area"], Quantity]:
    """
    Finds the peak coincident internal loads of a zone and returns the value in btu/h/ft2
    The function returns a dict giving 2 values: {"PEAK":total peak btu/h/ft2 in the zone, "AREA":total zone area} the
    total peak btu/sf is the internal non-coincident peak loads in all spaces in the zone

    The function does not raise exception for missing values rather it applies default values.

    Parameters
    ----------
    rmd: dict
    A dictionary representing a RuleModelInstance object as defined by the ASHRAE229 schema
    zone: dict
        zone dictionary representing a zone object as defined by the ASHRAE229 schema

    Returns
    -------
    result: dict
    a dictionary that contains two keys, peak, and area.
    """
    zone_area = 0
    zone_load = 0

    for space in find_all("$.spaces[*]", zone):
        space_area = space.get("floor_area", 0)
        zone_area += space_area
        for light in find_all("$.interior_lighting[*]", space):
            lighting_design_schedule = find_one(
                f'$.schedules[?(@.id=="{light["lighting_multiplier_schedule"]}")]', rmd
            )
            lighting_max_schedule_fraction = max(
                lighting_design_schedule.get("hourly_cooling_design_day", []), default=0
            )
            zone_load += (
                light.get("power_per_area", 0)
                * space_area
                * lighting_max_schedule_fraction
            )

        for equipment in find_all("$.miscellaneous_equipment[*]", space):
            equipment_design_schedule = find_one(
                f'$.schedules[?(@.id=="{equipment["multiplier_schedule"]}")]', rmd
            )
            equipment_max_schedule_fraction = max(
                equipment_design_schedule.get("hourly_cooling_design_day", []),
                default=0,
            )
            zone_load += equipment.get("power", 0) * equipment_max_schedule_fraction

        # allows no occupants data in a zone
        occupant_max_schedule_fraction = 0.0
        if space.get("occupant_multiplier_schedule"):
            occupant_design_schedule = find_one(
                f'$.schedules[?(@.id=="{space["occupant_multiplier_schedule"]}")]', rmd
            )
            occupant_max_schedule_fraction = max(
                occupant_design_schedule.get("hourly_cooling_design_day", []), default=0
            )
        zone_load += (
            space.get("occupant_sensible_heat_gain", 0)
            + space.get("occupant_latent_heat_gain", 0)
        ) * occupant_max_schedule_fraction

    return {"peak": zone_load, "area": zone_area}
