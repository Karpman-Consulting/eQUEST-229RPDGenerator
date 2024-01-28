from rpd_generator.models.parent_node import ParentNode


class System(ParentNode):
    """System object in the tree."""

    def __init__(self, obj_id):
        super().__init__(obj_id)

    def populate_schema_structure(self):
        """Populate schema structure for system object."""
        return {}
