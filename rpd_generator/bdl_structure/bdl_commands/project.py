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
