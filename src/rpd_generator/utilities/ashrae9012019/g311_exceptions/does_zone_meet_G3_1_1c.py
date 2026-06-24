from typing import TypedDict
from pint import Quantity

from rpd_generator.utilities.pint_utils import ZERO
from rpd_generator.config import Config
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

ureg = Config.ureg


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
    load_diff_threshold: Quantity
    eflh_diff_threshold: float


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
    zone_internal_load_dict: dict[str, dict] | None = None,
    zone_eflh_dict: dict[str, float] | None = None,
    zones_by_floor_map: dict[str, list[dict]] | None = None,
    computer_room_zones_dict: dict | None = None,
) -> G311CDiagnostics:

    num_hours = _infer_num_hours_per_year(rmd)
    num_weeks = num_hours / 168.0

    if zone_internal_load_dict is not None:
        zone_internal = zone_internal_load_dict[zone["id"]]
    else:
        zone_internal = get_zone_peak_internal_load_floor_area_dict(rmd, zone)

    if zone_eflh_dict is not None:
        zone_eflh_raw = zone_eflh_dict[zone["id"]]
    else:
        zone_eflh_raw = get_zone_eflh(rmd, zone)
    zone_eflh = zone_eflh_raw / num_weeks if num_weeks else 0.0

    zone_load_per_area = (
        zone_internal["peak"] / zone_internal["area"]
        if zone_internal["area"] != ZERO.AREA
        else ZERO.POWER_PER_AREA
    )

    expected_system_type = zones_and_systems[zone["id"]]["expected_system_type"]

    system_matched = any(
        baseline_system_type_compare(expected_system_type, sys_type, exact_match=False)
        for sys_type in ELIGIBLE_PRIMARY_SYSTEM_TYPES
    )

    if zones_by_floor_map is not None:
        floor_name = zone.get("floor_name")
        zones_on_same_floor = [
            z
            for z in zones_by_floor_map.get(floor_name, [])
            if z.get("id") != zone.get("id")
            and zones_and_systems.get(z.get("id"))
            and zones_and_systems[z["id"]]["expected_system_type"]
            == expected_system_type
        ]
    else:
        zones_on_same_floor = [
            z
            for z in get_zones_on_same_floor_list(rmd, zone)
            if z.get("id") != zone.get("id")
            and zones_and_systems.get(z.get("id"))
            and zones_and_systems[z["id"]]["expected_system_type"]
            == expected_system_type
        ]

    comparison_zones = zones_on_same_floor or [zone]

    if zone_internal_load_dict is not None and zone_eflh_dict is not None:
        zone_load_eflh_pairs = [
            (
                zone_internal_load_dict[z["id"]],
                zone_eflh_dict[z["id"]] / num_weeks if num_weeks else 0.0,
            )
            for z in comparison_zones
        ]
    else:
        zone_load_eflh_pairs = [
            (
                get_zone_peak_internal_load_floor_area_dict(rmd, z),
                _get_zone_weekly_eflh(rmd, z, num_weeks),
            )
            for z in comparison_zones
        ]

    total_area: Quantity = sum(
        (zl["area"] for zl, _ in zone_load_eflh_pairs), ZERO.AREA
    )
    total_load: Quantity = sum(
        (zl["peak"] for zl, _ in zone_load_eflh_pairs), ZERO.POWER
    )

    if total_area != ZERO.AREA:

        weighted_terms = []
        for zl, eflh in zone_load_eflh_pairs:
            # FIX: force consistent units before stripping magnitude
            area_frac = zl["area"].to(total_area.units).magnitude / total_area.magnitude
            contribution = eflh * area_frac
            weighted_terms.append(contribution)

        avg_internal_load_area = total_load / total_area
        avg_eflh = sum(weighted_terms)

    else:
        avg_internal_load_area = ZERO.POWER_PER_AREA
        avg_eflh = 0.0

    load_diff = abs(zone_load_per_area - avg_internal_load_area)
    eflh_diff = abs(zone_eflh - avg_eflh)

    if computer_room_zones_dict is None:
        computer_room_zones_dict = get_zone_computer_rooms(rmd)

    meets = (
        system_matched
        and (load_diff > LOAD_THRESHOLD or eflh_diff > EFLH_THRESHOLD)
        and zone["id"] not in computer_room_zones_dict
    )

    return G311CDiagnostics(
        meets=meets,
        zone_load_per_area=zone_load_per_area,
        avg_internal_load_area=avg_internal_load_area,
        zone_eflh=zone_eflh,
        avg_eflh=avg_eflh,
        load_diff=load_diff,
        eflh_diff=eflh_diff,
        load_diff_threshold=LOAD_THRESHOLD,
        eflh_diff_threshold=EFLH_THRESHOLD,
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
