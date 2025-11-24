from rpd_generator.schema.schema_enums import SchemaEnums

TERMINAL_TYPE = SchemaEnums.schema_enums["TerminalOptions"]


def are_all_terminal_types_cav(terminals_list):
    """Returns TRUE if all the terminal unit types input to this function are constant air volume (CAV) or if this
    data element is undefined. It returns FALSE if any of the terminal units are of a type other than constant air
    volume (CAV).

    Parameters
    ----------
    terminals_list : list
        List of terminal units IDs

    Returns
    -------
    bool
        True: all of the terminal unit types input to this function are constant air volume (CAV)
        False: any of the terminal units are of a type other than constant air volume (CAV).
    """

    return all(
        terminal.get("type") in [TERMINAL_TYPE.CONSTANT_AIR_VOLUME, None]
        for terminal in terminals_list
    )
