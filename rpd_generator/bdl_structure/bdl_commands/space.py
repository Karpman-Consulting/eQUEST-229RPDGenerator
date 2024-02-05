from rpd_generator.bdl_structure.parent_node import ParentNode
from rpd_generator.bdl_structure.child_node import ChildNode


class Space(ChildNode, ParentNode):
    """Space object in the tree."""

    bdl_command = "SPACE"

    def __init__(self, u_name, parent):
        super().__init__(u_name, parent)
        ParentNode.__init__(self, u_name)

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
        parent_repr = (
            f"{self.parent.__class__.__name__}('{self.parent.u_name}')"
            if self.parent
            else "None"
        )
        return f"Space(u_name='{self.u_name}', parent={parent_repr})"

    def populate_data_group(self):
        """Populate schema structure for space object."""
        self.space_data_structure[self.u_name] = {
            "interior_lighting": self.interior_lighting,
            "miscellaneous_equipment": self.miscellaneous_equipment,
            "service_water_heating_uses": self.service_water_heating_uses,
        }

    def insert_to_rpd(self, zone):
        """Insert space object into the rpd data structure."""
        zone.spaces.append(self)
