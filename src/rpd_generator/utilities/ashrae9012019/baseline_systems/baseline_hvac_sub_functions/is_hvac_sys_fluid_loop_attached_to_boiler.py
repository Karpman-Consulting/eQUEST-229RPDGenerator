from rpd_generator.schema.schema_enums import SchemaEnums

FLUID_LOOP = SchemaEnums.schema_enums["FluidLoopOptions"]


def is_hvac_sys_fluid_loop_attached_to_boiler(hvac, boiler_loop_id_list):
    """Returns TRUE if the fluid loop associated with the heating system associated with the HVAC system is attached to a boiler. Returns FALSE if this is not the case.

    Parameters
    ----------
    hvac : dict
        The HVAC system.
    boiler_loop_id_list : list
        List of fluid loop IDs that are attached to boilers.

    Returns
    -------
    bool
        True: the fluid loop associated with the heating system associated with the HVAC system is attached to a boiler
        False: otherwise
    """
    heating_system = hvac.get("heating_system")
    if heating_system is not None:
        return heating_system.get("hot_water_loop") in boiler_loop_id_list
    return False
