from rpd_generator.bdl_structure.child_node import ChildNode


class BelowGradeWall(ChildNode):
    """BelowGradeWall object in the tree."""

    bdl_command = "UNDERGROUND-WALL"

    def __init__(self, u_name, parent):
        super().__init__(u_name, parent)

    def __repr__(self):
        return f"BelowGradeWall({self.u_name})"

    def populate_schema_structure(self):
        """Populate schema structure for below grade wall object."""
        return {}
