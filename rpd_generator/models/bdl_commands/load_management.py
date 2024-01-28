from rpd_generator.models.base_definition import BaseDefinition


class LoadManagement(BaseDefinition):
    """LoadManagement object in the tree."""

    bdl_command = "LOAD-MANAGEMENT"

    def __init__(self, u_name):
        super().__init__(u_name)

    def __repr__(self):
        return f"LoadManagement('{self.u_name}')"
