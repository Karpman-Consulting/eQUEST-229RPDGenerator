from typing import TypedDict, NotRequired
from pydash import juxtapose

from rpd_generator.utilities.ashrae9012019.baseline_systems.baseline_system_util import (
    HVAC_SYS,
)
from rpd_generator.utilities.ashrae9012019.g311_exceptions.does_zone_meet_G3_1_1c import (
    get_g3_1_1c_diagnostics,
)
from rpd_generator.utilities.ashrae9012019.g311_exceptions.does_zone_meet_G3_1_1d import (
    get_g3_1_1d_diagnostics,
)
from rpd_generator.utilities.ashrae9012019.g311_exceptions.does_zone_meet_G3_1_1e import (
    get_g3_1_1e_diagnostics,
)
from rpd_generator.utilities.ashrae9012019.g311_exceptions.does_zone_meet_G3_1_1f import (
    get_g3_1_1f_diagnostics,
)
from rpd_generator.utilities.ashrae9012019.g311_exceptions.does_zone_meet_G3_1_1g import (
    get_g3_1_1g_diagnostics,
)
from rpd_generator.utilities.ashrae9012019.g311_exceptions.g311_sub_functions.expected_system_type_from_table_g311a_dict import (
    expected_system_type_from_table_g3_1_1_dict,
)
from rpd_generator.utilities.ashrae9012019.g311_exceptions.g311_sub_functions.get_computer_zones_peak_cooling_load import (
    get_computer_zones_peak_cooling_load,
)
from rpd_generator.utilities.ashrae9012019.g311_exceptions.g311_sub_functions.get_hvac_building_area_types_and_zones_dict import (
    get_hvac_building_area_types_and_zones_dict,
)
from rpd_generator.utilities.ashrae9012019.g311_exceptions.g311_sub_functions.get_number_of_floors import (
    get_number_of_floors,
)
from rpd_generator.utilities.ashrae9012019.g311_exceptions.g311_sub_functions.get_predominant_hvac_building_area_type import (
    get_predominant_hvac_building_area_type,
)
from rpd_generator.utilities.ashrae9012019.g311_exceptions.g311_sub_functions.get_zone_hvac_bat import (
    get_zone_hvac_bat_dict,
)
from rpd_generator.utilities.ashrae9012019.get_zone_conditioning_category_dict import (
    ZoneConditioningCategory as ZCC,
    get_zone_conditioning_category_rmd_dict,
)
from rpd_generator.utilities.ashrae9012019.is_cz_0_to_3a_bool import (
    is_cz_0_to_3a_bool,
)
from rpd_generator.utilities.jsonpath_utils import find_all

from rct229.schema.config import ureg

BUILDING_AREA_20000_ft2 = 20000 * ureg("ft2")
BUILDING_AREA_40000_ft2 = 40000 * ureg("ft2")
BUILDING_AREA_150000_ft2 = 150000 * ureg("ft2")
REQ_FL_6 = 6
COMPUTER_ROOM_PEAK_COOLING_LOAD_600000_BTUH = 600000 * ureg("Btu/hr")
COMPUTER_ROOM_PEAK_COOLING_LOAD_3000000_BTUH = 3000000 * ureg("Btu/hr")


class ZoneandSystem(TypedDict):
    expected_system_type: str
    system_origin: str
    debug: NotRequired[dict]


class SYSTEMORIGIN:
    G311_TABLE = "G3_1_1_table"
    G311B = "G3_1_1b"
    G311C = "G3_1_1c"
    G311D = "G3_1_1d"
    G311E = "G3_1_1e"
    G311F = "G3_1_1f"
    G311G_PART2 = "G3_1_1g_part2"
    G311G_PART3 = "G3_1_1g_part3"


