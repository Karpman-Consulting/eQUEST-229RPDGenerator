from rpd_generator.schema.schema_enums import SchemaEnums

EXTERNAL_FLUID_SOURCE = SchemaEnums.schema_enums["ExternalFluidSourceOptions"]
FLUID_LOOP_TYPE = SchemaEnums.schema_enums["FluidLoopOptions"]


def are_all_terminal_heating_loops_purchased_heating(
    terminals_list, purchased_heating_loop_id_list
):
    """Returns TRUE if the fluid loop associated with the heating_from_loop associated with each terminal unit is purchased heating. Returns FALSE if this is not the case.
    ----------
    terminals_list : list
        List of terminals

    Returns
    -------
    bool
        True: fluid loop associated with the heating_from_loop associated with each terminal unit is purchased heating
        False: otherwise
    """
    return all(
        terminal.get("heating_from_loop") in purchased_heating_loop_id_list
        for terminal in terminals_list
    )
