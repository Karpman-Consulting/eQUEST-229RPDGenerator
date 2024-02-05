from rpd_generator.bdl_structure.base_definition import BaseDefinition


class DesignDay(BaseDefinition):
    """DesignDay class"""

    bdl_command = "DESIGN-DAY"

    def __init__(self, u_name):
        super().__init__(u_name)

    def __repr__(self):
        return f"DesignDay('{self.u_name}')"

    def populate_schema_structure(self):
        """Populate schema structure for design day object."""
        return {}
