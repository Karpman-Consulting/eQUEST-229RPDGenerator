from rpd_generator.schema.schema_enums import SchemaEnums

HEATING_SOURCE = SchemaEnums.schema_enums["HeatingSourceOptions"]


def are_all_terminal_heat_sources_none_or_null(terminals_list):
    """Returns TRUE if the heat source associated with all terminal units input to this function are None or Null. It returns FALSE if any terminal unit has a heat source other than None or Null.

    Parameters
    ----------
    terminals_list : list
        List of terminals

    Returns
    -------
    bool
        True: the heat source associated with all terminal units input to this function are None or Null
        False: any terminal unit has a heat source other than None or Null
    """

    return all(
        terminal.get("heating_source") in [None, HEATING_SOURCE.NONE]
        for terminal in terminals_list
    )
