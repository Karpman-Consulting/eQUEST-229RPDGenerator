from rpd_generator.models.base_node import BaseNode


class Chiller(BaseNode):
    """Chiller object in the tree."""

    bdl_command = "CHILLER"

    def __init__(self, u_name):
        super().__init__(u_name)

    def __repr__(self):
        return f"Chiller({self.obj_id})"

    def populate_schema_structure(self):
        """Populate schema structure for chiller object."""
        return {}
