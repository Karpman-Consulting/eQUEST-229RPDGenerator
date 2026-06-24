from rpd_generator.schema.schema_enums import SchemaEnums

FLUID_LOOP = SchemaEnums.schema_enums["FluidLoopOptions"]


def is_hvac_sys_fluid_loop_attached_to_chiller(hvac, chiller_loop_id_list):
    """Returns TRUE if the fluid loop associated with the cooling system associated with the HVAC system is attached to a chiller. Returns FALSE if this is not the case.

    Parameters
    ----------
    hvac : dict
        The HVAC system.
    chiller_loop_id_list : list
        List of fluid loop IDs that are attached to chillers.

    Returns
    -------
    bool
        True: fluid loop associated with the cooling system associated with the HVAC system is attached to a chiller
        False: otherwise
    """
    cooling_system = hvac.get("cooling_system")
    if cooling_system is not None:
        return cooling_system.get("chilled_water_loop") in chiller_loop_id_list
    return False
