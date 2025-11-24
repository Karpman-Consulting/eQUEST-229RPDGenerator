def are_all_terminal_supplies_ducted(terminals_list):
    """Returns TRUE if all the terminal supplies are ducted (i.e., is_supply_ducted = TRUE) for the list of
    terminal units input to the function. It returns FALSE if any of the terminal supplies are not ducted (i.e.,
    is_supply_ducted = FALSE).

        Parameters
        ----------
        terminals_list : list
            List of terminal units IDs

        Returns
        -------
        bool
            True: all of the terminal supplies are ducted (i.e., is_supply_ducted = TRUE) for the list of terminal units input to the function
            False: any of the terminal supplies are not ducted (i.e., is_supply_ducted = FALSE)
    """

    return all(terminal.get("is_supply_ducted") for terminal in terminals_list)
