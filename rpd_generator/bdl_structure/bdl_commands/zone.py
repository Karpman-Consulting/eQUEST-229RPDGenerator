from rpd_generator.bdl_structure.child_node import ChildNode


class Zone(ChildNode):
    """Zone object in the tree."""

    bdl_command = "ZONE"

    def __init__(self, u_name, parent):
        super().__init__(u_name, parent)

    def __repr__(self):
        return f"Zone(u_name='{self.u_name}', parent={self.parent.__class__.__name__}('{self.parent.u_name}'))"

    def populate_schema_structure(self):
        """Populate schema structure for zone object."""
        return {}
