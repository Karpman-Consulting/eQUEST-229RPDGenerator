def does_each_zone_have_only_one_terminal(zone_list):
    """Returns TRUE if each zone input to this function only has one terminal unit. It returns FALSE if any zone has more than one terminal unit.

    Parameters
    ----------
    zone_list : list
        List of zones to evaluate.

    Returns
    -------
    bool
        True: each zone input to this function only has one terminal unit or no terminal
        False: any zone has more than one terminal
    """
    return all(
        zone.get("terminals") is not None and len(zone["terminals"]) == 1
        for zone in zone_list
    )
