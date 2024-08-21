from rpd_generator.bdl_structure.base_definition import BaseDefinition
from rpd_generator.bdl_structure.bdl_enumerations.bdl_enums import BDLEnums


BDL_Commands = BDLEnums.bdl_enums["Commands"]


class MasterMeters(BaseDefinition):

    bdl_command = BDL_Commands.MASTER_METERS

    def __init__(self, u_name, rmd):
        super().__init__(u_name, rmd)

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
