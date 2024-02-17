from rpd_generator.bdl_structure.base_definition import BaseDefinition


class EquipCtrl(BaseDefinition):
    """EquipCtrl object in the tree."""

    bdl_command = "EQUIP-CTRL"

    def __init__(self, u_name, rmd):
        super().__init__(u_name, rmd)

    def __repr__(self):
        return f"EquipCtrl(u_name='{self.u_name}')"
