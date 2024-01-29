from rpd_generator.bdl_structure.base_definition import BaseDefinition


class WeekSchedulePD(BaseDefinition):
    """WeekSchedulePD object in the tree."""

    bdl_command = "WEEK-SCHEDULE-PD"

    def __init__(self, u_name):
        super().__init__(u_name)

    def __repr__(self):
        return f"WeekSchedulePD('{self.u_name}')"
