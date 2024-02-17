from rpd_generator.bdl_structure.base_definition import BaseDefinition


class GlassType(BaseDefinition):
    """GlassType object in the tree."""

    bdl_command = "GLASS-TYPE"

    def __init__(self, u_name, rmd):
        super().__init__(u_name, rmd)

    def __repr__(self):
        return f"GlassType(u_name='{self.u_name}')"

    def populate_data_elements(self):
        """Populate schema structure for glass type object."""
        pass
