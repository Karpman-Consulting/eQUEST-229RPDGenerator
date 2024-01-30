from rpd_generator.bdl_structure.parent_node import ParentNode
from rpd_generator.bdl_structure.child_node import ChildNode


class ExteriorWall(
    ChildNode, ParentNode
):
    """ExteriorWall object in the tree."""

    bdl_command = "EXTERIOR-WALL"

    def __init__(self, u_name, parent):
        super().__init__(u_name, parent)

    def __repr__(self):
        parent_repr = (
            f"{self.parent.__class__.__name__}('{self.parent.u_name}')"
            if self.parent
            else "None"
        )
        return f"ExteriorWall(u_name='{self.u_name}', parent={parent_repr})"

    def populate_schema_structure(self):
        """Populate schema structure for exterior wall object."""
        return {}