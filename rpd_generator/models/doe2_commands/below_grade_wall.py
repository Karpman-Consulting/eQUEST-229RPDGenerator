from rpd_generator.models.child_node import ChildNode


class BelowGradeWall(ChildNode):
    """BelowGradeWall object in the tree."""

    def __init__(self, obj_id, parent):
        super().__init__(obj_id, parent)

    def populate_schema_structure(self):
        """Populate schema structure for below grade wall object."""
        return {}
