from rpd_generator.schema.schema_enums import SchemaEnums

HEATING_SOURCE = SchemaEnums.schema_enums["HeatingSourceOptions"]


def are_all_terminal_heat_sources_electric(terminals_list):
    """Returns TRUE if the heat source associated with all terminal units input to this function are electric. It
    returns FALSE if any terminal unit has a heat source other than electric.

    Parameters
    ----------
    terminals_list : list
        List of terminal units IDs

    Returns
    -------
    bool
        True: heat source associated with all terminal units input to this function are electric
        False: any terminal unit has a heat source other than electric
    """
    return all(
        terminal.get("heating_source") == HEATING_SOURCE.ELECTRIC
        for terminal in terminals_list
    )
