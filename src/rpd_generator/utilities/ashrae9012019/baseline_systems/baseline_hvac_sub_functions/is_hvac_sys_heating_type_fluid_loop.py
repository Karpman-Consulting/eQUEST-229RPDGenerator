from rpd_generator.schema.schema_enums import SchemaEnums

HEATING_SYSTEM = SchemaEnums.schema_enums["HeatingSystemOptions"]


def is_hvac_sys_heating_type_fluid_loop(hvac: dict) -> bool:
    """Returns TRUE if the HVAC system heating type is fluid loop. Returns FALSE if the HVAC system
    heating system has anything other than fluid loop or if it has more than 1 heating system.

    Parameters
    ----------
    hvac : dict
        The HVAC system.

    Returns
    -------
    bool
        True: HVAC system heating system has fluid loop as the heating type
        False: HVAC system has a heating system type other than fluid loop
    """
    heating_system = hvac.get("heating_system")
    if heating_system is not None:
        return (
            heating_system.get("hot_water_loop") is not None
            and heating_system.get("type") == HEATING_SYSTEM.FLUID_LOOP
        )
    return False
