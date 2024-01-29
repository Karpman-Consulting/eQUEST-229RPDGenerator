from rpd_generator.bdl_structure.child_node import ChildNode


class Door(ChildNode):
    """Door object in the tree."""

    bdl_command = "DOOR"

    def __init__(self, u_name, parent):
        super().__init__(u_name, parent)

    def __repr__(self):
        return f"Door({self.obj_id})"

    def populate_schema_structure(self):
        """Populate schema structure for door object."""
        return {}
