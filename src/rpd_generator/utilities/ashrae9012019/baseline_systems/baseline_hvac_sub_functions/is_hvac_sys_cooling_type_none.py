from rpd_generator.schema.schema_enums import SchemaEnums

COOLING_SYSTEM_TYPE = SchemaEnums.schema_enums["CoolingSystemOptions"]


def is_hvac_sys_cooling_type_none(hvac):
    """Returns TRUE if the HVAC system cooling type is None or Null. Returns FALSE if the HVAC system has anything
    other than None or Null for the cooling type.

    Parameters
    ----------
    hvac : dict
        The HVAC system.

    Returns
    -------
    bool
        True: HVAC system cooling type is None or Null
        False: HVAC system has anything other than None or Null for the cooling type
    """
    cooling_system = hvac.get("cooling_system")
    if cooling_system is None or cooling_system.get("type") == COOLING_SYSTEM_TYPE.NONE:
        return True
    return False
