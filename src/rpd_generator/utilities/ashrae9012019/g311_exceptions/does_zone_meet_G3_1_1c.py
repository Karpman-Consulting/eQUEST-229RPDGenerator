import numpy as np
from pydash import map_
from typing import TypedDict
from pint import Quantity
from rpd_generator.utilities.pint_utils import ZERO
from rpd_generator.config import Config

ureg = Config.ureg

from rpd_generator.utilities.ashrae9012019.baseline_system_type_compare import (
    baseline_system_type_compare,
)
from rpd_generator.utilities.ashrae9012019.baseline_systems.baseline_system_util import (
    HVAC_SYS,
)
from rpd_generator.utilities.ashrae9012019.g311_exceptions.g311_sub_functions.get_zone_eflh import (
    get_zone_eflh,
)
from rpd_generator.utilities.ashrae9012019.g311_exceptions.g311_sub_functions.get_zones_computer_rooms import (
    get_zone_computer_rooms,
)
from rpd_generator.utilities.ashrae9012019.g311_exceptions.g311_sub_functions.get_zones_on_same_floor_list import (
    get_zones_on_same_floor_list,
)
from rpd_generator.utilities.get_zone_peak_internal_load_floor_area_dict import (
    get_zone_peak_internal_load_floor_area_dict,
)
from rpd_generator.utilities.jsonpath_utils import find_all


class ZoneandSystem(TypedDict):
    expected_system_type: str
    system_origin: str


class G311CDiagnostics(TypedDict):
    meets: bool
    zone_load_per_area: Quantity
    avg_internal_load_area: Quantity
    zone_eflh: float
    avg_eflh: float
    load_diff: Quantity
    eflh_diff: float


ELIGIBLE_PRIMARY_SYSTEM_TYPES = [
    HVAC_SYS.SYS_5,
    HVAC_SYS.SYS_6,
    HVAC_SYS.SYS_7,
    HVAC_SYS.SYS_8,
]

NUMBER_OF_WEEKS_IN_YEAR = 52.1429
NUMBER_OF_WEEKS_IN_LEAP_YEAR = 52.2857
LOAD_THRESHOLD = 10 * ureg("Btu/hr/ft2")
EFLH_THRESHOLD = 40


def _infer_num_hours_per_year(rmd: dict) -> int:
    """Infer the number of hours in the year from any valid hourly schedule."""
    for sched in find_all("$.schedules[*].hourly_values", rmd):
        if isinstance(sched, list) and len(sched) > 0:
            return len(sched)
    # Fallback default
    return 8760


def _get_zone_weekly_eflh(rmd: dict, zone: dict, num_weeks: float) -> float:
    z_eflh = get_zone_eflh(rmd, zone)
    return z_eflh / num_weeks if num_weeks else 0.0


def get_g3_1_1c_diagnostics(
    rmd: dict,
    zone: dict,
    zones_and_systems: dict[str, ZoneandSystem],
) -> G311CDiagnostics:
    """
    Full diagnostics for G3.1.1c, including loads, EFLH, and differences.
    """
    num_hours = _infer_num_hours_per_year(rmd)
    num_weeks = num_hours / 168.0

    expected_system_type = zones_and_systems[zone["id"]]["expected_system_type"]
    system_matched = any(
        baseline_system_type_compare(
            expected_system_type, target_system_type, exact_match=False
        )
        for target_system_type in ELIGIBLE_PRIMARY_SYSTEM_TYPES
    )

    # Defaults for diagnostics
    zone_load_per_area = ZERO.POWER_PER_AREA
    avg_internal_load_area = ZERO.POWER_PER_AREA
    zone_eflh = 0.0
    avg_eflh = 0.0
    load_diff = ZERO.POWER_PER_AREA
    eflh_diff = 0.0
    meet_g3_1_1c_flag = False

    if system_matched:
        zones_on_same_floor = get_zones_on_same_floor_list(rmd, zone)
        zones_on_same_floor = [
            z for z in zones_on_same_floor if z.get("id") != zone.get("id")
        ]

        # Keep only zones with same expected system type
        zones_same_floor_same_system_type = [
            other_zone
            for other_zone in zones_on_same_floor
            if (
                zones_and_systems.get(other_zone["id"])
                and zones_and_systems[other_zone["id"]]["expected_system_type"]
                == expected_system_type
            )
        ]

        zone_internal_loads = get_zone_peak_internal_load_floor_area_dict(rmd, zone)
        zone_eflh = _get_zone_weekly_eflh(rmd, zone, num_weeks)

        if zone_internal_loads["area"] != ZERO.AREA:
            zone_load_per_area = (
                zone_internal_loads["peak"] / zone_internal_loads["area"]
            )
        else:
            zone_load_per_area = ZERO.POWER_PER_AREA

        if zones_same_floor_same_system_type:
            zone_load_and_eflh_list = [
                (
                    get_zone_peak_internal_load_floor_area_dict(rmd, other_match_zone),
                    _get_zone_weekly_eflh(rmd, other_match_zone, num_weeks),
                )
                for other_match_zone in zones_same_floor_same_system_type
            ]
        else:
            # Only zone on floor with this system type: compare to itself
            zone_load_and_eflh_list = [(zone_internal_loads, zone_eflh)]

        system_total_area: Quantity = sum(
            map_(zone_load_and_eflh_list, "0.area"), ZERO.AREA
        )
        system_total_load: Quantity = sum(
            map_(zone_load_and_eflh_list, "0.peak"), ZERO.POWER
        )

        if system_total_area != ZERO.AREA:
            avg_eflh = (
                np.dot(
                    map_(zone_load_and_eflh_list, lambda zl: zl[1]),
                    map_(zone_load_and_eflh_list, lambda zl: zl[0]["area"].magnitude),
                )
                / system_total_area.magnitude
            )
            avg_internal_load_area = system_total_load / system_total_area
        else:
            avg_eflh = 0.0
            avg_internal_load_area = ZERO.POWER_PER_AREA

        load_diff = abs(zone_load_per_area - avg_internal_load_area)
        eflh_diff = zone_eflh - avg_eflh

        meet_g3_1_1c_flag = load_diff > LOAD_THRESHOLD or eflh_diff > EFLH_THRESHOLD

        if meet_g3_1_1c_flag:
            meet_g3_1_1c_flag = zone["id"] not in get_zone_computer_rooms(rmd)

    return G311CDiagnostics(
        meets=meet_g3_1_1c_flag,
        zone_load_per_area=zone_load_per_area,
        avg_internal_load_area=avg_internal_load_area,
        zone_eflh=zone_eflh,
        avg_eflh=avg_eflh,
        load_diff=load_diff,
        eflh_diff=eflh_diff,
    )


def does_zone_meet_g3_1_1c(
    rmd: dict,
    zone: dict,
    zones_and_systems: dict[str, ZoneandSystem],
) -> bool:
    """
    Wrapper that preserves the original API.
    """
    diag = get_g3_1_1c_diagnostics(rmd, zone, zones_and_systems)
    return diag["meets"]
