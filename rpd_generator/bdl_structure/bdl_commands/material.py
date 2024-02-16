from rpd_generator.bdl_structure.base_node import BaseNode


class Material(BaseNode):
    """Material object in the tree."""

    bdl_command = "MATERIAL"

    def __init__(self, u_name, rmd):
        super().__init__(u_name, rmd)

        self.material_data_structure = {}

        # data elements with no children
        self.thickness = None
        self.thermal_conductivity = None
        self.density = None
        self.specific_heat = None
        self.r_value = None

    def __repr__(self):
        return f"Material(u_name='{self.u_name}')"

    def populate_data_elements(self):
        """Populate data elements for material object."""
        self.thickness = self.keyword_value_pairs.get("THICKNESS")
        if self.thickness is not None:
            self.thickness = float(self.thickness)

        self.thermal_conductivity = self.keyword_value_pairs.get("CONDUCTIVITY")
        if self.thermal_conductivity is not None:
            self.thermal_conductivity = float(self.thermal_conductivity)

        self.density = self.keyword_value_pairs.get("DENSITY")
        if self.density is not None:
            self.density = float(self.density)

        self.specific_heat = self.keyword_value_pairs.get("SPECIFIC-HEAT")
        if self.specific_heat is not None:
            self.specific_heat = float(self.specific_heat)

        self.r_value = self.keyword_value_pairs.get("RESISTANCE")
        if self.r_value is not None:
            self.r_value = float(self.r_value)

    def populate_data_group(self):
        """Populate schema structure for material object."""
        self.material_data_structure = {
            "id": self.u_name,
        }

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
                self.material_data_structure[attr] = value

    def insert_to_rpd(self, rmd):
        """Insert window object into the rpd data structure."""
