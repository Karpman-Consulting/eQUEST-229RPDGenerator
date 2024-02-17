from rpd_generator.bdl_structure.base_definition import BaseDefinition


class LightingSystem(BaseDefinition):
    """LightingSystem object in the tree."""

    bdl_command = "LIGHTING-SYSTEM"

    def __init__(self, u_name, rmd):
        super().__init__(u_name, rmd)

    def __repr__(self):
        return f"LightingSystem('{self.u_name}')"
