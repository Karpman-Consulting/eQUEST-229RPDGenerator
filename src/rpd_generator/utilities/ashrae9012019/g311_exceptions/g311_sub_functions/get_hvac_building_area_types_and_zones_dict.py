import logging
from typing import TypedDict
from pydash import curry
from pint import Quantity
from rpd_generator.utilities.pint_utils import ZERO

from rpd_generator.utilities.ashrae9012019.data_fns.table_lighting_to_hvac_bat_map_fns import (
    building_lighting_to_hvac_bat,
    space_lighting_to_hvac_bat,
)
from rpd_generator.utilities.ashrae9012019.get_zone_conditioning_category_dict import (
    ZoneConditioningCategory,
    get_zone_conditioning_category_rmd_dict,
)
from rpd_generator.schema.schema_enums import SchemaEnums

OTHER_UNDETERMINED = "OTHER_UNDETERMINED"
HVAC_BUILDING_AREA_TYPE_OPTIONS = SchemaEnums.schema_enums[
    "HeatingVentilatingAirConditioningBuildingAreaOptions2019ASHRAE901"
]


class ClassificationSource:
    BUILDING_SEGMENT_HVAC_BAT = "BUILDING_SEGMENT_HVAC_BAT"
    BUILDING_SEGMENT_LIGHTING = "BUILDING_SEGMENT_LIGHTING"
    SPACE_LIGHTING = "SPACE_LIGHTING"


logger = logging.getLogger(__name__)

# create currier that merges two building area type values
bat_val_merge_curry = curry(
    lambda a, b: {
        "zone_ids": [*a["zone_ids"], *b["zone_ids"]],
        "floor_area": a["floor_area"] + b["floor_area"],
    }
)
# create currier that retrieves a data form a dictionary with
# default handling of non-existence errors.
get_bat_val_func_curry = curry(
    lambda bat_dict, key: bat_dict.get(key, {"zone_ids": [], "floor_area": ZERO.AREA})
)


class BuildingAreaTypesWithTotalAreaZones(TypedDict):
    floor_area: Quantity
    zone_ids: list[str]


def get_hvac_building_area_types_and_zones_dict(
    climate_zone: str, rmd: dict
) -> dict[str, BuildingAreaTypesWithTotalAreaZones]:

    zone_conditioning_category_dict = get_zone_conditioning_category_rmd_dict(
        climate_zone, rmd
    )

    building_area_types_with_total_area_and_zones_dict = {}

    def get_bat_val(key):
        return building_area_types_with_total_area_and_zones_dict.get(
            key, {"zone_ids": [], "floor_area": ZERO.AREA}
        )

    def merge_bat_val(a, b):
        return {
            "zone_ids": a["zone_ids"] + b["zone_ids"],
            "floor_area": a["floor_area"] + b["floor_area"],
        }

    # -----------------------------
    # Iterate building segments
    # -----------------------------
    for building in rmd.get("buildings", []):
        for building_segment in building.get("building_segments", []):

            # -----------------------------
            # Determine HVAC BAT
            # -----------------------------
            if building_segment.get(
                "area_type_heating_ventilating_air_conditioning_system"
            ):
                building_segment_hvac_bat = building_segment[
                    "area_type_heating_ventilating_air_conditioning_system"
                ]
                classification_source = ClassificationSource.BUILDING_SEGMENT_HVAC_BAT

            elif building_segment.get("lighting_building_area_type"):
                building_segment_hvac_bat = building_lighting_to_hvac_bat(
                    building_segment["lighting_building_area_type"]
                )
                classification_source = ClassificationSource.BUILDING_SEGMENT_LIGHTING

            else:
                space_area_by_type = {}
                for zone in building_segment.get("zones", []):
                    for space in zone.get("spaces", []):
                        space_type = space.get("lighting_space_type")
                        if space_type:
                            space_area_by_type[space_type] = space_area_by_type.get(
                                space_type, ZERO.AREA
                            ) + space.get("floor_area", ZERO.AREA)

                assert space_area_by_type, (
                    f"Failed to determine hvac area type for building segment: "
                    f"{building_segment['id']}. Verify the model inputs."
                )

                dominant_space_type = max(
                    space_area_by_type, key=space_area_by_type.get
                )

                building_segment_hvac_bat = space_lighting_to_hvac_bat(
                    dominant_space_type
                )
                classification_source = ClassificationSource.SPACE_LIGHTING

            logger.info(
                f"building segment {building_segment['id']} is determined as "
                f"{building_segment_hvac_bat}. "
                f"The classification source is {classification_source}"
            )

            # -----------------------------
            # Filter conditioned zones
            # -----------------------------
            conditioned_zones = []
            total_floor_area = ZERO.AREA

            for zone in building_segment.get("zones", []):
                zone_id = zone["id"]
                if zone_conditioning_category_dict.get(zone_id) in {
                    ZoneConditioningCategory.CONDITIONED_MIXED,
                    ZoneConditioningCategory.CONDITIONED_NON_RESIDENTIAL,
                    ZoneConditioningCategory.CONDITIONED_RESIDENTIAL,
                }:
                    conditioned_zones.append(zone_id)
                    for space in zone.get("spaces", []):
                        total_floor_area += space.get("floor_area", ZERO.AREA)

            if not conditioned_zones:
                continue

            # -----------------------------
            # Merge results
            # -----------------------------
            existing = get_bat_val(building_segment_hvac_bat)
            merged = merge_bat_val(
                existing,
                {
                    "zone_ids": conditioned_zones,
                    "floor_area": total_floor_area,
                },
            )
            building_area_types_with_total_area_and_zones_dict[
                building_segment_hvac_bat
            ] = merged

    # -----------------------------
    # Handle OTHER_UNDETERMINED
    # -----------------------------
    if OTHER_UNDETERMINED in building_area_types_with_total_area_and_zones_dict:
        predominate_hvac_bat = max(
            building_area_types_with_total_area_and_zones_dict.items(),
            key=lambda x: x[1]["floor_area"],
        )[0]

        other_val = building_area_types_with_total_area_and_zones_dict.pop(
            OTHER_UNDETERMINED
        )

        def assign(key):
            return merge_bat_val(get_bat_val(key), other_val)

        if (
            predominate_hvac_bat == OTHER_UNDETERMINED
            or predominate_hvac_bat == HVAC_BUILDING_AREA_TYPE_OPTIONS.RESIDENTIAL
        ):
            building_area_types_with_total_area_and_zones_dict[
                HVAC_BUILDING_AREA_TYPE_OPTIONS.OTHER_NON_RESIDENTIAL
            ] = assign(HVAC_BUILDING_AREA_TYPE_OPTIONS.OTHER_NON_RESIDENTIAL)
        else:
            building_area_types_with_total_area_and_zones_dict[
                predominate_hvac_bat
            ] = assign(predominate_hvac_bat)

    assert building_area_types_with_total_area_and_zones_dict, (
        "No building area is found in the model. "
        "Please make sure there are building_segments data group in the model"
    )

    return building_area_types_with_total_area_and_zones_dict
