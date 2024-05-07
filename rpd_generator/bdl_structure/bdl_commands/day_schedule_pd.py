from rpd_generator.bdl_structure.base_definition import BaseDefinition


class DaySchedulePD(BaseDefinition):
    """DaySchedulePD object in the tree."""

    bdl_command = "DAY-SCHEDULE-PD"

    def __init__(self, u_name, rmd):
        super().__init__(u_name, rmd)

        # data elements with no children
        self.hourly_values = []


    def __repr__(self):
        return f"DaySchedulePD(u_name='{self.u_name}')"



