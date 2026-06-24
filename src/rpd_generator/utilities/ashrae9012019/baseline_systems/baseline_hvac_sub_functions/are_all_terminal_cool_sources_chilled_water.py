from rpd_generator.schema.schema_enums import SchemaEnums

COOLING_SOURCE = SchemaEnums.schema_enums["CoolingSourceOptions"]


def are_all_terminal_cool_sources_chilled_water(terminals_list):
    """Returns TRUE if the cool source associated with all terminal units is CHILLED_WATER. It returns FALSE if any terminal unit has a cool source other than CHILLED_WATER.
    ----------
    terminals_list : list
        List of terminal units IDs
    Returns
    -------
    bool
        True: cool source associated with all terminal units sent to this function is CHILLED_WATER
        False: any terminal unit has a cool source other than CHILLED_WATER
    """
    return all(
        terminal.get("cooling_source") == COOLING_SOURCE.CHILLED_WATER
        for terminal in terminals_list
    )
