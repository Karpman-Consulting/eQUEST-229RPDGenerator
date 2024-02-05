from rpd_generator.bdl_structure.base_definition import BaseDefinition


class GlobalParams(BaseDefinition):
    """GlobalParams object in the tree."""

    bdl_command = "GLOBAL-PARAMS"

    def __init__(self, u_name):
        super().__init__(u_name)

    def __repr__(self):
        return f"GlobalParams('{self.u_name}')"

    def populate_schema_structure(self):
        """Populate schema structure for global params object."""
        return {}
