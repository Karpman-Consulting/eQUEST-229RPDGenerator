from rpd_generator.schema.validate import (
    check_fluid_loop_association,
    check_fluid_loop_or_piping_association,
    check_hvac_association,
    check_schedule_association,
    check_service_water_heating_association,
    check_unique_ids_in_ruleset_model_descriptions,
    check_zone_association,
    json_paths_to_lists,
    non_schema_validate_rmd,
)


def _minimal_rpd(
    *,
    schedules=None,
    fluid_loops=None,
    pumps=None,
    service_water_heating_distribution_systems=None,
    service_water_heating_equipment=None,
    chillers=None,
    heat_rejections=None,
    boilers=None,
    external_fluid_sources=None,
    zones=None,
    hvac_systems=None,
):
    return {
        "ruleset_model_descriptions": [
            {
                "id": "RMD-1",
                "schedules": schedules or [],
                "fluid_loops": fluid_loops or [],
                "pumps": pumps or [],
                "service_water_heating_distribution_systems": (
                    service_water_heating_distribution_systems or []
                ),
                "service_water_heating_equipment": (
                    service_water_heating_equipment or []
                ),
                "chillers": chillers or [],
                "heat_rejections": heat_rejections or [],
                "boilers": boilers or [],
                "external_fluid_sources": external_fluid_sources or [],
                "buildings": [
                    {
                        "id": "B-1",
                        "building_segments": [
                            {
                                "id": "SEG-1",
                                "zones": zones or [],
                                "heating_ventilating_air_conditioning_systems": (
                                    hvac_systems or []
                                ),
                            }
                        ],
                    }
                ],
            }
        ]
    }


def test_json_paths_to_lists_returns_nested_list_paths():
    assert json_paths_to_lists({"a": [{"b": [1, 2]}], "c": {"d": []}}) == {
        "$.a",
        "$.a[*].b",
        "$.c.d",
    }


def test_check_unique_ids_reports_duplicate_ids_at_nested_list_path():
    rpd = _minimal_rpd(
        zones=[
            {
                "id": "Z-1",
                "spaces": [{"id": "S-1"}, {"id": "S-1"}],
                "terminals": [],
            }
        ]
    )

    message = check_unique_ids_in_ruleset_model_descriptions(rpd)

    assert (
        "ruleset_model_descriptions[0].buildings[*].building_segments[*]"
        ".zones[*].spaces" in message
    )


def test_check_hvac_association_reports_terminals_served_by_missing_hvac_system():
    rpd = _minimal_rpd(
        zones=[
            {
                "id": "Z-1",
                "terminals": [
                    {
                        "id": "T-1",
                        "served_by_heating_ventilating_air_conditioning_system": "HVAC-MISSING",
                    }
                ],
            }
        ],
        hvac_systems=[{"id": "HVAC-1"}],
    )

    assert check_hvac_association(rpd) == ["HVAC-MISSING"]


def test_check_zone_association_reports_missing_motor_location_zone():
    rpd = _minimal_rpd(
        zones=[{"id": "Z-1", "terminals": []}],
        hvac_systems=[
            {
                "id": "HVAC-1",
                "fan_system": {
                    "supply_fans": [{"id": "Fan-1", "motor_location_zone": "Z-404"}]
                },
            }
        ],
    )

    assert check_zone_association(rpd) == ["Z-404"]


def test_check_fluid_loop_association_reports_missing_chiller_loop_reference():
    rpd = _minimal_rpd(
        fluid_loops=[{"id": "Loop-1"}],
        chillers=[{"id": "Chiller-1", "cooling_loop": "Loop-404"}],
    )

    assert check_fluid_loop_association(rpd) == ["Loop-404"]


def test_check_schedule_association_finds_hvac_fan_schedules_in_building_segments():
    rpd = _minimal_rpd(
        schedules=[{"id": "Existing-Schedule"}],
        hvac_systems=[
            {
                "id": "HVAC-1",
                "fan_system": {
                    "supply_air_temperature_reset_schedule": "Existing-Schedule",
                    "operating_schedule": "Missing-Fan-Schedule",
                },
            }
        ],
    )

    assert check_schedule_association(rpd) == ["Missing-Fan-Schedule"]


def test_check_schedule_association_accepts_declared_loop_and_hvac_schedules():
    rpd = _minimal_rpd(
        schedules=[
            {"id": "Loop-Schedule"},
            {"id": "Fan-Schedule"},
            {"id": "Reset-Schedule"},
        ],
        fluid_loops=[
            {
                "id": "Loop-1",
                "heating_design_and_control": {"operation_schedule": "Loop-Schedule"},
            }
        ],
        hvac_systems=[
            {
                "id": "HVAC-1",
                "fan_system": {
                    "supply_air_temperature_reset_schedule": "Reset-Schedule",
                    "operating_schedule": "Fan-Schedule",
                },
            }
        ],
    )

    assert check_schedule_association(rpd) == []


def test_check_fluid_loop_or_piping_association_accepts_loops_child_loops_and_piping():
    rpd = _minimal_rpd(
        fluid_loops=[{"id": "Loop-1", "child_loops": [{"id": "Child-Loop"}]}],
        service_water_heating_distribution_systems=[
            {
                "id": "SWH-1",
                "service_water_piping": [{"id": "Pipe-1"}],
            }
        ],
        pumps=[
            {"id": "Pump-1", "loop_or_piping": "Loop-1"},
            {"id": "Pump-2", "loop_or_piping": "Child-Loop"},
            {"id": "Pump-3", "loop_or_piping": "Pipe-1"},
        ],
    )

    assert check_fluid_loop_or_piping_association(rpd) == []


def test_check_fluid_loop_or_piping_association_reports_missing_reference():
    rpd = _minimal_rpd(pumps=[{"id": "Pump-1", "loop_or_piping": "Missing-Pipe"}])

    assert check_fluid_loop_or_piping_association(rpd) == ["Missing-Pipe"]


def test_check_service_water_heating_association_reports_missing_distribution():
    rpd = _minimal_rpd(
        service_water_heating_distribution_systems=[{"id": "SWH-1"}],
        service_water_heating_equipment=[
            {"id": "Water-Heater-1", "distribution_system": "SWH-404"}
        ],
    )

    assert check_service_water_heating_association(rpd) == ["SWH-404"]


def test_non_schema_validate_rmd_passes_for_minimal_valid_associations():
    rpd = _minimal_rpd(
        schedules=[{"id": "Fan-Schedule"}],
        zones=[
            {
                "id": "Z-1",
                "terminals": [
                    {
                        "id": "T-1",
                        "served_by_heating_ventilating_air_conditioning_system": "HVAC-1",
                    }
                ],
            }
        ],
        hvac_systems=[
            {"id": "HVAC-1", "fan_system": {"operating_schedule": "Fan-Schedule"}}
        ],
    )

    assert non_schema_validate_rmd(rpd) == {"passed": True, "error": None}


def test_non_schema_validate_rmd_aggregates_duplicate_id_and_association_errors():
    rpd = _minimal_rpd(
        zones=[
            {
                "id": "Z-1",
                "spaces": [{"id": "S-1"}, {"id": "S-1"}],
                "terminals": [
                    {
                        "id": "T-1",
                        "served_by_heating_ventilating_air_conditioning_system": "HVAC-404",
                    }
                ],
            }
        ],
        hvac_systems=[],
    )

    result = non_schema_validate_rmd(rpd)

    assert result["passed"] is False
    assert any("Non-unique ids" in error for error in result["error"])
    assert any("HVAC-404" in error for error in result["error"])
