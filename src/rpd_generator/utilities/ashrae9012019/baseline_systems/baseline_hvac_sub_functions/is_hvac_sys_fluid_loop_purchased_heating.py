def is_hvac_sys_fluid_loop_purchased_heating(hvac, purchased_heating_loop_id_list):
    """Returns TRUE if the fluid loop associated with the heating system associated with the HVAC system is attached to an external purchased heating loop. Returns FALSE if this is not the case.

    Parameters
    ----------
    hvac : dict
        The HVAC system.
    purchased_heating_loop_id_list : list
        List of purchased heating loop IDs.

    Returns
    -------
    bool
        True: the fluid loop associated with the heating system associated with the HVAC system is attached to an external purchased heating loop
        False: otherwise
    """
    heating_system = hvac.get("heating_system")
    if heating_system is not None:
        return heating_system.get("hot_water_loop") in purchased_heating_loop_id_list
    return False
