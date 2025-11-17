from pydash import flat_map
from rpd_generator.utilities.get_list_hvac_systems_associated_with_zone import (
    get_list_hvac_systems_associated_with_zone,
)
from rpd_generator.schema.schema_enums import SchemaEnums
from rpd_generator.utilities.jsonpath_utils import find_all, find_one
from rpd_generator.utilities.pint_utils import ZERO

CoolingSystemOptions = SchemaEnums.schema_enums["CoolingSystemOptions"]
CoolingSourceOptions = SchemaEnums.schema_enums["CoolingSourceOptions"]


def is_zone_mechanically_cooled(rmd: dict, zone: dict) -> bool:
    """
    Function determines whether a zone is cooled. Checks for transfer air

    Parameters
    ----------
    rmd: dict
        A dictionary representing a ruleset model description as defined by the ASHRAE229 schema
    zone: dict
        A dictionary representing a zone as defined by the ASHRAE229 schema

    Returns
    -------
    Boolean True if it is determined to be cooled, False otherwise.
    """
    list_hvac_systems = get_list_hvac_systems_associated_with_zone(rmd, zone)
    zone_id_to_zone_map = {
        zn["id"]: zn
        for zn in find_all("$.buildings[*].building_segments[*].zones[*]", rmd)
    }

    def does_hvac_has_cooling_sys(hvac: dict) -> bool:
        cooling_type = find_one("$.cooling_system.type", hvac)
        return cooling_type not in [None, CoolingSourceOptions.NONE]

    def does_zone_terminals_have_cooling_type(zone_id: str) -> bool:
        terminal_list = find_all("$.terminals[*]", zone_id_to_zone_map[zone_id])
        return any(
            [
                find_one("$.cooling_source", terminal)
                not in [None, CoolingSourceOptions.NONE]
                for terminal in terminal_list
            ]
        )

    has_cooling_system = any(
        flat_map(
            list_hvac_systems,
            lambda hvac_system: does_hvac_has_cooling_sys(hvac_system),
        )
    ) or does_zone_terminals_have_cooling_type(zone["id"])

    if not has_cooling_system:
        if zone.get("transfer_airflow_rate", ZERO.FLOW) > ZERO.FLOW:
            # in this case, we are checking the source zone
            transfer_source_zone_id = zone["transfer_airflow_source_zone"]
            # get the HVAC system list from the source zone
            list_hvac_systems = get_list_hvac_systems_associated_with_zone(
                rmd, zone_id_to_zone_map[transfer_source_zone_id]
            )
            has_cooling_system = any(
                flat_map(
                    list_hvac_systems,
                    lambda hvac_system: does_hvac_has_cooling_sys(hvac_system),
                )
            ) or does_zone_terminals_have_cooling_type(transfer_source_zone_id)

    return has_cooling_system