def get_zone_target_baseline_system(
    rmd_b: dict, rmd_p: dict, climate_zone_b: str
) -> dict[str, ZoneandSystem]:
    """
    Following G3.1.1, determines the baseline system type for each zone in a building.
    Now includes a `debug` block per zone with detailed diagnostics for:
    - zone_conditioning_category
    - expected system from Table G3.1.1
    - each exception c–g (including all the values you listed).
    """

    zone_id_to_zone_b_map = {
        zone_b["id"]: zone_b
        for zone_b in find_all("$.buildings[*].building_segments[*].zones[*]", rmd_b)
    }
    zone_id_to_zone_p_map = {
        zone_p["id"]: zone_p
        for zone_p in find_all("$.buildings[*].building_segments[*].zones[*]", rmd_p)
    }
    zone_conditioning_category_dict = get_zone_conditioning_category_rmd_dict(
        climate_zone_b, rmd_b
    )

    (
        list_building_area_types_and_zones_b,
        predominant_building_area_type_b,
        num_floors_b,
    ) = juxtapose(
        lambda cz, rmd: get_hvac_building_area_types_and_zones_dict(cz, rmd),
        lambda cz, rmd: get_predominant_hvac_building_area_type(cz, rmd),
        lambda cz, rmd: get_number_of_floors(cz, rmd),
    )(
        climate_zone_b, rmd_b
    )

    floor_area_b = sum(
        [
            list_building_area_types_and_zones_b[bat]["floor_area"]
            for bat in list_building_area_types_and_zones_b
        ]
    )
    expected_system_type_dict_b = expected_system_type_from_table_g3_1_1_dict(
        predominant_building_area_type_b, climate_zone_b, num_floors_b, floor_area_b
    )

    # Precompute this once for diagnostics and G3.1.1g
    total_computer_zones_peak_cooling_load_b = get_computer_zones_peak_cooling_load(
        rmd_b
    )

    is_cz_0_to_3a_result_bool = is_cz_0_to_3a_bool(climate_zone_b)

    # zones_and_systems dictionary filters out unconditioned zones
    zones_and_systems_b: dict[str, ZoneandSystem] = {}

    # ----------------------------------------------------------------------
    # Base assignment from Table G3.1.1 (no exceptions)
    # ----------------------------------------------------------------------
    for zone_b in find_all("$.buildings[*].building_segments[*].zones[*]", rmd_b):
        zid = str(zone_b["id"])
        zcc = zone_conditioning_category_dict[zid]

        if zcc in (
            ZCC.CONDITIONED_RESIDENTIAL,
            ZCC.CONDITIONED_NON_RESIDENTIAL,
            ZCC.CONDITIONED_MIXED,
        ):
            zones_and_systems_b[zid] = ZoneandSystem(
                expected_system_type=expected_system_type_dict_b[
                    "expected_system_type"
                ],
                system_origin=SYSTEMORIGIN.G311_TABLE,
                debug={
                    "zone_conditioning_category": str(zcc),
                    "table_g3_1_1": {
                        "expected_system_type_from_table": expected_system_type_dict_b[
                            "expected_system_type"
                        ],
                        "system_origin_from_table": expected_system_type_dict_b[
                            "system_origin"
                        ],
                        "building_area_type": predominant_building_area_type_b.replace(
                            "_", " "
                        ).title(),
                        "num_floors": num_floors_b,
                        "floor_area": floor_area_b,
                    },
                    "exceptions": {
                        "g3_1_1b": {"applied": False},
                        "g3_1_1c": {},
                        "g3_1_1d": {},
                        "g3_1_1e": {},
                        "g3_1_1f": {},
                        "g3_1_1g": {},
                    },
                },
            )

    # ----------------------------------------------------------------------
    # G3.1.1b – Secondary building area types
    # ----------------------------------------------------------------------
    if floor_area_b > BUILDING_AREA_40000_ft2:
        for building_area_type in list_building_area_types_and_zones_b:
            if building_area_type != predominant_building_area_type_b and (
                list_building_area_types_and_zones_b[building_area_type]["floor_area"]
                >= BUILDING_AREA_20000_ft2
            ):
                secondary_system_type_b = expected_system_type_from_table_g3_1_1_dict(
                    building_area_type,
                    climate_zone_b,
                    num_floors_b,
                    floor_area_b,
                )
                for zone_id_b in zones_and_systems_b:
                    if (
                        zone_id_b
                        in list_building_area_types_and_zones_b[building_area_type][
                            "zone_ids"
                        ]
                    ):
                        zones_and_systems_b[zone_id_b]["expected_system_type"] = (
                            secondary_system_type_b["expected_system_type"]
                        )
                        zones_and_systems_b[zone_id_b][
                            "system_origin"
                        ] = SYSTEMORIGIN.G311B

                        debug = zones_and_systems_b[zone_id_b].setdefault("debug", {})
                        exc = debug.setdefault("exceptions", {})
                        exc["g3_1_1b"] = {
                            "applied": True,
                            "secondary_expected_system_type_from_table": secondary_system_type_b[
                                "expected_system_type"
                            ],
                            "secondary_system_origin_from_table": secondary_system_type_b[
                                "system_origin"
                            ],
                            "secondary_building_area_type": building_area_type,
                        }

    # ----------------------------------------------------------------------
    # Per-zone exceptions C through G
    # ----------------------------------------------------------------------
    for zone_id in zones_and_systems_b:
        zone_b = zone_id_to_zone_b_map[zone_id]
        zone_p = zone_id_to_zone_p_map[zone_id]
        zs_entry = zones_and_systems_b[zone_id]
        debug = zs_entry.setdefault("debug", {})
        exc_debug = debug.setdefault("exceptions", {})

        # -------------------------
        # G3.1.1c
        # -------------------------
        c_diag = get_g3_1_1c_diagnostics(rmd_b, zone_b, zones_and_systems_b)
        exc_debug["g3_1_1c"] = {
            "does_zone_meet_g3_1_1c": c_diag["meets"],
            "zone_internal_load_per_area": c_diag["zone_load_per_area"],
            "avg_internal_load_area": c_diag["avg_internal_load_area"],
            "zone_eflh": c_diag["zone_eflh"],
            "avg_eflh": c_diag["avg_eflh"],
            "load_diff": c_diag["load_diff"],
            "eflh_diff": c_diag["eflh_diff"],
        }

        if c_diag["meets"]:
            zs_entry["system_origin"] = SYSTEMORIGIN.G311C
            zs_entry["expected_system_type"] = (
                HVAC_SYS.SYS_4 if is_cz_0_to_3a_result_bool else HVAC_SYS.SYS_3
            )

        # -------------------------
        # G3.1.1d
        # -------------------------
        d_diag = get_g3_1_1d_diagnostics(rmd_b, zone_id)
        exc_debug["g3_1_1d"] = {
            "does_zone_meet_g3_1_1d": d_diag["meets"],
            "building_total_lab_exhaust": d_diag["building_total_lab_exhaust"],
            "zone_is_lab_zone": d_diag["is_lab_zone"],
        }

        if d_diag["meets"]:
            zs_entry["system_origin"] = SYSTEMORIGIN.G311D
            zs_entry["expected_system_type"] = (
                HVAC_SYS.SYS_5
                if num_floors_b < REQ_FL_6 and floor_area_b < BUILDING_AREA_150000_ft2
                else HVAC_SYS.SYS_7
            )

        # -------------------------
        # G3.1.1e
        # -------------------------
        e_diag = get_g3_1_1e_diagnostics(rmd_b, rmd_p, zone_p)
        exc_debug["g3_1_1e"] = {
            "does_zone_meet_g3_1_1e": e_diag["meets"],
            "all_spaces_exception_E": e_diag["all_spaces_exception_E"],
            "is_zone_likely_a_vestibule": e_diag["is_zone_likely_a_vestibule"],
            "is_zone_mechanically_heated_and_not_cooled": e_diag[
                "is_zone_mechanically_heated_and_not_cooled"
            ],
        }

        if e_diag["meets"]:
            zs_entry["system_origin"] = SYSTEMORIGIN.G311E
            zs_entry["expected_system_type"] = (
                HVAC_SYS.SYS_10 if is_cz_0_to_3a_result_bool else HVAC_SYS.SYS_9
            )

        # -------------------------
        # G3.1.1f
        # -------------------------
        f_diag = get_g3_1_1f_diagnostics(
            rmd_b, zone_b, zs_entry["expected_system_type"]
        )
        exc_debug["g3_1_1f"] = {
            "does_zone_meet_g3_1_1f": f_diag["meets"],
            "is_zone_mechanically_cooled": f_diag["is_zone_mechanically_cooled"],
            "is_system_type_9_or_10": f_diag["is_system_type_9_or_10"],
        }

        if f_diag["meets"] and zs_entry["expected_system_type"] in (
            HVAC_SYS.SYS_9,
            HVAC_SYS.SYS_10,
        ):
            zone_hvac_bat_dict_b = get_zone_hvac_bat_dict(zone_b)
            zs_entry["system_origin"] = SYSTEMORIGIN.G311F
            zs_entry["expected_system_type"] = (
                expected_system_type_from_table_g3_1_1_dict(
                    max(zone_hvac_bat_dict_b, key=zone_hvac_bat_dict_b.get),
                    climate_zone_b,
                    num_floors_b,
                    floor_area_b,
                )["expected_system_type"]
            )

        # -------------------------
        # G3.1.1g
        # -------------------------
        g_diag = get_g3_1_1g_diagnostics(
            rmd_b, zone_b, total_computer_zones_peak_cooling_load_b
        )
        exc_debug["g3_1_1g"] = {
            "does_zone_meet_g3_1_1g": g_diag["meets"],
            "total_computer_zones_peak_cooling_load_b": g_diag[
                "total_computer_zones_peak_cooling_load"
            ],
            "zone_is_computer_room_zone": g_diag["is_computer_room_zone"],
        }

        if g_diag["meets"]:
            if (
                total_computer_zones_peak_cooling_load_b
                > COMPUTER_ROOM_PEAK_COOLING_LOAD_3000000_BTUH
            ) or (
                zs_entry["expected_system_type"]
                in (
                    HVAC_SYS.SYS_7,
                    HVAC_SYS.SYS_8,
                )
            ):
                zs_entry["system_origin"] = SYSTEMORIGIN.G311G_PART2
                zs_entry["expected_system_type"] = HVAC_SYS.SYS_11_1
            else:
                zs_entry["system_origin"] = SYSTEMORIGIN.G311G_PART3
                zs_entry["expected_system_type"] = (
                    HVAC_SYS.SYS_4 if is_cz_0_to_3a_result_bool else HVAC_SYS.SYS_3
                )

    # ----------------------------------------------------------------------
    # Final debug: record final expected system and origin
    # ----------------------------------------------------------------------
    for zid, zs in zones_and_systems_b.items():
        debug = zs.get("debug")
        if isinstance(debug, dict):
            debug["final_expected_system_type"] = zs["expected_system_type"]
            debug["final_system_origin"] = zs["system_origin"]

    return zones_and_systems_b
