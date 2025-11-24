from rpd_generator.schema.schema_enums import SchemaEnums

HEATING_SYSTEM = SchemaEnums.schema_enums["HeatingSystemOptions"]


def is_hvac_sys_heating_type_furnace(hvac):
    """Returns TRUE if the HVAC system heating type is furnace. Returns FALSE if the HVAC system
    heating system has anything other than furnace or if it has more than 1 heating system.

    Parameters
    ----------
    hvac : dict
        The HVAC system.

    Returns
    -------
    bool
        True: the HVAC system heating system has furnace as the heating type
        False: the HVAC system has a heating system type other than furnace
    """
    heating_system = hvac.get("heating_system")
    if heating_system is not None:
        return heating_system.get("type") == HEATING_SYSTEM.FURNACE
    return False
