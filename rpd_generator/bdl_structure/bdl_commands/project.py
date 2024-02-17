from rpd_generator.bdl_structure.base_definition import BaseDefinition


class SiteParameters(BaseDefinition):
    bdl_command = "SITE-PARAMETERS"

    has_daylight_savings_map = {
        "YES": True,
        "NO": False,
    }

    def __init__(self, u_name, rmd):
        super().__init__(u_name, rmd)

    def __repr__(self):
        return f"SitePameters(u_name='{self.u_name}')"

    def populate_data_elements(self):
        """Populate schema structure for site parameters object."""
        rpd = self.rmd.bdl_obj_instances["ASHRAE 229"]
        rpd.calendar.setdefault("has_daylight_saving_time", self.has_daylight_savings_map.get(
            self.keyword_value_pairs.get("DAYLIGHT-SAVINGS")
        ))


class RunPeriod(BaseDefinition):
    bdl_command = "RUN-PERIOD-PD"

    def __init__(self, u_name, rmd):
        super().__init__(u_name, rmd)

    def __repr__(self):
        return f"SitePameters(u_name='{self.u_name}')"

    def populate_data_elements(self):
        """Populate schema structure for site parameters object."""
        rpd = self.rmd.bdl_obj_instances["ASHRAE 229"]
        rpd.calendar.setdefault("day_of_week_for_january_1", get_day_of_week_jan_1(
            int(float(self.keyword_value_pairs.get("END-YEAR")))
        ))


def get_day_of_week_jan_1(year):
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

    days = ["MONDAY", "TUESDAY", "WEDNESDAY", "THURSDAY", "FRIDAY", "SATURDAY", "SUNDAY"]

    return days[day_of_week]
