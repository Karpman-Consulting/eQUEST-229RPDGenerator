from rpd_generator.bdl_structure.base_node import BaseNode
from rpd_generator.bdl_structure.base_definition import BaseDefinition


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
        self.thickness = self.try_float(self.keyword_value_pairs.get("THICKNESS"))

        self.thermal_conductivity = self.try_float(
            self.keyword_value_pairs.get("CONDUCTIVITY")
        )

        self.density = self.try_float(self.keyword_value_pairs.get("DENSITY"))

        self.specific_heat = self.try_float(
            self.keyword_value_pairs.get("SPECIFIC-HEAT")
        )

        self.r_value = self.try_float(self.keyword_value_pairs.get("RESISTANCE"))

    def populate_data_group(self):
        """Populate schema structure for material object."""
        self.material_data_structure["id"] = self.u_name

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


class Layers(BaseDefinition):
    """Layers object in the tree."""

    bdl_command = "LAYERS"

    def __init__(self, u_name, rmd):
        super().__init__(u_name, rmd)

        self.material_references = None

    def __repr__(self):
        return f"Layers(u_name='{self.u_name}')"

    def populate_data_elements(self):
        """Populate data elements for layers object."""
        material_references = self.keyword_value_pairs.get("MATERIAL")
        self.material_references = (
            material_references if isinstance(material_references, list) else []
        )
