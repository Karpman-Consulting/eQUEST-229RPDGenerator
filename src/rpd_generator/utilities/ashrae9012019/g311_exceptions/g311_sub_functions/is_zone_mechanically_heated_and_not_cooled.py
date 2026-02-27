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


def is_zone_mechanically_heated_and_not_cooled(
    rmd: dict,
    zone: dict,
    hvac_systems_map: dict[str, dict] | None = None,
    zone_map: dict[str, dict] | None = None,
) -> bool:
    """
    Determines whether a zone is mechanically heated, but not cooled. Checks for transfer air
    """
    if hvac_systems_map is not None:
        hvac_ids_serving_zone = {
            t["served_by_heating_ventilating_air_conditioning_system"]
            for t in zone.get("terminals", [])
            if t.get("served_by_heating_ventilating_air_conditioning_system")
        }
        list_hvac_systems = [
            hvac_systems_map[hid]
            for hid in hvac_ids_serving_zone
            if hid in hvac_systems_map
        ]
    else:
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
        [does_hvac_has_heating_sys(hvac) for hvac in list_hvac_systems]
    ) or does_zone_terminals_have_heating_type(zone)

    # Check if a zone is mechanically cooled
    is_cooled = is_zone_mechanically_cooled(
        rmd, zone, hvac_systems_map=hvac_systems_map, zone_map=zone_map
    )

    return is_heated and not is_cooled
