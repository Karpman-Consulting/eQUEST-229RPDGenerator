from rpd_generator.models.base_node import BaseNode


class Boiler(BaseNode):
    """Boiler object in the tree."""

    bdl_command = "BOILER"

    def __init__(self, u_name):
        super().__init__(u_name)

    def __repr__(self):
        return f"Boiler('{self.obj_id}')"

    def populate_schema_structure(self):
        """Populate schema structure for boiler object."""
        return {}


boiler = Boiler("boiler")
print(boiler)