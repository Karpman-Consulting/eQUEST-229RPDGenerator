from rpd_generator.schema.schema_enums import SchemaEnums

HEATING_SOURCE = SchemaEnums.schema_enums["HeatingSourceOptions"]


def are_all_terminal_heat_sources_hot_water(terminals_list):
    """Returns TRUE if the heat source associated with all terminal units input to this function is HOT_WATER. It returns FALSE if any terminal unit has a heat source other than HOT_WATER.

    Parameters
    ----------
    terminals_list : list
        List of terminals

    Returns
    -------
    bool
        True: the heat source associated with all terminal units input to this function is HOT_WATER
        False: any terminal unit has a heat source other than HOT_WATER.
    """

    return all(
        terminal.get("heating_source") == HEATING_SOURCE.HOT_WATER
        for terminal in terminals_list
    )
