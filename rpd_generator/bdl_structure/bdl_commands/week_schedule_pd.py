from rpd_generator.bdl_structure.base_definition import BaseDefinition


class WeekSchedulePD(BaseDefinition):
    """WeekSchedulePD object in the tree."""

    bdl_command = "WEEK-SCHEDULE-PD"

    def __init__(self, u_name, rmd):
        super().__init__(u_name, rmd)

        # data elements with no children
        self.day_hourly_values = []

    def __repr__(self):
        return f"WeekSchedulePD(u_name='{self.u_name}')"

    def populate_data_elements(self):
        """Populate data elements that originate from eQUEST's WEEK-SCHEDULE-PD command"""
        """Create a list of 12 lists including Mon-Sun, Holidays and then 4 design day schedules"""
        wk_sch_type = self.keyword_value_pairs.get("TYPE")
        if wk_sch_type != "RESET-TEMP" and wk_sch_type != "RESET-RATIO":
            wk_sch_day_sch_list = self.keyword_value_pairs.get("DAY-SCHEDULES")
            self.day_hourly_values = [
                self.rmd.bdl_obj_instances[val].hourly_values
                for val in wk_sch_day_sch_list
            ]
