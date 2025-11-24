from rpd_generator.schema.schema_enums import SchemaEnums

HEATING_SYSTEM = SchemaEnums.schema_enums["HeatingSystemOptions"]


def is_hvac_sys_heating_type_heat_pump(hvac):
    """Returns TRUE if the HVAC system has heat pump as the heating system type. Returns FALSE if the HVAC system has
    anything other than heat pump as the heating system type or if it has more than 1 heating system.

    Parameters
    ----------
    hvac : dict
        The HVAC system.

    Returns
    -------
    bool
        True: the HVAC system has heat pump as the heating system type
        False: the HVAC system has a heating system type other than heat pump as the heating system type
    """
    heating_system = hvac.get("heating_system")
    if heating_system is not None:
        return heating_system.get("type") == HEATING_SYSTEM.HEAT_PUMP
    return False
