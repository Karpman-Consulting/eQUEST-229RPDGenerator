from rpd_generator.models.parent_node import ParentNode
from rpd_generator.models.child_node import ChildNode


class ExteriorWall(ChildNode, ParentNode):  # Inherit ChildNode first so that the MRO does not try to call ParentNode.__init__ twice
    """ExteriorWall object in the tree."""

    bdl_command = "EXTERIOR-WALL"

    def __init__(self, u_name, parent):
        super().__init__(u_name, parent)

    def __repr__(self):
        parent_repr = f"{self.parent.__class__.__name__}('{self.parent.obj_id}')" if self.parent else "None"
        return f"ExteriorWall(obj_id='{self.obj_id}', parent={parent_repr})"

    def populate_schema_structure(self):
        """Populate schema structure for exterior wall object."""
        return {}
