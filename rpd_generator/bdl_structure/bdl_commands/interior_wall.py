from rpd_generator.bdl_structure.parent_node import ParentNode
from rpd_generator.bdl_structure.child_node import ChildNode


class InteriorWall(
    ChildNode, ParentNode
):  # Inherit ChildNode first so that the MRO does not try to call ParentNode.__init__ twice
    """InteriorWall object in the tree."""

    bdl_command = "INTERIOR-WALL"

    def __init__(self, u_name, parent):
        super().__init__(u_name, parent)

    def __repr__(self):
        return f"InteriorWall(obj_id='{self.obj_id}', parent={self.parent.__class__.__name__}('{self.parent.u_name}')"

    def populate_schema_structure(self):
        """Populate schema structure for interior wall object."""
        return {}
