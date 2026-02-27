import unittest

from rpd_generator.utilities.ashrae9012019.g311_exceptions.g311_sub_functions.get_zone_eflh import (
    get_zone_eflh,
)


def _weekly_workday_schedule(hours_per_day: int = 8) -> list[float]:
    values = [0.0] * 168
    for day in range(5):  # weekdays
        start = day * 24 + 8
        for hour in range(start, start + hours_per_day):
            values[hour] = 1.0
    return values


class TestGetZoneEflh(unittest.TestCase):
    def test_missing_fan_schedule_is_not_treated_as_continuous(self):
        occupant_schedule = _weekly_workday_schedule(hours_per_day=8)

        rmd = {
            "schedules": [
                {"id": "OccSched", "hourly_values": occupant_schedule},
            ]
        }
        zone = {
            "id": "Z1",
            "terminals": [
                {"served_by_heating_ventilating_air_conditioning_system": "SYS1"}
            ],
            "spaces": [
                {
                    "number_of_occupants": 10,
                    "occupant_multiplier_schedule": "OccSched",
                }
            ],
        }
        hvac_systems_map = {
            "SYS1": {
                "id": "SYS1",
                "fan_system": {
                    # No operating_schedule on purpose.
                },
            }
        }

        self.assertEqual(get_zone_eflh(rmd, zone, hvac_systems_map=hvac_systems_map), 0)


if __name__ == "__main__":
    unittest.main()
