from rpd_generator.bdl_structure.base_node import BaseNode


class Construction(BaseNode):
    """Construction object in the tree."""

    bdl_command = "CONSTRUCTION"

    def __init__(self, u_name, rmd):
        super().__init__(u_name, rmd)

        self.construction_data_structure = {}
        self.material_references = None

        # data elements with children
        self.primary_layers = []
        self.framing_layers = []
        self.insulation_locations = []
        self.r_values = []

        # data elements with no children
        self.classification = None
        self.surface_construction_input_option = None
        self.fraction_framing = None
        self.u_factor = None
        self.c_factor = None
        self.f_factor = None
        self.has_radiant_heating = None
        self.has_radiant_cooling = None

    def __repr__(self):
        return f"Construction(u_name='{self.u_name}')"

    def populate_data_elements(self):
        """Populate data elements for construction object."""
        layer_reference = self.keyword_value_pairs.get("LAYERS")
        layer = (
            self.rmd.bdl_obj_instances.get(layer_reference) if layer_reference else None
        )
        self.material_references = layer.material_references if layer else None
        self.material_references = (
            self.material_references if self.material_references else []
        )

        for material_reference in self.material_references:
            material = self.rmd.bdl_obj_instances.get(material_reference)
            if material:
                self.primary_layers.append(material.material_data_structure)

    def populate_data_group(self):
        """Populate schema structure for construction object."""
        self.construction_data_structure = {
            "id": self.u_name,
            "primary_layers": self.primary_layers,
            "framing_layers": self.framing_layers,
            "insulation_locations": self.insulation_locations,
            "r_values": self.r_values,
        }

        no_children_attributes = [
            "reporting_name",
            "notes",
            "classification",
            "surface_construction_input_option",
            "fraction_framing",
            "u_factor",
            "c_factor",
            "f_factor",
            "has_radiant_heating",
            "has_radiant_cooling",
        ]

        # Iterate over the no_children_attributes list and populate if the value is not None
        for attr in no_children_attributes:
            value = getattr(self, attr, None)
            if value is not None:
                self.construction_data_structure[attr] = value
