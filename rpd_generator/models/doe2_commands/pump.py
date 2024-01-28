from rpd_generator.models.base_node import BaseNode


class Pump(BaseNode):
    """Pump object in the tree."""

    def __init__(self, obj_id):
        super().__init__(obj_id)

    def populate_schema_structure(self):
        """Populate schema structure for pump object."""
        return {}
