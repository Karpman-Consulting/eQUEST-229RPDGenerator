def get_day_of_week_jan_1(year: int) -> str:
    """
    Get the day of the week for January 1st of a given year using Zeller's Congruence method.
    :param year: (int) The year to get the day of the week for
    :return: day_of_week (str): "MONDAY", "TUESDAY", etc.
    """
    # Adjustments for January
    q = 1  # Day of the month
    m = 13  # Month (January is treated as the 13th month of the previous year)
    year -= 1  # Adjust year since January is treated as part of the previous year

    # Zeller's Congruence components
    k = year % 100  # Year of the century
    j = year // 100  # Zero-based century
    # Zeller's Congruence for Gregorian calendar
    h = (q + ((13 * (m + 1)) // 5) + k + (k // 4) + (j // 4) - (2 * j)) % 7

    # Convert Zeller's result to weekday with 0 = Monday, 1 = Tuesday, ..., 6 = Sunday
    day_of_week = (h + 5) % 7

    days = [
        "MONDAY",
        "TUESDAY",
        "WEDNESDAY",
        "THURSDAY",
        "FRIDAY",
        "SATURDAY",
        "SUNDAY",
    ]

    return days[day_of_week]


def is_leap_year(year: int) -> bool:
    """
    Determine if a year is a leap year.
    :param year:
    :return: True/False boolean
    """
    return (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0)


def generate_year_calendar(year: int, first_day: str) -> dict:
    """
    Generate a dictionary of days in a year with day types.
    :param year:
    :param first_day:
    :return: dictionary of days in a year with day types
    """
    first_day = ["MONDAY", "TUESDAY", "WEDNESDAY", "THURSDAY", "FRIDAY", "SATURDAY", "SUNDAY"].index(first_day) + 1
    calendar = {}
    day_types = [7, 1, 2, 3, 4, 5, 6]
    day_type = None

    month_days = [
        31,
        28 if not is_leap_year(year) else 29,
        31,
        30,
        31,
        30,
        31,
        31,
        30,
        31,
        30,
        31,
    ]
    m = 0
    d = 1

    days_left_in_month = month_days[m]

    for i in range(366 if is_leap_year(year) else 365):
        days_left_in_month -= 1

        if (i + first_day) % 7 == 0:
            day_type = 7
        else:
            day_type = day_types[(i + first_day) % 7]

        calendar[f"{m+1}/{d}"] = day_type

        if days_left_in_month > 0:
            d += 1
        else:
            m += 1
            d = 1
            if m < 12:
                days_left_in_month = month_days[m]

    return calendar


def get_official_us_holidays(calendar: dict) -> dict:
    """
    Set official US holidays to type 8 in the calendar dictionary returned by `generate_year_calendar()`.
    :param calendar:
    :return: calendar with official US holidays set to type 8
    """
    # New Year's Day
    if calendar["12/31"] == 5:
        calendar["12/31"] = 8
    elif calendar["1/1"] not in [6, 7]:
        calendar["1/1"] = 8
    elif calendar["1/2"] == 1:
        calendar["1/2"] = 8

    # M.L. King Birthday (Third Monday in January)
    for i in range(15, 22):
        if calendar[f"1/{i}"] == 1:
            calendar[f"1/{i}"] = 8

    # Washington's Birthday (Third Monday in February)
    for i in range(15, 22):
        if calendar[f"2/{i}"] == 1:
            calendar[f"2/{i}"] = 8

    # Memorial Day (Last Monday in May)
    for i in range(25, 32):
        if calendar[f"5/{i}"] == 1:
            calendar[f"5/{i}"] = 8

    # Fourth of July
    if calendar["7/3"] == 5:
        calendar["7/3"] = 8
    elif calendar["7/4"] not in [6, 7]:
        calendar["7/4"] = 8
    elif calendar["7/5"] == 1:
        calendar["7/5"] = 8

    # Labor Day (First Monday in September)
    for i in range(1, 8):
        if calendar[f"9/{i}"] == 1:
            calendar[f"9/{i}"] = 8

    # Columbus Day (Second Monday in October)
    for i in range(8, 15):
        if calendar[f"10/{i}"] == 1:
            calendar[f"10/{i}"] = 8

    # Veterans Day
    if calendar["11/10"] == 5:
        calendar["11/10"] = 8
    elif calendar["11/11"] not in [6, 7]:
        calendar["11/11"] = 8
    elif calendar["11/12"] == 1:
        calendar["11/12"] = 8

    # Thanksgiving (Fourth Thursday in November)
    for i in range(22, 29):
        if calendar[f"11/{i}"] == 4:
            calendar[f"11/{i}"] = 8

    # Christmas
    if calendar["12/24"] == 5:
        calendar["12/24"] = 8
    elif calendar["12/25"] not in [6, 7]:
        calendar["12/25"] = 8
    elif calendar["12/26"] == 1:
        calendar["12/26"] = 8

    return calendar
