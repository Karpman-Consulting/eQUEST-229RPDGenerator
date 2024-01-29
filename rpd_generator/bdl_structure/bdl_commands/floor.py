from rpd_generator.bdl_structure.parent_definition import ParentDefinition


class Floor(ParentDefinition):
    """Floor object in the tree."""

    bdl_command = "FLOOR"

    def __init__(self, u_name):
        super().__init__(u_name)

    def __repr__(self):
        return f"Floor('{self.u_name}')"
