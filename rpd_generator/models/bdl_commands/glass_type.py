from rpd_generator.models.base_definition import BaseDefinition


class GlassType(BaseDefinition):
    """GlassType object in the tree."""

    bdl_command = "GLASS-TYPE"

    def __init__(self, u_name):
        super().__init__(u_name)

    def __repr__(self):
        return f"GlassType('{self.u_name}')"
