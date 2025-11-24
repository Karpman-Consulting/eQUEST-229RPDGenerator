from rpd_generator.schema.schema_enums import SchemaEnums

FLUID_LOOP = SchemaEnums.schema_enums["FluidLoopOptions"]


def is_hvac_sys_preheat_fluid_loop_attached_to_boiler(hvac, boiler_loop_id_list):
    """Returns True if the fluid loop associated with preheat system associated with the HVAC system is attached to a boiler.
    Returns False if this is not the case.

    Parameters
    ----------
    hvac : dict
        The HVAC system.
    boiler_loop_id_list : list
        List of fluid loop IDs that are attached to boilers.

    Returns
    -------
    bool
        True: preheat system is attached to a boiler
        False: otherwise
    """
    preheat_system = hvac.get("preheat_system")
    if preheat_system is not None:
        return preheat_system.get("hot_water_loop") in boiler_loop_id_list
    return False
