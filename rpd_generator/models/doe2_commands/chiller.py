from rpd_generator.models.base_node import BaseNode


class Chiller(BaseNode):
    """Chiller object in the tree."""

    def __init__(self, obj_id):
        super().__init__(obj_id)

    def populate_schema_structure(self):
        """Populate schema structure for chiller object."""
        return {}
