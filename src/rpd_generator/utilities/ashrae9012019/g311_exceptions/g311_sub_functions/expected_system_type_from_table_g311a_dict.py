import pydash
from typing import Literal
from pint import Quantity
from rct229.schema.config import ureg

from rpd_generator.utilities.ashrae9012019.baseline_systems.baseline_system_util import (
    HVAC_SYS,
)
from rpd_generator.utilities.ashrae9012019.is_cz_0_to_3a_bool import (
    is_cz_0_to_3a_bool,
)
from rpd_generator.schema.schema_enums import SchemaEnums


PUBLIC_ASSEMBLY_BUILDING_AREA_THRESHOLD = 120_000 * ureg("ft2")
RETAIL_FLOOR_NUMBER_THRESHOLD = 3
HOSPITAL_BUILDING_AREA_THRESHOLD = 150_000 * ureg("ft2")
HOSPITAL_FLOOR_NUMBER_THRESHOLD = 5
OTHER_NON_RESIDENTIAL_BUILDING_AREA_LOWER_THRESHOLD = 25_000 * ureg("ft2")
OTHER_NON_RESIDENTIAL_BUILDING_AREA_HIGHER_THRESHOLD = 150_000 * ureg("ft2")
OTHER_NON_RESIDENTIAL_FLOOR_NUMBER_LOWER_THRESHOLD = 4
OTHER_NON_RESIDENTIAL_FLOOR_NUMBER_HIGHER_THRESHOLD = 5
HVAC_BUILDING_AREA_TYPE_OPTIONS = SchemaEnums.schema_enums[
    "HeatingVentilatingAirConditioningBuildingAreaOptions2019ASHRAE901"
]

# True message, false message, condition
message_currier = pydash.curry(
    lambda condition, true_input, false_input: true_input if condition else false_input
)


