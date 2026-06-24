from rpd_generator.schema.schema_enums import SchemaEnums

TERMINAL_TYPE = SchemaEnums.schema_enums["TerminalOptions"]


def are_all_terminal_types_vav(terminals_list: list[dict]) -> bool:
    """It returns FALSE if no terminal unit in the list or any of the terminal units are of a type other than variable air volume (VAV) or null.

    Parameters
    ----------
    terminals_list : list
        List of terminals

    Returns
    -------
    bool
        True: all of the terminal unit types input to this function are variable air volume (VAV)
        False: any of the terminal units are of a type other than variable air volume (VAV)
    """
    return len(terminals_list) > 0 and all(
        [
            terminal.get("type") in [None, TERMINAL_TYPE.VARIABLE_AIR_VOLUME]
            for terminal in terminals_list
        ]
    )
