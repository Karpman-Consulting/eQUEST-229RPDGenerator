from rpd_generator.schema.schema_enums import SchemaEnums

FLUID_LOOP_TYPE = SchemaEnums.schema_enums["FluidLoopOptions"]


def are_all_terminal_heating_loops_attached_to_boiler(
    terminals_list, boiler_loop_id_list
):
    """Returns TRUE if the fluid loop associated with the heating_from_loop associated with each terminal unit is attached to a boiler. Returns FALSE if this is not the case.

    Parameters
    ----------
    terminals_list : list
        List of terminals
    boiler_loop_id_list : list
        List of loop ids that are attached to boilers

    Returns
    -------
    bool
        True: fluid loop associated with the heating_from_loop associated with each terminal unit is attached to a boiler
        False: otherwise
    """
    return all(
        terminal.get("heating_from_loop") in boiler_loop_id_list
        for terminal in terminals_list
    )
