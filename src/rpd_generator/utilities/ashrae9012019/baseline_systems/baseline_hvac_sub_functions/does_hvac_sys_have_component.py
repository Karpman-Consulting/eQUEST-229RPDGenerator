from rpd_generator.schema.schema_enums import SchemaEnums

HEATING_SYSTEM = SchemaEnums.schema_enums["HeatingSystemOptions"]
COOLING_SYSTEM = SchemaEnums.schema_enums["CoolingSystemOptions"]


def has_preheat_system(hvac: dict) -> bool:
    """
    Check whether the specified hvac system has a preheat system.

    Parameters
    ----------
    hvac: dict
        The HVAC system to evaluate.

    Returns
    -------
    If preheat system exists, it returns true. Otherwise, it returns false.
    """
    preheat_system = hvac.get("preheat_system")

    return (
        preheat_system is not None
        and preheat_system.get("type") is not None
        and preheat_system["type"] != HEATING_SYSTEM.NONE
    )


def has_heating_system(hvac: dict) -> bool:
    """
    Check whether the specified hvac system has a heating system.

    Parameters
    ----------
    hvac: dict
        The HVAC system to evaluate.

    Returns
    -------
    If heating system exists, it returns true. Otherwise, it returns false.
    """
    heating_system = hvac.get("heating_system")

    return (
        heating_system is not None
        and heating_system.get("type") is not None
        and heating_system["type"] != HEATING_SYSTEM.NONE
    )


def has_cooling_system(hvac: dict) -> bool:
    """
    Check whether the specified hvac system has a cooling system.

    Parameters
    ----------
    hvac: dict
        The HVAC system to evaluate.

    Returns
    -------
    If cooling system exists, it returns true. Otherwise, it returns false.
    """
    cooling_system = hvac.get("cooling_system")

    return (
        cooling_system is not None
        and cooling_system.get("type") is not None
        and cooling_system["type"] != COOLING_SYSTEM.NONE
    )


def has_fan_system(hvac: dict) -> bool:
    """
    Check whether the specified hvac system has a fan system.

    Parameters
    ----------
    hvac: dict
        The HVAC system to evaluate.

    Returns
    -------
    If fan system exists, it returns true. Otherwise, it returns false.
    """

    return hvac.get("fan_system") is not None
