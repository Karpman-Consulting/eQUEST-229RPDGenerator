from rpd_generator.models.base_node import BaseNode


class DomesticWaterHeater(BaseNode):
    """DomesticWaterHeater object in the tree."""

    bdl_command = "DW-HEATER"

    def __init__(self, u_name):
        super().__init__(u_name)

    def __repr__(self):
        return f"DomesticWaterHeater({self.obj_id})"

    def populate_schema_structure(self):
        """Populate schema structure for domestic water heater object."""
        return {}