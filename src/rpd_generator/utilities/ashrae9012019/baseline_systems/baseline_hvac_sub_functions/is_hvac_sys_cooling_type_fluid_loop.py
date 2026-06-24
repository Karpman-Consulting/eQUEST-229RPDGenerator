from rpd_generator.schema.schema_enums import SchemaEnums

COOLING_SYSTEM_TYPE = SchemaEnums.schema_enums["CoolingSystemOptions"]


def is_hvac_sys_cooling_type_fluid_loop(hvac):
    """Returns TRUE if the HVAC system has fluid_loop cooling. Returns FALSE if the HVAC system has anything other
    than fluid_loop cooling or if it has more than 1 cooling system.

    Parameters
    ----------
    hvac: dict
        The HVAC system.

    Returns
    -------
    bool
        True: HVAC system has fluid_loop cooling
        False: HVAC system has a cooling system type other than fluid_loop
    """
    cooling_system = hvac.get("cooling_system")
    if cooling_system is not None:
        return (
            cooling_system.get("type") == COOLING_SYSTEM_TYPE.FLUID_LOOP
            and cooling_system.get("chilled_water_loop") is not None
        )
    return False
