def are_all_terminal_chw_loops_purchased_cooling(
    terminals_list, purchased_cooling_loop_id_list
):
    """Returns TRUE if the fluid loop associated with the cooling_from_loop associated with each terminal unit is purchased CHW. Returns FALSE if this is not the case.

    Parameters
    ----------
    terminals_list : list
        List of terminals
    purchased_cooling_loop_id_list : list
        List of purchased cooling loop ids

    Returns
    -------
    bool
        True: the fluid loop associated with the cooling_from_loop associated with each terminal unit is purchased CHW.
        False: otherwise
    """
    return all(
        terminal.get("cooling_from_loop") in purchased_cooling_loop_id_list
        for terminal in terminals_list
    )
