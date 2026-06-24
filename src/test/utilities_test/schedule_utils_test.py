from rpd_generator.utilities.schedule_utils import (
    get_max_schedule_multiplier_cooling_design_hourly_value_or_default,
    get_max_schedule_multiplier_heating_design_hourly_value_or_default,
    get_max_schedule_multiplier_hourly_value_or_default,
    get_schedule_multiplier_hourly_value_or_default,
    get_schedule_year_length,
)


def test_get_schedule_multiplier_hourly_value_returns_matching_schedule_values():
    rmd = {"schedules": [{"id": "Occ", "hourly_values": [0.0, 0.5, 1.0]}]}

    assert get_schedule_multiplier_hourly_value_or_default(rmd, "Occ") == [
        0.0,
        0.5,
        1.0,
    ]


def test_get_schedule_multiplier_hourly_value_returns_default_when_missing_or_empty():
    rmd = {
        "schedules": [
            {"id": "Empty", "hourly_values": []},
            {"id": "Other", "hourly_values": [1]},
        ]
    }

    assert get_schedule_multiplier_hourly_value_or_default(
        rmd, "Missing", default=[0]
    ) == [0]
    assert get_schedule_multiplier_hourly_value_or_default(
        rmd, "Empty", default=[0]
    ) == [0]


def test_get_max_schedule_multiplier_hourly_value_returns_zero_when_values_are_zero():
    rmd = {"schedules": [{"id": "Zero", "hourly_values": [0.0, 0.0]}]}

    assert get_max_schedule_multiplier_hourly_value_or_default(rmd, "Zero", 99) == 0.0


def test_get_max_design_day_values_return_defaults_for_missing_schedules():
    rmd = {
        "schedules": [
            {
                "id": "Design",
                "hourly_heating_design_day": [0.1, 0.7, 0.3],
                "hourly_cooling_design_day": [0.2, 0.9, 0.4],
            }
        ]
    }

    assert (
        get_max_schedule_multiplier_heating_design_hourly_value_or_default(
            rmd, "Design"
        )
        == 0.7
    )
    assert (
        get_max_schedule_multiplier_cooling_design_hourly_value_or_default(
            rmd, "Design"
        )
        == 0.9
    )
    assert (
        get_max_schedule_multiplier_heating_design_hourly_value_or_default(
            rmd, "Missing", default=0.25
        )
        == 0.25
    )


def test_get_schedule_year_length_uses_first_non_empty_hourly_values():
    rmd = {
        "schedules": [
            {"id": "Empty", "hourly_values": []},
            {"id": "Short", "hourly_values": [1, 2, 3]},
            {"id": "Long", "hourly_values": list(range(10))},
        ]
    }

    assert get_schedule_year_length(rmd) == 3


def test_get_schedule_year_length_defaults_to_8760_without_hourly_values():
    assert get_schedule_year_length({"schedules": [{"id": "NoHourly"}]}) == 8760
    assert get_schedule_year_length({}) == 8760
