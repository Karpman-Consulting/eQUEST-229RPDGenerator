from rpd_generator.bdl_structure.base_node import BaseNode

CHILLED_WATER = "CHILLED_WATER"
STEAM = "STEAM"
OTHER = "OTHER"


class SteamMeter(BaseNode):
    """Steam Meter object in the tree."""

    bdl_command = "STEAM-METER"

    def __init__(self, u_name, rmd):
        super().__init__(u_name, rmd)

        self.data_structure = {}

        # data elements with no children
        self.loop = None
        self.type = None
        self.energy_source_type = None

    def __repr__(self):
        return f"SteamMeter(u_name='{self.u_name}')"

    def populate_data_elements(self):
        """Populate data elements for ExternalFluidSource object."""
        self.loop = self.keyword_value_pairs.get("CIRCULATION-LOOP")
        self.type = STEAM
        self.energy_source_type = OTHER

    def populate_data_group(self):
        """Populate schema structure for ExternalFluidSource object."""
        self.data_structure = {
            "id": self.u_name,
        }

        no_children_attributes = [
            "reporting_name",
            "notes",
            "loop",
            "type",
            "energy_source_type",
        ]

        # Iterate over the no_children_attributes list and populate if the value is not None
        for attr in no_children_attributes:
            value = getattr(self, attr, None)
            if value is not None:
                self.data_structure[attr] = value

    def insert_to_rpd(self, rmd):
        rmd.external_fluid_sources.append(self.data_structure)


class CHWMeter(BaseNode):
    """Chiled Water Meter object in the tree."""

    bdl_command = "CHW-METER"

    def __init__(self, u_name, rmd):
        super().__init__(u_name, rmd)

        self.data_structure = {}

        # data elements with no children
        self.loop = None
        self.type = None
        self.energy_source_type = None

    def __repr__(self):
        return f"CHWMeter(u_name='{self.u_name}')"

    def populate_data_elements(self):
        """Populate data elements for ExternalFluidSource object."""
        self.loop = self.keyword_value_pairs.get("CIRCULATION-LOOP")
        self.type = CHILLED_WATER
        self.energy_source_type = OTHER

    def populate_data_group(self):
        """Populate schema structure for ExternalFluidSource object."""
        self.data_structure = {
            "id": self.u_name,
        }

        no_children_attributes = [
            "reporting_name",
            "notes",
            "loop",
            "type",
            "energy_source_type",
        ]

        # Iterate over the no_children_attributes list and populate if the value is not None
        for attr in no_children_attributes:
            value = getattr(self, attr, None)
            if value is not None:
                self.data_structure[attr] = value

    def insert_to_rpd(self, rmd):
        rmd.external_fluid_sources.append(self.data_structure)
