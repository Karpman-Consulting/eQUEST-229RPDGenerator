from rpd_generator.bdl_structure.base_definition import BaseDefinition
from rpd_generator.utilities import schedule_funcs

class WeekSchedulePD(BaseDefinition):
    """WeekSchedulePD object in the tree."""

    bdl_command = "WEEK-SCHEDULE-PD"

    def __init__(self, u_name, rmd):
        super().__init__(u_name, rmd)

        # data elements with no children
        self.day_type_hourly_values = []

    def __repr__(self):
        return f"WeekSchedulePD(u_name='{self.u_name}')"

    def populate_data_elements(self):
        """Populate data elements that originate from eQUEST's WEEK-SCHEDULE-PD command"""
        """Create a list of 12 lists including Mon-Sun, Holidays and then 4 design day schedules"""
        wk_sch_type = self.keyword_value_pairs.get("TYPE")
        if wk_sch_type in schedule_funcs.supported_schedules():
            day_schedule_names = self.keyword_value_pairs.get("DAY-SCHEDULES")
            self.day_type_hourly_values = [
                self.rmd.bdl_obj_instances[day_sch].hourly_values
                for day_sch in day_schedule_names
            ]
