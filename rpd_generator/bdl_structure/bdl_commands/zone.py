from rpd_generator.bdl_structure.child_node import ChildNode


class Zone(ChildNode):
    """Zone object in the tree."""

    bdl_command = "ZONE"

    def __init__(self, u_name, parent):
        super().__init__(u_name, parent)

    def __repr__(self):
        return f"Zone(obj_id='{self.obj_id}', parent={self.parent.__class__.__name__}('{self.parent.obj_id}'))"

    def populate_schema_structure(self):
        """Populate schema structure for zone object."""
        return {}
