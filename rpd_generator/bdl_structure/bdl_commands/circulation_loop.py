from rpd_generator.bdl_structure.base_node import BaseNode


class CirculationLoop(BaseNode):
    """CirculationLoop object in the tree."""

    bdl_command = "CIRCULATION-LOOP"

    def __init__(self, u_name):
        super().__init__(u_name)

    def __repr__(self):
        return f"CirculationLoop({self.obj_id})"

    def populate_schema_structure(self):
        """Populate schema structure for circulation loop object."""
        return {}
