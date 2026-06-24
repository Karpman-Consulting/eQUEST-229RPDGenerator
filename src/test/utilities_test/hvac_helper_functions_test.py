import pytest

from rpd_generator.utilities.get_dict_of_zones_and_terminals_served_by_hvac_sys import (
    get_dict_of_zones_and_terminals_served_by_hvac_sys,
)
from rpd_generator.utilities.get_hvac_zone_list_w_area_dict import (
    get_hvac_zone_list_w_area_by_rmd_dict,
    get_hvac_zone_list_w_area_dict,
)
from rpd_generator.utilities.get_list_hvac_systems_associated_with_zone import (
    get_list_hvac_systems_associated_with_zone,
)


def _building():
    zone_1 = {
        "id": "Z-1",
        "spaces": [{"id": "S-1", "floor_area": 100}],
        "terminals": [
            {
                "id": "T-1",
                "served_by_heating_ventilating_air_conditioning_system": "HVAC-B",
            },
            {
                "id": "T-2",
                "served_by_heating_ventilating_air_conditioning_system": "HVAC-B",
            },
        ],
    }
    zone_2 = {
        "id": "Z-2",
        "spaces": [{"id": "S-2", "floor_area": 50}],
        "terminals": [
            {
                "id": "T-3",
                "served_by_heating_ventilating_air_conditioning_system": "HVAC-A",
            },
            {"id": "T-4"},
        ],
    }
    return {
        "building_segments": [
            {
                "id": "SEG-1",
                "heating_ventilating_air_conditioning_systems": [
                    {"id": "HVAC-B"},
                    {"id": "HVAC-A"},
                    {"id": "HVAC-C"},
                ],
                "zones": [zone_1, zone_2],
            }
        ]
    }


def test_get_dict_of_zones_and_terminals_served_by_hvac_sys_groups_objects_by_hvac():
    rmd = {"buildings": [_building()]}

    result = get_dict_of_zones_and_terminals_served_by_hvac_sys(rmd)

    assert [zone["id"] for zone in result["HVAC-B"]["zones_list"]] == ["Z-1"]
    assert [terminal["id"] for terminal in result["HVAC-B"]["terminals_list"]] == [
        "T-1",
        "T-2",
    ]
    assert [zone["id"] for zone in result["HVAC-A"]["zones_list"]] == ["Z-2"]


def test_get_list_hvac_systems_associated_with_zone_sorts_and_ignores_missing_links():
    building = _building()
    rmd = {"buildings": [building]}
    zone = building["building_segments"][0]["zones"][1]

    result = get_list_hvac_systems_associated_with_zone(rmd, zone)

    assert result == [{"id": "HVAC-A"}]


def test_get_hvac_zone_list_w_area_dict_deduplicates_zone_area_per_hvac():
    result = get_hvac_zone_list_w_area_dict(_building())

    assert result["HVAC-B"]["zones_list"] == ["Z-1"]
    assert result["HVAC-B"]["total_area"].to("ft2").magnitude == pytest.approx(100)
    assert result["HVAC-A"]["zones_list"] == ["Z-2"]
    assert result["HVAC-A"]["total_area"].to("ft2").magnitude == pytest.approx(50)


def test_get_hvac_zone_list_w_area_by_rmd_dict_reads_all_buildings():
    rmd = {
        "buildings": [
            _building(),
            {
                "building_segments": [
                    {
                        "id": "SEG-2",
                        "zones": [
                            {
                                "id": "Z-3",
                                "spaces": [{"id": "S-3", "floor_area": 25}],
                                "terminals": [
                                    {
                                        "id": "T-5",
                                        "served_by_heating_ventilating_air_conditioning_system": "HVAC-D",
                                    }
                                ],
                            }
                        ],
                    }
                ]
            },
        ]
    }

    result = get_hvac_zone_list_w_area_by_rmd_dict(rmd)

    assert set(result) == {"HVAC-A", "HVAC-B", "HVAC-D"}
    assert result["HVAC-D"]["total_area"].to("ft2").magnitude == pytest.approx(25)


def test_get_hvac_zone_list_w_area_dict_rejects_zero_area_served_zone():
    building = {
        "building_segments": [
            {
                "zones": [
                    {
                        "id": "Z-0",
                        "spaces": [{"id": "S-0", "floor_area": 0}],
                        "terminals": [
                            {
                                "id": "T-0",
                                "served_by_heating_ventilating_air_conditioning_system": "HVAC-0",
                            }
                        ],
                    }
                ]
            }
        ]
    }

    with pytest.raises(AssertionError, match="zone:Z-0 has zero floor area"):
        get_hvac_zone_list_w_area_dict(building)
