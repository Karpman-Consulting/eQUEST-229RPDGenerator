from rpd_generator.models.base_definition import BaseDefinition


class Floor(BaseDefinition):
    """Floor object in the tree."""

    bdl_command = "FLOOR"

    def __init__(self, u_name):
        super().__init__(u_name)

    def __repr__(self):
        return f"Floor('{self.u_name}')"
