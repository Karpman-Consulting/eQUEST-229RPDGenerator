from rpd_generator.schema.schema_enums import SchemaEnums

COOLING_SYSTEM_TYPE = SchemaEnums.schema_enums["CoolingSystemOptions"]


def is_hvac_sys_cooling_type_dx(hvac):
    """Returns TRUE if the HVAC system has DX cooling. Returns FALSE if the HVAC system has anything other than DX cooling.

    Parameters
    ----------
    hvac : dict
        The HVAC system.

    Returns
    -------
    bool
        True: the HVAC system has DX cooling
        False: the HVAC system has a cooling system type other than DX
    """
    cooling_system = hvac.get("cooling_system")
    if cooling_system is not None:
        return cooling_system.get("type") == COOLING_SYSTEM_TYPE.DIRECT_EXPANSION
    return False
