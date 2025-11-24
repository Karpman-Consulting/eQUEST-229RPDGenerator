from rpd_generator.schema.schema_enums import SchemaEnums

TERMINAL_TYPE = SchemaEnums.schema_enums["TerminalOptions"]


def are_all_terminal_types_cav_with_none_equal_to_null(terminals_list):
    """Returns TRUE if all of the terminal unit types input to this function are constant air volume (CAV).
    It returns FALSE if any of the terminal units are of a type other than constant air volume (CAV).

    Parameters
    ----------
    terminals_list : list
        List of terminal units IDs

    Returns
    -------
    bool
        True: all of the terminal unit types input to this function are constant air volume (CAV) (null or missing is false)
        False: any of the terminal units are of a type other than constant air volume (CAV).
    """
    return all(
        terminal.get("type") == TERMINAL_TYPE.CONSTANT_AIR_VOLUME
        for terminal in terminals_list
    )
