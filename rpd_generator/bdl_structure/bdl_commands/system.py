from rpd_generator.bdl_structure.parent_node import ParentNode


class System(ParentNode):
    """System object in the tree."""

    bdl_command = "SYSTEM"

    def __init__(self, u_name, rmd):
        super().__init__(u_name, rmd)
        # On initialization the parent building segment is not known. It will be set in the GUI.
        self.parent_building_segment = rmd.bdl_obj_instances.get(
            "Default Building Segment", None
        )

        self.system_data_structure = {}

        # data elements with children
        self.fan_systems = []
        self.heating_systems = []
        self.cooling_systems = []
        self.air_economizer = {}
        self.air_energy_recovery = {}

        # data elements with no children
        self.status_type = None

    def __repr__(self):
        return f"System(u_name='{self.u_name}')"

    def populate_data_group(self):
        """Populate schema structure for system object."""
        self.system_data_structure = {
            "id": self.u_name,
            "fan_systems": self.fan_systems,
            "heating_systems": self.heating_systems,
            "cooling_systems": self.cooling_systems,
            "air_economizer": self.air_economizer,
            "air_energy_recovery": self.air_energy_recovery,
        }

        no_children_attributes = [
            "reporting_name",
            "notes",
            "status_type",
        ]

        # Iterate over the no_children_attributes list and populate if the value is not None
        for attr in no_children_attributes:
            value = getattr(self, attr, None)
            if value is not None:
                self.system_data_structure[attr] = value

    def insert_to_rpd(self, rmd):
        """Insert zone object into the rpd data structure."""
        self.parent_building_segment.hvac_systems.append(self.system_data_structure)
