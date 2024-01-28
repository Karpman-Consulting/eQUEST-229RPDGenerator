from rpd_generator.models.parent_node import ParentNode
from rpd_generator.models.child_node import ChildNode


class Space(ParentNode, ChildNode):
    """Space object in the tree."""

    def __init__(self, parent):
        super().__init__(parent)

    def populate_schema_structure(self):
        """Populate schema structure for space object."""
        return {}
