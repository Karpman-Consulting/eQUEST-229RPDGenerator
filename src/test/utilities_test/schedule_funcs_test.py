import pytest

from rpd_generator.utilities.schedule_funcs import (
    FRIDAY,
    HOLIDAY,
    MONDAY,
    THURSDAY,
    find_nth_weekday_in_range,
    generate_year_calendar,
    get_alternate_holidays,
    get_day_of_week_jan_1,
    get_official_us_holidays,
    is_leap_year,
    set_holiday_if_workday,
)


@pytest.mark.parametrize(
    ("year", "expected"),
    [
        (2024, "MONDAY"),
        (2025, "WEDNESDAY"),
        (2026, "THURSDAY"),
    ],
)
def test_get_day_of_week_jan_1(year, expected):
    assert get_day_of_week_jan_1(year) == expected


@pytest.mark.parametrize(
    ("year", "expected"),
    [
        (2024, True),
        (2025, False),
        (1900, False),
        (2000, True),
    ],
)
def test_is_leap_year_handles_century_rules(year, expected):
    assert is_leap_year(year) is expected


def test_generate_year_calendar_uses_expected_day_types_for_common_year():
    calendar = generate_year_calendar(2025, "WEDNESDAY")

    assert len(calendar) == 365
    assert calendar["1/1"] == 3
    assert calendar["1/6"] == MONDAY
    assert calendar["1/10"] == FRIDAY


def test_generate_year_calendar_includes_february_29_for_leap_year():
    calendar = generate_year_calendar(2024, "MONDAY")

    assert len(calendar) == 366
    assert calendar["2/29"] == THURSDAY


def test_set_holiday_if_workday_only_changes_monday():
    calendar = {"1/1": MONDAY, "1/2": 2}

    set_holiday_if_workday(calendar, "1/1")
    set_holiday_if_workday(calendar, "1/2")

    assert calendar == {"1/1": HOLIDAY, "1/2": 2}


def test_find_nth_weekday_in_range_returns_matching_date_or_none():
    calendar = generate_year_calendar(2025, "WEDNESDAY")

    assert find_nth_weekday_in_range(calendar, 1, 15, 21, MONDAY) == "1/20"
    assert find_nth_weekday_in_range(calendar, 1, 15, 21, THURSDAY) == "1/16"
    assert find_nth_weekday_in_range(calendar, 1, 15, 15, MONDAY) is None


def test_get_official_us_holidays_marks_observed_and_floating_holidays():
    calendar = get_official_us_holidays(generate_year_calendar(2021, "FRIDAY"))

    assert calendar["1/1"] == HOLIDAY
    assert calendar["1/18"] == HOLIDAY
    assert calendar["5/31"] == HOLIDAY
    assert calendar["7/5"] == HOLIDAY
    assert calendar["11/25"] == HOLIDAY
    assert calendar["12/24"] == HOLIDAY
    assert calendar["12/31"] == HOLIDAY


def test_get_official_us_holidays_marks_monday_observed_new_year():
    calendar = get_official_us_holidays(generate_year_calendar(2023, "SUNDAY"))

    assert calendar["1/2"] == HOLIDAY


def test_get_alternate_holidays_accepts_numeric_strings():
    calendar = generate_year_calendar(2025, "WEDNESDAY")

    updated = get_alternate_holidays(calendar, ["2.0", 8], ["14.0", 1])

    assert updated["2/14"] == HOLIDAY
    assert updated["8/1"] == HOLIDAY
