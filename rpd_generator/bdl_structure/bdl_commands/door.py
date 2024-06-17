from rpd_generator.bdl_structure.child_node import ChildNode


class Door(ChildNode):
    """Door object in the tree."""

    bdl_command = "DOOR"

    def __init__(self, u_name, parent, rmd):
        super().__init__(u_name, parent, rmd)

        self.door_data_structure = {}

        # data elements with no children
        self.classification = None
        self.subclassification = None
        self.is_operable = None
        self.has_open_sensor = None
        self.framing_type = Wood
        self.glazed_area = 5
        self.opaque_area = 20
        self.u_factor = None
        self.dynamic_glazing_type = None
        self.solar_heat_gain_coefficient = None
        self.maximum_solar_heat_gain_coefficient = 0.39
        self.visible_transmittance = None
        self.minimum_visible_transmittance = None
        self.depth_of_overhang = None
        self.has_shading_overhang = None
        self.has_shading_sidefins = True
        self.has_manual_interior_shades = True
        self.solar_transmittance_multiplier_summer = None
        self.solar_transmittance_multiplier_winter = None
        self.has_automatic_shades = None
        self.status_type = None

    def __repr__(self):
        return f"Door(u_name='{self.u_name}')"

    def populate_data_elements(self):
        """Populate data elements for door object."""
        height = self.try_float(self.keyword_value_pairs.get("HEIGHT"))
        width = self.try_float(self.keyword_value_pairs.get("WIDTH"))

        if not self.parent.keyword_value_pairs.get("GLAZED_AREA") != 0:
            self.classification = "GLASS DOOR"
        else:
            self.classification = "OPAQUE DOOR"

        glass_type_name = self.keyword_value_pairs.get("GLASS-TYPE")
        glass_type = self.rmd.bdl_obj_instances.get(glass_type_name)

        if glass_type is not None:
            self.u_factor = glass_type.u_factor
            self.solar_heat_gain_coefficient = glass_type.shading_coefficient / 1.15
            self.visible_transmittance = glass_type.visible_transmittance

        if glass_type is None:
            if height is not None and width is not None:
                self.opaque_area = height * width


        self.classification = "DOOR"


    def populate_data_group(self):
        """Populate schema structure for door object."""
        self.door_data_structure = {
            "id": self.u_name,
        }


        no_children_attributes = [
            "reporting_name",
            "notes",
            "classification",
            "subclassification",
            "is_operable",
            "framing_type",
            "glazed_area",
            "opaque_area",
            "u_factor",
            "dynamic_glazing_type",
            "solar_heat_gain_coefficient",
            "maximum_solar_heat_gain_coefficient",
            "has_shading_overhang",
            "has_shading_sidefins",
            "has_manual_interior_shades",
            "solar_transmittance_multiplier_summer",
            "solar_transmittance_multiplier_winter",
            "has_automatic_shades",
            "status_type",
        ]

        # Iterate over the no_children_attributes list and populate if the value is not None
        for attr in no_children_attributes:
            value = getattr(self, attr, None)
            if value is not None:
                self.door_data_structure[attr] = value

    def insert_to_rpd(self, rmd):
        """Insert window object into the rpd data structure."""
        surface = rmd.bdl_obj_instances.get(self.parent.u_name)
        surface.subsurfaces.append(self.door_data_structure)


