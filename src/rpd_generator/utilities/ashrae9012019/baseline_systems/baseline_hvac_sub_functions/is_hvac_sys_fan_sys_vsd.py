from rpd_generator.schema.schema_enums import SchemaEnums

FAN_SYSTEM_SUPPLY_FAN_CONTROL = SchemaEnums.schema_enums[
    "FanSystemSupplyFanControlOptions"
]


def is_hvac_sys_fan_sys_vsd(hvac):
    """Returns TRUE if the HVAC system fan system is variable speed drive controlled. Returns FALSE if the HVAC system fan system is anything other than variable speed drive controlled.

    Parameters
    ----------
    hvac : dict
        The HVAC system.

    Returns
    -------
    bool
        True: HVAC system fan system his variable speed drive control
        False: the HVAC system has a fan system that is anything other than variable speed drive controlled
    """

    fan_system = hvac.get("fan_system")
    if fan_system is not None:
        return (
            fan_system.get("fan_control")
            == FAN_SYSTEM_SUPPLY_FAN_CONTROL.VARIABLE_SPEED_DRIVE
        )
    return False
