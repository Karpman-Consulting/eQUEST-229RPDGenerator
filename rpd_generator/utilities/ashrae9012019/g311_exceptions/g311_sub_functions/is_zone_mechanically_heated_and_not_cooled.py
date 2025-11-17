from pydash import flat_map
from rpd_generator.utilities.ashrae9012019.g311_exceptions.g311_sub_functions.is_zone_mechanically_cooled import (
    is_zone_mechanically_cooled,
)
from rpd_generator.utilities.get_list_hvac_systems_associated_with_zone import (
    get_list_hvac_systems_associated_with_zone,
)
from rpd_generator.schema.schema_enums import SchemaEnums

HeatingSystemOptions = SchemaEnums.schema_enums["HeatingSystemOptions"]
HeatingSourceOptions = SchemaEnums.schema_enums["HeatingSourceOptions"]


def is_zone_mechanically_heated_and_not_cooled(rmd: dict, zone: dict) -> bool:
    """
    Determines whether a zone is mechanically heated, but not cooled. Checks for transfer air

    Parameters
    ----------
    rmd: dict
        A dictionary representing a ruleset model description as defined by the ASHRAE229 schema
    zone: dict
        A dictionary representing a zone data group as defined by the ASHRAE229 schema

    Returns
    -------
    Boolean True if it is determined to be heated, but not cooled, False otherwise.
    """
    list_hvac_systems = get_list_hvac_systems_associated_with_zone(rmd, zone)

    def does_hvac_has_heating_sys(hvac: dict) -> bool:
        heating_type = hvac.get("heating_system", {}).get("type")
        return heating_type not in [None, HeatingSourceOptions.NONE]

    def does_zone_terminals_have_heating_type(zn: dict) -> bool:
        terminal_list = zn.get("terminals", [])
        return any(
            [
                terminal.get("heating_source") not in [None, HeatingSourceOptions.NONE]
                for terminal in terminal_list
            ]
        )

    is_heated = any(
        flat_map(
            list_hvac_systems,
            lambda hvac_system: does_hvac_has_heating_sys(hvac_system),
        )
    ) or does_zone_terminals_have_heating_type(zone)

    # Check if a zone is mechanically cooled
    is_cooled = is_zone_mechanically_cooled(rmd, zone)

    return is_heated and not is_cooled
