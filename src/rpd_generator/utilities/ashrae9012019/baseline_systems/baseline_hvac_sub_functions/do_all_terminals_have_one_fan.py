def do_all_terminals_have_one_fan(terminals_list):
    """Returns TRUE if a fan data element associated with all terminal units input to this function.
     It returns FALSE if any terminal unit has no fan data element not equal to one.

    Parameters
    ----------
    terminals_list : list
        List of terminal units IDs

    Returns
    -------
    bool
        True: there is a fan data element associated with all terminal units input to this function.
        False: any terminal unit a no fan data.
    """

    return all([terminal.get("fan") is not None for terminal in terminals_list])
