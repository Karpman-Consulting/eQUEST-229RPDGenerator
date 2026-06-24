from rpd_generator.schema.schema_enums import SchemaEnums

TERMINAL_FAN_CONFIGURATION = SchemaEnums.schema_enums["TerminalFanConfigurationOptions"]


def are_all_terminal_fan_configs_parallel(terminals_list):
    """Returns TRUE if the fan configuration associated with all terminal units input to this function are parallel.
    It returns FALSE if any terminal unit has a fan configuration other than parallel.

    ----------
    terminals_list : list
        List of terminal units IDs
    Returns
    -------
    bool
        True: fan configuration associated with all terminal units input to this function are parallel
        False: any terminal unit has a fan configuration other than parallel
    """
    # all terminal's fan configuration should be parallel, and false otherwise.
    return all(
        terminal.get("fan_configuration") == TERMINAL_FAN_CONFIGURATION.PARALLEL
        for terminal in terminals_list
    )
