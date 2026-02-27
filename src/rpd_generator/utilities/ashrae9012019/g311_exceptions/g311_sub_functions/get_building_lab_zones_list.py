from rpd_generator.schema.schema_enums import SchemaEnums

SpaceFunctionOptions = SchemaEnums.schema_enums["SpaceFunctionOptions"]
LightingSpaceOptions = SchemaEnums.schema_enums["LightingSpaceOptions2019ASHRAE901TG37"]


def get_building_lab_zones_list(rmd: dict) -> list[dict]:
    """
    returns a list of all the zones in the building that include a laboratory space

    Parameters
    ----------
    rmd: dict
        A dictionary representing a ruleset model description as defined by the ASHRAE229 schema

    Returns
    -------
    a list of zones for all zones that have a laboratory space in the building
    """
    laboratory_zone_list = []
    zones = [
        zone
        for b in rmd.get("buildings", [])
        for seg in b.get("building_segments", [])
        for zone in seg.get("zones", [])
    ]
    for zone in zones:
        if any(
            [
                space.get("function") == SpaceFunctionOptions.LABORATORY
                and space.get("lighting_space_type") is None
                or space.get("function") is None
                and space.get("lighting_space_type")
                == LightingSpaceOptions.LABORATORY_EXCEPT_IN_OR_AS_A_CLASSROOM
                or space.get("function") == SpaceFunctionOptions.LABORATORY
                and LightingSpaceOptions.LABORATORY_EXCEPT_IN_OR_AS_A_CLASSROOM
                for space in zone.get("spaces", [])
            ]
        ):
            laboratory_zone_list.append(zone)

    return laboratory_zone_list
