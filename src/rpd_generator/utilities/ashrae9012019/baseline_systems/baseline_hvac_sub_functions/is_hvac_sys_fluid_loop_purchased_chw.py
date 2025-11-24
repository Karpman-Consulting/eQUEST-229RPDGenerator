def is_hvac_sys_fluid_loop_purchased_chw(hvac, purchased_cooling_loop_id_list):
    """Returns TRUE if the fluid loop associated with the cooling system associated with the HVAC system is attached to an external purchased chilled water loop. Returns FALSE if this is not the case.

    Parameters
    ----------
    hvac : dict
        The HVAC system.
    purchased_cooling_loop_id_list : list
        List of purchased cooling loop IDs.

    Returns
    -------
    bool
        True: the fluid loop associated with the cooling system associated with the HVAC system is attached to an external purchased cooling loop
        False: otherwise
    """
    cooling_system = hvac.get("cooling_system")
    if cooling_system is not None:
        return (
            cooling_system.get("chilled_water_loop") in purchased_cooling_loop_id_list
        )
    return False
