from rpd_generator.bdl_structure.base_node import BaseNode


class Material(BaseNode):
    """Material object in the tree."""

    bdl_command = "MATERIAL"

    def __init__(self, u_name):
        super().__init__(u_name)

        self.material_data_structure = {}

        # data elements with no children
        self.thickness = None
        self.thermal_conductivity = None
        self.density = None
        self.specific_heat = None
        self.r_value = None

    def __repr__(self):
        return f"Material({self.u_name})"

    def populate_data_group(self):
        """Populate schema structure for material object."""
        no_children_attributes = [
            "reporting_name",
            "notes",
            "thickness",
            "thermal_conductivity",
            "density",
            "specific_heat",
            "r_value",
        ]

        # Iterate over the no_children_attributes list and populate if the value is not None
        for attr in no_children_attributes:
            value = getattr(self, attr, None)
            if value is not None:
                self.material_data_structure[self.u_name][attr] = value

    def insert_to_rpd(self, rmd):
        """Insert window object into the rpd data structure."""
