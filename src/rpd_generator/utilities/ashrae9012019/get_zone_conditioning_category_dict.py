from typing import List, Dict

from rpd_generator.utilities.ashrae9012019.data_fns.table_3_2_fns import (
    table_3_2_lookup,
)
from rpd_generator.utilities.get_hvac_zone_list_w_area_dict import (
    get_hvac_zone_list_w_area_dict,
)
from rpd_generator.utilities.get_opaque_surface_type import (
    get_opaque_surface_type,
)
from rpd_generator.utilities.jsonpath_utils import find_all
from rpd_generator.utilities.pint_utils import ZERO
from rpd_generator.config import Config

ureg = Config.ureg

CAPACITY_THRESHOLD = 3.4 * ureg("Btu/(hr * ft2)")
CRAWLSPACE_HEIGHT_THRESHOLD = 7 * ureg("ft")


# Intended for export and internal use
class ZoneConditioningCategory:
    """Enumeration class for zone conditioning categories"""

    CONDITIONED_MIXED: str = "CONDITIONED MIXED"
    CONDITIONED_NON_RESIDENTIAL: str = "CONDITIONED NON-RESIDENTIAL"
    CONDITIONED_RESIDENTIAL: str = "CONDITIONED RESIDENTIAL"
    SEMI_HEATED: str = "SEMI-HEATED"
    UNCONDITIONED: str = "UNCONDITIONED"
    UNENCLOSED: str = "UNENCLOSED"


def get_zone_conditioning_category_rmd_dict(
    climate_zone: str, rmd: dict
) -> dict[str, ZoneConditioningCategory]:
    """
    Determines the zone conditioning category for every zone in an RMD.

    Parameters
    ----------
    climate_zone: str
        One of the ClimateZoneOptions2019ASHRAE901 enumerated values
    rmd: dict
        A dictionary representing a ruleset model description as defined by the ASHRAE229 schema
    Returns
    -------
    dict
        A dictionary that maps zones to one of the conditioning categories:
        CONDITIONED_MIXED, CONDITIONED_NON_RESIDENTIAL, CONDITIONED_RESIDENTIAL,
        SEMI_HEATED, UNCONDITIONED, UNENCOLOSED
    """
    zone_conditioning_category_rmd_dict = {}
    constructions = rmd.get("constructions", [])
    for building in find_all("$.buildings[*]", rmd):
        zone_conditioning_category_dict = get_zone_conditioning_category_dict(
            climate_zone, building, constructions
        )
        zone_conditioning_category_rmd_dict.update(zone_conditioning_category_dict)
    return zone_conditioning_category_rmd_dict


