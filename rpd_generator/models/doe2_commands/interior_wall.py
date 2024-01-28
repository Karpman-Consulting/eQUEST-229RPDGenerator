from rpd_generator.models.parent_node import ParentNode
from rpd_generator.models.child_node import ChildNode


class InteriorWall(ParentNode, ChildNode):
    """InteriorWall object in the tree."""

    def __init__(self, obj_id, parent):
        super().__init__(obj_id)
        ChildNode.__init__(self, obj_id, parent)

    def populate_schema_structure(self):
        """Populate schema structure for interior wall object."""
        return {}
