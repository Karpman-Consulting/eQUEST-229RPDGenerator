from rpd_generator.bdl_structure.base_definition import BaseDefinition
from rpd_generator.utilities import schedule_funcs


class SiteParameters(BaseDefinition):
    bdl_command = "SITE-PARAMETERS"

    def __init__(self, u_name, rmd):
        super().__init__(u_name, rmd)

    def __repr__(self):
        return f"SitePameters(u_name='{self.u_name}')"

    def populate_data_elements(self):
        """Populate schema structure for site parameters object."""
        rpd = self.rmd.bdl_obj_instances["ASHRAE 229"]
        rpd.calendar.setdefault(
            "has_daylight_saving_time",
            self.boolean_map.get(self.keyword_value_pairs.get("DAYLIGHT-SAVINGS")),
        )


class RunPeriod(BaseDefinition):
    bdl_command = "RUN-PERIOD-PD"

    def __init__(self, u_name, rmd):
        super().__init__(u_name, rmd)

    def __repr__(self):
        return f"SitePameters(u_name='{self.u_name}')"

    def populate_data_elements(self):
        """Populate schema structure for site parameters object."""
        rpd = self.rmd.bdl_obj_instances["ASHRAE 229"]
        rpd.calendar.setdefault(
            "day_of_week_for_january_1",
            schedule_funcs.get_day_of_week_jan_1(
                int(float(self.keyword_value_pairs.get("END-YEAR")))
            ),
        )


class FixedShade(BaseDefinition):
    bdl_command = "FIXED-SHADE"

    has_site_shading = False

    def __init__(self, u_name, rmd):
        super().__init__(u_name, rmd)

        if not self.has_site_shading:
            self.has_site_shading = True
