def is_hvac_sys_preheat_fluid_loop_purchased_heating(hvac, purchased_heating_loop_list):
    """Returns TRUE if the fluid loop associated with the preheating system associated with the HVAC system is
    attached to an external purchased heating loop. Returns FALSE if this is not the case.

    Parameters
    ----------
    hvac : dict
    The HVAC system to evaluate.
    purchased_heating_loop_list : list
        List of purchased heating loop IDs.

    Returns
    -------
    bool
        True: fluid loop associated with the preheating system associated with the HVAC system is attached to an external purchased heating loop
        False: otherwise
    """
    preheat_system = hvac.get("preheat_system")
    if preheat_system is not None:
        return preheat_system.get("hot_water_loop") in purchased_heating_loop_list
    return False
