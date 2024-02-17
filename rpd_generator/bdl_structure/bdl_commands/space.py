from rpd_generator.bdl_structure.parent_node import ParentNode
from rpd_generator.bdl_structure.child_node import ChildNode


class Space(ChildNode, ParentNode):
    """Space object in the tree."""

    bdl_command = "SPACE"

    def __init__(self, u_name, parent, rmd):
        super().__init__(u_name, parent, rmd)
        ParentNode.__init__(self, u_name, rmd)

        self.space_data_structure = {}

        # data elements with children
        self.interior_lighting = []
        self.miscellaneous_equipment = []
        self.service_water_heating_uses = []

        # data elements with no children
        self.floor_area = None
        self.number_of_occupants = None
        self.occupant_multiplier_schedule = None
        self.occupant_sensible_heat_gain = None
        self.occupant_latent_heat_gain = None
        self.status_type = None
        self.function = None
        self.envelope_space_type = None
        self.lighting_space_type = None
        self.ventilation_space_type = None
        self.service_water_heating_space_type = None

    def __repr__(self):
        return f"Space(u_name='{self.u_name}', parent={self.parent})"

    def populate_data_elements(self):
        """Populate data elements for space object."""
        self.floor_area = self.keyword_value_pairs.get("AREA")
        if self.floor_area is not None:
            self.floor_area = float(self.floor_area)

        volume = self.keyword_value_pairs.get("VOLUME")
        if volume is not None:
            volume = float(volume)
            zone = self.rmd.space_map.get(self.u_name)
            zone.__setattr__("volume", volume)

        self.number_of_occupants = self.keyword_value_pairs.get("NUMBER-OF-PEOPLE")
        if self.number_of_occupants is not None:
            self.number_of_occupants = float(self.number_of_occupants)

        self.occupant_multiplier_schedule = self.keyword_value_pairs.get(
            "PEOPLE-SCHEDULE"
        )

        self.occupant_sensible_heat_gain = self.keyword_value_pairs.get(
            "PEOPLE-HG-SENS"
        )
        if self.occupant_sensible_heat_gain is not None:
            self.occupant_sensible_heat_gain = float(self.occupant_sensible_heat_gain)

        self.occupant_latent_heat_gain = self.keyword_value_pairs.get("PEOPLE-HG-LAT")
        if self.occupant_latent_heat_gain is not None:
            self.occupant_latent_heat_gain = float(self.occupant_latent_heat_gain)

    def populate_data_group(self):
        """Populate schema structure for space object."""
        self.space_data_structure = {
            "id": self.u_name,
            "interior_lighting": self.interior_lighting,
            "miscellaneous_equipment": self.miscellaneous_equipment,
            "service_water_heating_uses": self.service_water_heating_uses,
        }

        no_children_attributes = [
            "reporting_name",
            "notes",
            "floor_area",
            "number_of_occupants",
            "occupant_multiplier_schedule",
            "occupant_sensible_heat_gain",
            "occupant_latent_heat_gain",
            "status_type",
            "function",
            "envelope_space_type",
            "lighting_space_type",
            "ventilation_space_type",
            "service_water_heating_space_type",
        ]

        # Iterate over the no_children_attributes list and populate if the value is not None
        for attr in no_children_attributes:
            value = getattr(self, attr, None)
            if value is not None:
                self.space_data_structure[attr] = value

    def insert_to_rpd(self, rmd):
        """Insert space object into the rpd data structure."""
        # find the zone that has the "SPACE" attribute value equal to the space object's u_name
        zone = rmd.space_map.get(self.u_name)
        zone.spaces.append(self.space_data_structure)
