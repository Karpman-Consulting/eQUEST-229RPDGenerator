from rpd_generator.models.base_definition import BaseDefinition


class LightingSystem(BaseDefinition):
    """LightingSystem object in the tree."""

    bdl_command = "LIGHTING-SYSTEM"

    def __init__(self, u_name):
        super().__init__(u_name)

    def __repr__(self):
        return f"LightingSystem('{self.u_name}')"
