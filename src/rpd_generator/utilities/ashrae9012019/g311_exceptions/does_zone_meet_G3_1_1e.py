from typing import TypedDict
from pydash import filter_, flat_map
from rpd_generator.config import Config
from rpd_generator.schema.schema_utils import get_q

ureg = Config.ureg
from rpd_generator.utilities.pint_utils import ZERO

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
    return sum((get_q(s, "floor_area", ZERO.AREA) for s in spaces), ZERO.AREA)


def is_zone_likely_a_vestibule(
    rmd: dict,
    zone: dict,
    zones_by_floor_map: dict[str, list[dict]] | None = None,
    zone_map: dict[str, dict] | None = None,
) -> bool:
    spaces = get_zone_spaces(zone)

    if not all(is_vestibule_space_type(s) for s in spaces):
        return False

    surfaces = zone.get("surfaces", [])
    exterior_surfaces = filter_(surfaces, {"adjacent_to": SurfaceAdjacency.EXTERIOR})

    exterior_doors = filter_(
        flat_map(exterior_surfaces, lambda surf: surf.get("subsurfaces", [])),
        {"classification": SubsurfaceClassification.DOOR},
    )

    exterior_door_area = (
        sum(
            (
                get_q(door, "glazed_area", ZERO.AREA)
                + get_q(door, "opaque_area", ZERO.AREA)
            )
            for door in exterior_doors
        )
        or ZERO.AREA
    )

    if exterior_door_area <= ZERO.AREA:
        return False

    zone_area = sum_floor_area(spaces)

    if zones_by_floor_map is not None:
        floor_name = zone.get("floor_name")
        zones_same_floor = zones_by_floor_map.get(floor_name, [])
    else:
        zones_same_floor = get_zones_on_same_floor_list(rmd, zone)

    if zone_map is None:
        zone_map = {
            z["id"]: z
            for b in rmd.get("buildings", [])
            for seg in b.get("building_segments", [])
            for z in seg.get("zones", [])
        }

    # Ensure we use the actual zone objects from the map/input
    spaces_same_floor = flat_map(
        zones_same_floor, lambda zn: get_zone_spaces(zone_map.get(zn["id"], zn))
    )
    floor_area = sum_floor_area(spaces_same_floor)

    threshold = max(
        VESTIBULE_AREA_THRESHOLD,
        VESTIBULE_AREA_MULTIPLIER_THRESHOLD * floor_area,
    )

    return zone_area <= threshold


def get_g3_1_1e_diagnostics(
    rmd_b: dict,
    rmd_p: dict,
    zone_b: dict,
    zone_p: dict,
    zones_by_floor_map_b: dict[str, list[dict]] | None = None,
    zone_map_b: dict[str, dict] | None = None,
    hvac_systems_map_p: dict[str, dict] | None = None,
) -> G311EDiagnostics:
    spaces_b = get_zone_spaces(zone_b)

    all_spaces_exception_e = all(is_exception_space_type(s) for s in spaces_b)
    vestibule_flag = is_zone_likely_a_vestibule(
        rmd_b, zone_b, zones_by_floor_map=zones_by_floor_map_b, zone_map=zone_map_b
    )
    mech_heat_only_flag = is_zone_mechanically_heated_and_not_cooled(
        rmd_p, zone_p, hvac_systems_map=hvac_systems_map_p
    )

    meets = (all_spaces_exception_e or vestibule_flag) and mech_heat_only_flag

    return G311EDiagnostics(
        meets=meets,
        all_spaces_exception_E=all_spaces_exception_e,
        is_zone_likely_a_vestibule=vestibule_flag,
        is_zone_mechanically_heated_and_not_cooled=mech_heat_only_flag,
    )


def does_zone_meet_g3_1_1e(rmd_b: dict, rmd_p: dict, zone: dict) -> bool:
    diag = get_g3_1_1e_diagnostics(rmd_b, rmd_p, zone, zone)
    return diag["meets"]
