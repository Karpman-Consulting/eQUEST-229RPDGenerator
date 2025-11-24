from rpd_generator.schema.schema_enums import SchemaEnums

HEATING_SYSTEM = SchemaEnums.schema_enums["HeatingSystemOptions"]


def is_hvac_sys_preheating_type_fluid_loop(hvac: dict) -> bool:
    """Returns TRUE if the HVAC system preheating system heating type is fluid loop. Returns FALSE if the HVAC system
    preheating system has anything other than fluid loop.

    Parameters
    ----------
    hvac : dict
        The HVAC system.

    Returns
    -------
    bool
        True: HVAC system preheating system has fluid loop as the heating type
        False: otherwise
    """
    preheat_system = hvac.get("preheat_system")
    if preheat_system is not None:
        return (
            preheat_system.get("type") == HEATING_SYSTEM.FLUID_LOOP
            and preheat_system.get("hot_water_loop") is not None
        )
    return False
