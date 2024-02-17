from rpd_generator.bdl_structure.base_definition import BaseDefinition


class MasterMeters(BaseDefinition):

    bdl_command = "MASTER-METERS"

    def __init__(self, u_name):
        super().__init__(u_name)

    def __repr__(self):
        return f"MasterMeters(u_name='{self.u_name}')"

    def populate_data_elements(self):
        """Populate data elements from master meters object."""
        return {}


class FuelMeter(BaseDefinition):

    bdl_command = "FUEL-METER"

    def __init__(self, u_name):
        super().__init__(u_name)

    def __repr__(self):
        return f"FuelMeter(u_name='{self.u_name}')"

    def populate_data_elements(self):
        """Populate data elements from fuel meter object."""
        return {}


class ElecMeter(BaseDefinition):

    bdl_command = "ELEC-METER"

    def __init__(self, u_name):
        super().__init__(u_name)

    def __repr__(self):
        return f"ElecMeter(u_name='{self.u_name}')"

    def populate_data_elements(self):
        """Populate data elements from electric meter object."""
        return {}


class SteamMeter(BaseDefinition):

    bdl_command = "STEAM-METER"

    def __init__(self, u_name):
        super().__init__(u_name)

    def __repr__(self):
        return f"SteamMeter(u_name='{self.u_name}')"

    def populate_data_elements(self):
        """Populate data elements from steam meter object."""
        return {}


class CHWMeter(BaseDefinition):

    bdl_command = "CHW-METER"

    def __init__(self, u_name):
        super().__init__(u_name)

    def __repr__(self):
        return f"CHWMeter(u_name='{self.u_name}')"

    def populate_data_elements(self):
        """Populate data elements from chilled water meter object."""
        return {}
