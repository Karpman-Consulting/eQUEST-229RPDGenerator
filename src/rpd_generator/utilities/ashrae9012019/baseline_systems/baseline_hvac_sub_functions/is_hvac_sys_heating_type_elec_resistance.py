from rpd_generator.schema.schema_enums import SchemaEnums

HEATING_SYSTEM = SchemaEnums.schema_enums["HeatingSystemOptions"]


def is_hvac_sys_heating_type_elec_resistance(hvac):
    """Returns TRUE if the HVAC system heating type is ELECTRIC_RESISTANCE. Returns FALSE if the HVAC system heating system has anything other than ELECTRIC_RESISTANCE.

    Parameters
    ----------
    hvac : dict
        The HVAC system.

    Returns
    -------
    bool
        True: the HVAC system heating system has ELECTRIC_RESISTANCE as the heating type
        False: the HVAC system has a heating system type other than ELECTRIC_RESISTANCE
    """
    heating_system = hvac.get("heating_system")
    if heating_system is not None:
        return heating_system.get("type") == HEATING_SYSTEM.ELECTRIC_RESISTANCE
    return False
