from typing import TypedDict
from pydash import filter_, flat_map
from rct229.schema.config import ureg
from rct229.utils.pint_utils import ZERO

from rpd_generator.utilities.ashrae9012019.g311_exceptions.g311_sub_functions.get_zones_on_same_floor_list import (
    get_zones_on_same_floor_list,
)
from rpd_generator.utilities.ashrae9012019.g311_exceptions.g311_sub_functions.is_zone_mechanically_heated_and_not_cooled import (
    is_zone_mechanically_heated_and_not_cooled,
)
from rpd_generator.schema.schema_enums import SchemaEnums
from rpd_generator.utilities.jsonpath_utils import find_all

LightingSpaceOptions = SchemaEnums.schema_enums["LightingSpaceOptions2019ASHRAE901TG37"]
SurfaceAdjacency = SchemaEnums.schema_enums["SurfaceAdjacencyOptions"]
SubsurfaceClassification = SchemaEnums.schema_enums["SubsurfaceClassificationOptions"]

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

EXCEPTION_E_SPACE_TYPES = [
    LightingSpaceOptions.STORAGE_ROOM_HOSPITAL,
    LightingSpaceOptions.STORAGE_ROOM_SMALL,
    LightingSpaceOptions.STORAGE_ROOM_LARGE,
    LightingSpaceOptions.WAREHOUSE_STORAGE_AREA_MEDIUM_TO_BULKY_PALLETIZED_ITEMS,
    LightingSpaceOptions.WAREHOUSE_STORAGE_AREA_SMALLER_HAND_CARRIED_ITEMS,
    LightingSpaceOptions.STAIRWELL,
    LightingSpaceOptions.ELECTRICAL_MECHANICAL_ROOM,
    LightingSpaceOptions.RESTROOM_FACILITY_FOR_THE_VISUALLY_IMPAIRED,
    LightingSpaceOptions.RESTROOM_ALL_OTHERS,
]

VESTIBULE_LIGHTING_SPACE_TYPES = [
    LightingSpaceOptions.CORRIDOR_FACILITY_FOR_THE_VISUALLY_IMPAIRED,
    LightingSpaceOptions.CORRIDOR_HOSPITAL,
    LightingSpaceOptions.CORRIDOR_ALL_OTHERS,
    LightingSpaceOptions.LOBBY_FACILITY_FOR_THE_VISUALLY_IMPAIRED,
    LightingSpaceOptions.LOBBY_HOTEL,
    LightingSpaceOptions.LOBBY_MOTION_PICTURE_THEATER,
    LightingSpaceOptions.LOBBY_PERFORMING_ARTS_THEATER,
    LightingSpaceOptions.LOBBY_ALL_OTHERS,
    LightingSpaceOptions.STAIRWELL,
]

VESTIBULE_AREA_THRESHOLD = 50 * ureg("ft2")
VESTIBULE_AREA_MULTIPLIER_THRESHOLD = 0.2


class G311EDiagnostics(TypedDict):
    meets: bool
    all_spaces_exception_E: bool
    is_zone_likely_a_vestibule: bool
    is_zone_mechanically_heated_and_not_cooled: bool


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def get_zone_spaces(zone):
    return find_all("$.spaces[*]", zone)


def is_exception_space_type(space):
    return space.get("lighting_space_type") in EXCEPTION_E_SPACE_TYPES


def is_vestibule_space_type(space):
    lst = space.get("lighting_space_type")
    return lst is None or lst in VESTIBULE_LIGHTING_SPACE_TYPES


def sum_floor_area(spaces):
    return sum((s.get("floor_area", ZERO.AREA) for s in spaces), ZERO.AREA)


def is_zone_likely_a_vestibule(rmd: dict, zone: dict) -> bool:
    spaces = get_zone_spaces(zone)

    if not all(is_vestibule_space_type(s) for s in spaces):
        return False

    surfaces = find_all("$.surfaces[*]", zone)
    exterior_surfaces = filter_(surfaces, {"adjacent_to": SurfaceAdjacency.EXTERIOR})

    exterior_doors = filter_(
        flat_map(exterior_surfaces, lambda surf: find_all("$.subsurfaces[*]", surf)),
        {"classification": SubsurfaceClassification.DOOR},
    )

    exterior_door_area = (
        sum(
            (door.get("glazed_area", ZERO.AREA) + door.get("opaque_area", ZERO.AREA))
            for door in exterior_doors
        )
        or ZERO.AREA
    )

    if exterior_door_area <= ZERO.AREA:
        return False

    zone_area = sum_floor_area(spaces)

    zones_same_floor = get_zones_on_same_floor_list(rmd, zone)
    zone_map = {
        z["id"]: z
        for z in find_all("$.buildings[*].building_segments[*].zones[*]", rmd)
    }

    spaces_same_floor = flat_map(
        zones_same_floor, lambda zn: get_zone_spaces(zone_map[zn["id"]])
    )
    floor_area = sum_floor_area(spaces_same_floor)

    threshold = max(
        VESTIBULE_AREA_THRESHOLD,
        VESTIBULE_AREA_MULTIPLIER_THRESHOLD * floor_area,
    )

    return zone_area <= threshold


def get_g3_1_1e_diagnostics(rmd_b: dict, rmd_p: dict, zone: dict) -> G311EDiagnostics:
    spaces = get_zone_spaces(zone)

    all_spaces_exception_e = all(is_exception_space_type(s) for s in spaces)
    vestibule_flag = is_zone_likely_a_vestibule(rmd_b, zone)
    mech_heat_only_flag = is_zone_mechanically_heated_and_not_cooled(rmd_p, zone)

    meets = (all_spaces_exception_e or vestibule_flag) and mech_heat_only_flag

    return G311EDiagnostics(
        meets=meets,
        all_spaces_exception_E=all_spaces_exception_e,
        is_zone_likely_a_vestibule=vestibule_flag,
        is_zone_mechanically_heated_and_not_cooled=mech_heat_only_flag,
    )


def does_zone_meet_g3_1_1e(rmd_b: dict, rmd_p: dict, zone: dict) -> bool:
    diag = get_g3_1_1e_diagnostics(rmd_b, rmd_p, zone)
    return diag["meets"]
