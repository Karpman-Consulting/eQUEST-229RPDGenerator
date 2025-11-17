def are_all_terminal_fans_null(terminals_list):
    """Returns TRUE if the fan data element associated with all terminal units input to this function are equal to Null. It returns FALSE if any terminal unit has a fan data element not equal to Null.
    ----------
    terminals_list : list
        List of terminal units IDs
    Returns
    -------
    bool
        True: fan data element associated with all terminal units input to this function are equal to Null
        False: any terminal unit has a fan data element not equal to Null.
    """
    return all(terminal.get("fan") is None for terminal in terminals_list)
