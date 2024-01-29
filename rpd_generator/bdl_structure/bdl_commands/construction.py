from rpd_generator.bdl_structure.base_node import BaseNode


class Construction(BaseNode):
    """Construction object in the tree."""

    bdl_command = "CONSTRUCTION"

    def __init__(self, u_name):
        super().__init__(u_name)

    def __repr__(self):
        return f"Construction({self.obj_id})"

    def populate_schema_structure(self):
        """Populate schema structure for construction object."""
        return {}
