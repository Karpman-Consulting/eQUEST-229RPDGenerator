from rpd_generator.utilities.jsonpath_utils import find_all


def get_list_hvac_systems_associated_with_zone(rmd: dict, zone: dict) -> list[dict]:
    """
    Get the list of the heating ventilation and cooling system ids associated with a zone in either the U_RMD, P_RMD, or B_RMD.

    Parameters
    ----------
    rmd: dict RMD at RuleSetModelDescription level
    zone: dict Zone object within the RMD

    Returns
    -------
    list  A list that saves all the HVAC systems associated with the zone.
    -------

    """
    heating_ventilating_air_conditioning_systems = find_all(
        "$.buildings[*].building_segments[*].heating_ventilating_air_conditioning_systems[*]",
        rmd,
    )
    hvac_ids_serving_zone = {
        terminal.get("served_by_heating_ventilating_air_conditioning_system")
        for terminal in zone.get("terminals", [])
        if terminal.get("served_by_heating_ventilating_air_conditioning_system")
    }

    # return a sorted list of hvac systems associated with the ids serving the zone
    return sorted(
        [
            hvac_system
            for hvac_system in heating_ventilating_air_conditioning_systems
            if hvac_system["id"] in hvac_ids_serving_zone
        ],
        key=lambda d: d["id"],
    )
