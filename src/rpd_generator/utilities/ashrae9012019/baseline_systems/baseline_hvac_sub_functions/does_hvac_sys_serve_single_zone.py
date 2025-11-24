def does_hvac_sys_serve_single_zone(zone_list: list) -> bool:
    """Returns TRUE if the HVAC system serves a single zone. Returns FALSE if the HVAC system serves multiple zones.

    Parameters
    ----------
    zone_list : list
         list of zones

    Returns
    -------
    bool
        True: HVAC system serves a single zone
        False: HVAC system serves multiple zones
    """
    return len(zone_list) == 1
