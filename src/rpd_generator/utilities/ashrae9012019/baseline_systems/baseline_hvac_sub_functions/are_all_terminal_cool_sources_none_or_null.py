from rpd_generator.schema.schema_enums import SchemaEnums

COOLING_SOURCE = SchemaEnums.schema_enums["CoolingSourceOptions"]


def are_all_terminal_cool_sources_none_or_null(terminals_list):
    """Returns TRUE if the cool source associated with all terminal units input to this function are None or Null. It returns FALSE if any terminal unit has a cool source other than None or Null.
    ----------
    terminals_list : list
        List of terminal units IDs
    Returns
    -------
    bool
        True: the cool source associated with all terminal units input to this function are None or Null
        False: any terminal unit has a cool source other than None or Null
    """
    return all(
        terminal.get("cooling_source") in [COOLING_SOURCE.NONE, None]
        for terminal in terminals_list
    )
