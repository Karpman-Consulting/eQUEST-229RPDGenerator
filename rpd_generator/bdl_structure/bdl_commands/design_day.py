from rpd_generator.bdl_structure.base_definition import BaseDefinition
from rpd_generator.bdl_structure.bdl_enumerations.bdl_enums import BDLEnums


BDL_Commands = BDLEnums.bdl_enums["Commands"]


class DesignDay(BaseDefinition):
    """DesignDay class"""

    bdl_command = BDL_Commands.DESIGN_DAY

    def __init__(self, u_name, rmd):
        super().__init__(u_name, rmd)

    def __repr__(self):
        return f"DesignDay(u_name='{self.u_name}')"
