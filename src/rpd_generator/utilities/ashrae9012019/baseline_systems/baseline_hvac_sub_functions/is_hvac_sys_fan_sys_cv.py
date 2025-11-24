from rpd_generator.schema.schema_enums import SchemaEnums

FAN_SYSTEM_SUPPLY_FAN_CONTROL = SchemaEnums.schema_enums[
    "FanSystemSupplyFanControlOptions"
]


def is_hvac_sys_fan_sys_cv(hvac):
    """Returns TRUE if the HVAC system fan system is constant volume. Returns FALSE if the HVAC system fan system is anything other than constant volume.

    Parameters
    ----------
    hvac: dict
        The HVAC system ID.

    Returns
    -------
    bool
        True: the HVAC system fan system has constant volume
        False: the HVAC system has a fan system that is anything other than constant volume
    """
    fan_system = hvac.get("fan_system")
    if fan_system is not None:
        return fan_system.get("fan_control") == FAN_SYSTEM_SUPPLY_FAN_CONTROL.CONSTANT
    return False
