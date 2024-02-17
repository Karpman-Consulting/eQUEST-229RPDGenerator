from rpd_generator.bdl_structure.base_definition import BaseDefinition


class LoadManagement(BaseDefinition):
    """LoadManagement object in the tree."""

    bdl_command = "LOAD-MANAGEMENT"

    def __init__(self, u_name, rmd):
        super().__init__(u_name, rmd)

    def __repr__(self):
        return f"LoadManagement(u_name='{self.u_name}')"
