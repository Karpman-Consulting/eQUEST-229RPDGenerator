from rpd_generator.bdl_structure.base_node import BaseNode
from rpd_generator.bdl_structure.base_definition import BaseDefinition
from rpd_generator.bdl_structure.bdl_enumerations.bdl_enums import BDLEnums


BDL_Commands = BDLEnums.bdl_enums["Commands"]
BDL_SteamAndCHWaterMeterKeywords = BDLEnums.bdl_enums[
    "SteamAndChilledWaterMeterKeywords"
]
CHILLED_WATER = "CHILLED_WATER"
STEAM = "STEAM"
OTHER = "OTHER"


class MasterMeters(BaseDefinition):

    bdl_command = BDL_Commands.MASTER_METERS

    def __init__(self, u_name, rmd):
        super().__init__(u_name, rmd)

        self.rmd.master_meters = u_name

    def __repr__(self):
        return f"MasterMeters(u_name='{self.u_name}')"


class FuelMeter(BaseDefinition):

    bdl_command = BDL_Commands.FUEL_METER

    def __init__(self, u_name, rmd):
        super().__init__(u_name, rmd)

    def __repr__(self):
        return f"FuelMeter(u_name='{self.u_name}')"


class ElecMeter(BaseDefinition):

    bdl_command = BDL_Commands.ELEC_METER

    def __init__(self, u_name, rmd):
        super().__init__(u_name, rmd)

    def __repr__(self):
        return f"ElecMeter(u_name='{self.u_name}')"


class SteamMeter(BaseNode):
    """Steam Meter object in the tree."""

    bdl_command = BDL_Commands.STEAM_METER

    def __init__(self, u_name, rmd):
        super().__init__(u_name, rmd)
        self.rmd.steam_meter_names.append(u_name)

        self.data_structure = {}

        # data elements with no children
        self.loop = None
        self.type = STEAM
        self.energy_source_type = OTHER

    def __repr__(self):
        return f"SteamMeter(u_name='{self.u_name}')"

    def populate_data_elements(self):
        """Populate data elements for ExternalFluidSource object."""
        self.loop = self.keyword_value_pairs.get(
            BDL_SteamAndCHWaterMeterKeywords.CIRCULATION_LOOP
        )

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

    bdl_command = BDL_Commands.CHW_METER

    def __init__(self, u_name, rmd):
        super().__init__(u_name, rmd)

        self.data_structure = {}

        # data elements with no children
        self.loop = None
        self.type = CHILLED_WATER
        self.energy_source_type = OTHER

    def __repr__(self):
        return f"CHWMeter(u_name='{self.u_name}')"

    def populate_data_elements(self):
        """Populate data elements for ExternalFluidSource object."""
        self.loop = self.keyword_value_pairs.get(
            BDL_SteamAndCHWaterMeterKeywords.CIRCULATION_LOOP
        )

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
