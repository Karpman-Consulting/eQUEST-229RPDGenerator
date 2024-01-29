from rpd_generator.bdl_structure.base_node import BaseNode


class Schedule(BaseNode):
    """Schedule object in the tree."""

    bdl_command = "SCHEDULE-PD"

    def __init__(self, u_name):
        super().__init__(u_name)

    def __repr__(self):
        return f"Schedule({self.obj_id})"

    def populate_schema_structure(self):
        """Populate schema structure for schedule object."""
        return {}
