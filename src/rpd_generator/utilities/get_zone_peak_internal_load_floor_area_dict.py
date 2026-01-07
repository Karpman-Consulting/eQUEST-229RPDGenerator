from typing import Literal

from pint import Quantity
from rpd_generator.utilities.pint_utils import ZERO
from rpd_generator.config import Config

ureg = Config.ureg


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
    zone_area = ZERO.AREA
    zone_load = ZERO.POWER
    schedules_map = {sch["id"]: sch for sch in rmd.get("schedules", [])}
    for space in zone.get("spaces", []):
        space_area = space.get("floor_area", ZERO.AREA)
        zone_area += space_area

        for light in space.get("interior_lighting", []):
            lighting_schedule_id = light.get("lighting_multiplier_schedule")
            lighting_schedule = schedules_map.get(lighting_schedule_id, {})
            cooling_design_values = [
                v
                for v in (
                    lighting_schedule.get("hourly_cooling_design_year")
                    or lighting_schedule.get("hourly_cooling_design_day")
                    or []
                )
                if v is not None
            ]
            if cooling_design_values:
                lighting_design_schedule_max_fraction = max(
                    cooling_design_values, default=0
                )
            else:
                lighting_design_schedule_max_fraction = 0.0
            zone_load += (
                light.get("power_per_area", ZERO.POWER_PER_AREA)
                * space_area
                * lighting_design_schedule_max_fraction
            )

        for equipment in space.get("miscellaneous_equipment", []):
            equipment_schedule_id = equipment.get("multiplier_schedule")
            equipment_schedule = schedules_map.get(equipment_schedule_id, {})
            cooling_design_values = [
                v
                for v in (
                    equipment_schedule.get("hourly_cooling_design_year")
                    or equipment_schedule.get("hourly_cooling_design_day")
                    or []
                )
                if v is not None
            ]
            if cooling_design_values:
                equipment_design_schedule_max_fraction = max(
                    cooling_design_values, default=0
                )
            else:
                equipment_design_schedule_max_fraction = 0.0
            zone_load += (
                equipment.get("power", ZERO.POWER)
                * equipment_design_schedule_max_fraction
            )

        # allows no occupants data in a zone
        occupant_design_schedule_max_fraction = 0.0
        if space.get("occupant_multiplier_schedule"):
            occupant_schedule_id = space.get("occupant_multiplier_schedule")
            occupant_schedule = schedules_map.get(occupant_schedule_id, {})
            cooling_design_values = [
                v
                for v in (
                    occupant_schedule.get("hourly_cooling_design_year")
                    or occupant_schedule.get("hourly_cooling_design_day")
                    or []
                )
                if v is not None
            ]
            if cooling_design_values:
                occupant_design_schedule_max_fraction = max(
                    cooling_design_values, default=0
                )
            else:
                occupant_design_schedule_max_fraction = 0.0

        zone_load += (
            space.get("occupant_sensible_heat_gain", ZERO.POWER)
            + space.get("occupant_latent_heat_gain", ZERO.POWER)
        ) * occupant_design_schedule_max_fraction

    return {"peak": zone_load, "area": zone_area}
