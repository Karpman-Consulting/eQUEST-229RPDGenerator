from rpd_generator.schema.schema_enums import SchemaEnums

HEATING_SYSTEM = SchemaEnums.schema_enums["HeatingSystemOptions"]


def is_hvac_sys_preheating_type_elec_resistance(hvac):
    """Returns TRUE if the HVAC system preheating system heating type is ELECTRIC_RESISTANCE. Returns FALSE if the
    HVAC system preheating system has anything other than ELECTRIC_RESISTANCE.

    Parameters
    ----------
    hvac : dict
        The HVAC system.

    Returns
    -------
    bool
        True: HVAC system preheating system has ELECTRIC_RESISTANCE as the heating type
        False: HVAC system has a preheating system type other than ELECTRIC_RESISTANCE
    """
    preheat_system = hvac.get("preheat_system")
    if preheat_system is not None:
        return preheat_system.get("type") == HEATING_SYSTEM.ELECTRIC_RESISTANCE
    return False
