from rpd_generator.models.base_node import BaseNode


class Door(BaseNode):
    """Door object in the tree."""

    bdl_command = "DOOR"

    def __init__(self, u_name):
        super().__init__(u_name)

    def __repr__(self):
        return f"Door({self.obj_id})"

    def populate_schema_structure(self):
        """Populate schema structure for door object."""
        return {}
