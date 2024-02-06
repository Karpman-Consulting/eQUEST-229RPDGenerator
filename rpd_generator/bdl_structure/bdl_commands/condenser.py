from rpd_generator.bdl_structure.base_definition import BaseDefinition


class Condenser(BaseDefinition):
    """Condenser object in the tree."""

    bdl_command = "CONDENSING-UNIT"

    def __init__(self, u_name):
        super().__init__(u_name)

    def __repr__(self):
        return f"Condenser(u_name='{self.u_name}')"

    def populate_schema_structure(self):
        """Populate schema structure for condenser object."""
        return {}
