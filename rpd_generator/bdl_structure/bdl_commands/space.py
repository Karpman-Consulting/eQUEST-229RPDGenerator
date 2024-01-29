from rpd_generator.bdl_structure.parent_definition import ParentDefinition
from rpd_generator.bdl_structure.child_node import ChildNode


class Space(
    ChildNode, ParentDefinition
):
    """Space object in the tree."""

    bdl_command = "SPACE"

    def __init__(self, u_name, parent):
        super().__init__(u_name, parent)
        ParentDefinition.__init__(self, u_name)

    def __repr__(self):
        parent_repr = (
            f"{self.parent.__class__.__name__}('{self.parent.u_name}')"
            if self.parent
            else "None"
        )
        return f"Space(obj_id='{self.obj_id}', parent={parent_repr})"

    def populate_schema_structure(self):
        """Populate schema structure for space object."""
        return {}
