from rpd_generator.bdl_structure.parent_node import ParentNode


class System(ParentNode):
    """System object in the tree."""

    bdl_command = "SYSTEM"

    def __init__(self, u_name):
        super().__init__(u_name)

    def __repr__(self):
        return f"System({self.obj_id})"

    def populate_schema_structure(self):
        """Populate schema structure for system object."""
        return {}
