from rpd_generator.bdl_structure.base_definition import BaseDefinition


class MasterMeters(BaseDefinition):

    bdl_command = "MASTER-METERS"

    def __init__(self, u_name, rmd):
        super().__init__(u_name, rmd)

    def __repr__(self):
        return f"MasterMeters(u_name='{self.u_name}')"


class FuelMeter(BaseDefinition):

    bdl_command = "FUEL-METER"

    def __init__(self, u_name, rmd):
        super().__init__(u_name, rmd)

    def __repr__(self):
        return f"FuelMeter(u_name='{self.u_name}')"


class ElecMeter(BaseDefinition):

    bdl_command = "ELEC-METER"

    def __init__(self, u_name, rmd):
        super().__init__(u_name, rmd)

    def __repr__(self):
        return f"ElecMeter(u_name='{self.u_name}')"


class SteamMeter(BaseDefinition):

    bdl_command = "STEAM-METER"

    def __init__(self, u_name, rmd):
        super().__init__(u_name, rmd)

    def __repr__(self):
        return f"SteamMeter(u_name='{self.u_name}')"


class CHWMeter(BaseDefinition):

    bdl_command = "CHW-METER"

    def __init__(self, u_name, rmd):
        super().__init__(u_name, rmd)

    def __repr__(self):
        return f"CHWMeter(u_name='{self.u_name}')"
