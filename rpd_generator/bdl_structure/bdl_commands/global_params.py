from rpd_generator.bdl_structure.base_definition import BaseDefinition


class GlobalParams(BaseDefinition):
    """GlobalParams object in the tree."""

    bdl_command = "GLOBAL-PARAMS"

    def __init__(self, u_name, rmd):
        super().__init__(u_name, rmd)

    def __repr__(self):
        return f"GlobalParams(u_name='{self.u_name}')"
