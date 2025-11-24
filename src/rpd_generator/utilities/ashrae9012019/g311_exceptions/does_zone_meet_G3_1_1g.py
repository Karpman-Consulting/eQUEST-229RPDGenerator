from typing import TypedDict
from pint import Quantity

from rpd_generator.utilities.ashrae9012019.g311_exceptions.g311_sub_functions.get_computer_zones_peak_cooling_load import (
    get_computer_zones_peak_cooling_load,
)
from rpd_generator.utilities.ashrae9012019.g311_exceptions.g311_sub_functions.get_zones_computer_rooms import (
    get_zone_computer_rooms,
)
from rpd_generator.utilities.pint_utils import ZERO

from rct229.schema.config import ureg

COMPUTER_ZONE_PEAK_COOLING_LOAD_THRESHOLD = 600_000 * ureg("Btu/hr")


class G311GDiagnostics(TypedDict):
    meets: bool
    total_computer_zones_peak_cooling_load: Quantity
    is_computer_room_zone: bool


def get_g3_1_1g_diagnostics(
    rmd: dict,
    zone: dict,
    total_computer_peak_cooling_load: Quantity | None = None,
) -> G311GDiagnostics:
    computer_room_zones_dict = get_zone_computer_rooms(rmd)

    if total_computer_peak_cooling_load is None:
        total_computer_peak_cooling_load = get_computer_zones_peak_cooling_load(rmd)

    is_computer_zone = zone["id"] in computer_room_zones_dict
    meets = (
        is_computer_zone
        and total_computer_peak_cooling_load > COMPUTER_ZONE_PEAK_COOLING_LOAD_THRESHOLD
    )

    return G311GDiagnostics(
        meets=meets,
        total_computer_zones_peak_cooling_load=total_computer_peak_cooling_load,
        is_computer_room_zone=is_computer_zone,
    )


def does_zone_meet_g3_1_1g(rmd: dict, zone: dict) -> bool:
    diag = get_g3_1_1g_diagnostics(rmd, zone)
    return diag["meets"]
