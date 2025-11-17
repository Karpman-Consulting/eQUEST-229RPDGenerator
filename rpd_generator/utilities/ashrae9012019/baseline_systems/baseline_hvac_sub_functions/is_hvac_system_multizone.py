def is_hvac_system_multizone(zone_list):
    """
    Returns TRUE if the HVAC system serves multiple zones. Returns FALSE if the HVAC system serves a single or no zones.

    Parameters
    ----------
    zone_list: list[dict] zones

    Returns
    -------
    bool
        True: HVAC system serves a multiple zones.
        False: HVAC system serves zero or one zone.
    """
    return len(zone_list) > 1