def expected_system_type_from_table_g3_1_1_dict(
    building_area_type: str,
    climate_zone: str,
    number_of_floors: int,
    building_area: Quantity,
) -> dict[Literal["expected_system_type", "system_origin"], str]:

    is_cz_0_to_3a_flag = is_cz_0_to_3a_bool(climate_zone)
    climate_zone_currier = message_currier(is_cz_0_to_3a_flag)

    # Initialize pieces
    building_area_string = ""
    number_of_floors_string = ""
    expected_system_type = ""
    climate_zone_category = climate_zone_currier("CZ 0-3A", "CZ 3B,C or 4-8")

    # -------------------------------------------------------------------------
    # RETAIL
    # -------------------------------------------------------------------------
    if building_area_type == HVAC_BUILDING_AREA_TYPE_OPTIONS.RETAIL:
        if number_of_floors >= RETAIL_FLOOR_NUMBER_THRESHOLD:
            building_area_type = HVAC_BUILDING_AREA_TYPE_OPTIONS.OTHER_NON_RESIDENTIAL
        else:
            number_of_floors_string = message_currier(
                number_of_floors < RETAIL_FLOOR_NUMBER_THRESHOLD, "1–2 floors", ""
            )
            expected_system_type = climate_zone_currier(HVAC_SYS.SYS_4, HVAC_SYS.SYS_3)

    # -------------------------------------------------------------------------
    # RESIDENTIAL
    # -------------------------------------------------------------------------
    if building_area_type == HVAC_BUILDING_AREA_TYPE_OPTIONS.RESIDENTIAL:
        expected_system_type = climate_zone_currier(HVAC_SYS.SYS_2, HVAC_SYS.SYS_1)

    # -------------------------------------------------------------------------
    # PUBLIC ASSEMBLY
    # -------------------------------------------------------------------------
    if building_area_type == HVAC_BUILDING_AREA_TYPE_OPTIONS.PUBLIC_ASSEMBLY:
        pa_cur = message_currier(
            building_area < PUBLIC_ASSEMBLY_BUILDING_AREA_THRESHOLD
        )

        building_area_string = pa_cur("<120,000 ft²", "≥120,000 ft²")

        expected_system_type = pa_cur(
            climate_zone_currier(HVAC_SYS.SYS_4, HVAC_SYS.SYS_3),
            climate_zone_currier(HVAC_SYS.SYS_13, HVAC_SYS.SYS_12),
        )

    # -------------------------------------------------------------------------
    # HEATED-ONLY STORAGE
    # -------------------------------------------------------------------------
    if building_area_type == HVAC_BUILDING_AREA_TYPE_OPTIONS.HEATED_ONLY_STORAGE:
        expected_system_type = climate_zone_currier(HVAC_SYS.SYS_10, HVAC_SYS.SYS_9)

    # -------------------------------------------------------------------------
    # HOSPITAL
    # -------------------------------------------------------------------------
    if building_area_type == HVAC_BUILDING_AREA_TYPE_OPTIONS.HOSPITAL:
        climate_zone_category = ""  # Hospitals ignore CZ

        hosp_cur = message_currier(
            building_area > HOSPITAL_BUILDING_AREA_THRESHOLD
            or number_of_floors > HOSPITAL_FLOOR_NUMBER_THRESHOLD
        )

        building_area_string = hosp_cur(">150,000 ft² or >5 floors", "All Other")

        expected_system_type = hosp_cur(HVAC_SYS.SYS_7, HVAC_SYS.SYS_5)

    # -------------------------------------------------------------------------
    # OTHER NON-RESIDENTIAL
    # -------------------------------------------------------------------------
    if building_area_type == HVAC_BUILDING_AREA_TYPE_OPTIONS.OTHER_NON_RESIDENTIAL:

        # Flags
        low_area_flag = (
            building_area < OTHER_NON_RESIDENTIAL_BUILDING_AREA_LOWER_THRESHOLD
        )
        med_area_flag = (
            OTHER_NON_RESIDENTIAL_BUILDING_AREA_LOWER_THRESHOLD
            <= building_area
            <= OTHER_NON_RESIDENTIAL_BUILDING_AREA_HIGHER_THRESHOLD
        )
        large_area_flag = (
            building_area > OTHER_NON_RESIDENTIAL_BUILDING_AREA_HIGHER_THRESHOLD
        )
        low_floors = (
            number_of_floors < OTHER_NON_RESIDENTIAL_FLOOR_NUMBER_LOWER_THRESHOLD
        )
        med_floors = (
            number_of_floors <= OTHER_NON_RESIDENTIAL_FLOOR_NUMBER_HIGHER_THRESHOLD
        )
        high_floors = (
            number_of_floors > OTHER_NON_RESIDENTIAL_FLOOR_NUMBER_HIGHER_THRESHOLD
        )

        if low_area_flag:
            building_area_string = "<25,000 ft²"
            if low_floors:
                number_of_floors_string = "3 floors or fewer"
                expected_system_type = climate_zone_currier(
                    HVAC_SYS.SYS_4, HVAC_SYS.SYS_3
                )
            elif med_floors:
                number_of_floors_string = "4–5 floors"
                expected_system_type = climate_zone_currier(
                    HVAC_SYS.SYS_6, HVAC_SYS.SYS_5
                )

        elif med_area_flag and med_floors:
            building_area_string = "25,000–150,000 ft²"
            number_of_floors_string = "<6 floors"
            expected_system_type = climate_zone_currier(HVAC_SYS.SYS_6, HVAC_SYS.SYS_5)

        elif large_area_flag or high_floors:
            building_area_string = ">150,000 ft² or >5 floors"
            expected_system_type = climate_zone_currier(HVAC_SYS.SYS_8, HVAC_SYS.SYS_7)

    formatted_parts = list(
        filter(
            None,
            [
                building_area_type,
                climate_zone_category,
                building_area_string,
                number_of_floors_string,
            ],
        )
    )

    # Join with semicolons for readability
    system_origin = "; ".join(formatted_parts)

    return {
        "expected_system_type": expected_system_type,
        "system_origin": system_origin,
    }