def get_zone_conditioning_category_dict(
    climate_zone: str, building: dict, constructions: list
) -> dict[str, ZoneConditioningCategory]:

    if constructions is None:
        constructions = []

    zone_conditioning_category_dict = {}

    # -----------------------------
    # Precompute / cache lookups
    # -----------------------------
    zones = list(find_all("$.building_segments[*].zones[*]", building))

    construction_by_id = {c["id"]: c for c in constructions}

    hvac_systems_dict = {
        hvac["id"]: hvac
        for hvac in find_all(
            "building_segments[*].heating_ventilating_air_conditioning_systems[*]",
            building,
        )
    }

    hvac_zone_list_w_area_dict = get_hvac_zone_list_w_area_dict(building)

    # -----------------------------
    # HVAC capacity per area
    # -----------------------------
    hvac_cool_capacity_dict = {}
    hvac_heat_capacity_dict = {}

    for hvac_id, hvac_values in hvac_zone_list_w_area_dict.items():
        hvac = hvac_systems_dict.get(hvac_id, {})

        cooling = hvac.get("cooling_system", {})
        heating = hvac.get("heating_system", {})
        preheat = hvac.get("preheat_system", {})

        hvac_cool_capacity_dict[hvac_id] = (
            cooling.get("design_sensible_cool_capacity", ZERO.POWER)
            / hvac_values["total_area"]
        )

        hvac_heat_capacity_dict[hvac_id] = (
            heating.get("design_capacity", ZERO.POWER)
            + preheat.get("design_capacity", ZERO.POWER)
        ) / hvac_values["total_area"]

    system_min_heating_output = table_3_2_lookup(climate_zone)[
        "system_min_heating_output"
    ]

    # -----------------------------
    # Zone capacities
    # -----------------------------
    zone_capacity_dict = {}

    for zone in zones:
        zone_id = zone["id"]
        spaces = zone.get("spaces", [])
        zone_area = sum((s.get("floor_area", ZERO.AREA) for s in spaces), ZERO.AREA)
        assert zone_area > ZERO.AREA, f"zone:{zone_id} has no floor area"

        zone_cap = {
            "sensible_cooling": ZERO.THERMAL_CAPACITY,
            "heating": ZERO.THERMAL_CAPACITY,
        }
        zone_capacity_dict[zone_id] = zone_cap

        for terminal in zone.get("terminals", []):
            hvac_id = terminal.get(
                "served_by_heating_ventilating_air_conditioning_system"
            )

            zone_cap["sensible_cooling"] += hvac_cool_capacity_dict.get(
                hvac_id, ZERO.THERMAL_CAPACITY
            )
            zone_cap["heating"] += (
                hvac_heat_capacity_dict.get(hvac_id, ZERO.THERMAL_CAPACITY)
                + terminal.get("heating_capacity", ZERO.POWER) / zone_area
            )

    # -----------------------------
    # Direct / semi-heated
    # -----------------------------
    directly_conditioned_zone_ids = set()
    semiheated_zone_ids = set()

    for zone in zones:
        zid = zone["id"]
        cap = zone_capacity_dict[zid]

        if (
            cap["sensible_cooling"] > CAPACITY_THRESHOLD
            or cap["heating"] >= system_min_heating_output
        ):
            directly_conditioned_zone_ids.add(zid)
        elif cap["heating"] >= CAPACITY_THRESHOLD:
            semiheated_zone_ids.add(zid)

    # -----------------------------
    # Indirectly conditioned
    # -----------------------------
    indirectly_conditioned_zone_ids = set()

    for zone in zones:
        zid = zone["id"]
        if zid in directly_conditioned_zone_ids:
            continue

        spaces = zone.get("spaces", [])
        lighting_types = {s.get("lighting_space_type") for s in spaces}

        if lighting_types & {"ATRIUM_LOW_MEDIUM", "ATRIUM_HIGH"}:
            indirectly_conditioned_zone_ids.add(zid)
            continue

        zone_direct_ua = ZERO.UA
        zone_other_ua = ZERO.UA

        for surface in zone.get("surfaces", []):
            subsurfaces = surface.get("subsurfaces", [])

            subsurf_area = sum(
                (
                    ss.get("glazed_area", ZERO.AREA) + ss.get("opaque_area", ZERO.AREA)
                    for ss in subsurfaces
                ),
                ZERO.AREA,
            )

            subsurf_ua = sum(
                (
                    ss["u_factor"]
                    * (
                        ss.get("glazed_area", ZERO.AREA)
                        + ss.get("opaque_area", ZERO.AREA)
                    )
                    for ss in subsurfaces
                ),
                ZERO.UA,
            )

            non_sub_area = surface["area"] - subsurf_area

            surface_construction = construction_by_id.get(surface["construction"], {})
            construction = surface_construction.get("construction", {})

            factor = next(
                (
                    construction[k]
                    for k in ("u_factor", "f_factor", "c_factor")
                    if k in construction
                ),
                None,
            )

            surface_ua = factor * non_sub_area + subsurf_ua if factor else ZERO.UA

            if (
                surface["adjacent_to"] == "INTERIOR"
                and surface.get("adjacent_zone") in directly_conditioned_zone_ids
            ):
                zone_direct_ua += surface_ua
            else:
                zone_other_ua += surface_ua

        if zone_direct_ua > zone_other_ua:
            indirectly_conditioned_zone_ids.add(zid)

    # -----------------------------
    # Final category assignment
    # -----------------------------
    for building_segment in find_all("building_segments[*]", building):
        seg_type = building_segment.get("lighting_building_area_type")

        seg_res = seg_type in {"DORMITORY", "HOTEL_MOTEL", "MULTIFAMILY"}
        seg_nonres = seg_type is not None and not seg_res

        for zone in building_segment.get("zones", []):
            zid = zone["id"]
            spaces = zone.get("spaces", [])

            if zid in directly_conditioned_zone_ids | indirectly_conditioned_zone_ids:
                res = False
                nonres = False

                for space in spaces:
                    lst = space.get("lighting_space_type")
                    if lst in {
                        "DORMITORY_LIVING_QUARTERS",
                        "FIRE_STATION_SLEEPING_QUARTERS",
                        "GUEST_ROOM",
                        "DWELLING_UNIT",
                        "HEALTHCARE_FACILITY_NURSERY",
                        "HEALTHCARE_FACILITY_PATIENT_ROOM",
                    }:
                        res = True
                    elif lst is not None:
                        nonres = True
                    elif seg_res:
                        res = True
                    else:
                        nonres = True

                if res and nonres:
                    zone_conditioning_category_dict[
                        zid
                    ] = ZoneConditioningCategory.CONDITIONED_MIXED
                elif res:
                    zone_conditioning_category_dict[
                        zid
                    ] = ZoneConditioningCategory.CONDITIONED_RESIDENTIAL
                else:
                    zone_conditioning_category_dict[
                        zid
                    ] = ZoneConditioningCategory.CONDITIONED_NON_RESIDENTIAL

            elif zid in semiheated_zone_ids:
                zone_conditioning_category_dict[
                    zid
                ] = ZoneConditioningCategory.SEMI_HEATED

            else:
                zone_volume = zone.get("volume", ZERO.VOLUME)
                assert zone_volume > ZERO.VOLUME, f"zone:{zid} has no volume"

                zone_floor_area = sum(
                    (s.get("floor_area", ZERO.AREA) for s in spaces), ZERO.AREA
                )
                assert zone_floor_area > ZERO.AREA, f"zone:{zid} has no floor area"

                # ---- Crawlspace
                if zone_volume / zone_floor_area < CRAWLSPACE_HEIGHT_THRESHOLD and any(
                    get_opaque_surface_type(
                        surface,
                        construction_by_id.get(surface["construction"], {}).get(
                            "has_radiant_heat"
                        ),
                    )
                    in ["HEATED SLAB-ON-GRADE", "UNHEATED SLAB-ON-GRADE"]
                    and surface["adjacent_to"] == "GROUND"
                    for surface in zone.get("surfaces", [])
                ):
                    zone_conditioning_category_dict[
                        zid
                    ] = ZoneConditioningCategory.UNENCLOSED

                # ---- Attic
                elif any(
                    get_opaque_surface_type(
                        surface,
                        construction_by_id.get(surface["construction"], {}).get(
                            "has_radiant_heat"
                        ),
                    )
                    == "ROOF"
                    and surface["adjacent_to"] == "EXTERIOR"
                    for surface in zone.get("surfaces", [])
                ):
                    zone_conditioning_category_dict[
                        zid
                    ] = ZoneConditioningCategory.UNENCLOSED

                else:
                    zone_conditioning_category_dict[
                        zid
                    ] = ZoneConditioningCategory.UNCONDITIONED

    return zone_conditioning_category_dict


def find_construction_by_surface(surface: dict, constructions: List[Dict]) -> dict:
    surface_construction_id = surface["construction"]
    surface_construction = next(
        (
            construction
            for construction in constructions
            if construction["id"] == surface_construction_id
        ),
        {},  # empty dict if not found, to allow constructions to be optional
    )
    return surface_construction
