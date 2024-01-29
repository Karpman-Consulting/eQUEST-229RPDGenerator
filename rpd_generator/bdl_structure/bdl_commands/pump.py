from rpd_generator.bdl_structure.base_node import BaseNode


class Pump(BaseNode):
    """Pump object in the tree."""

    bdl_command = "PUMP"

    def __init__(self, u_name):
        super().__init__(u_name)

    def __repr__(self):
        return f"Pump({self.obj_id})"

    def populate_schema_structure(self):
        """Populate schema structure for pump object."""
        return {}
