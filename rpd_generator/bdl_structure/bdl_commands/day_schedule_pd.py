from rpd_generator.bdl_structure.base_definition import BaseDefinition


class DaySchedulePD(BaseDefinition):
    """DaySchedulePD object in the tree."""

    bdl_command = "DAY-SCHEDULE-PD"

    def __init__(self, u_name):
        super().__init__(u_name)

    def __repr__(self):
        return f"DaySchedulePD(u_name='{self.u_name}')"

    def populate_schema_structure(self):
        """Populate schema structure for day schedule PD object."""
        return {}
