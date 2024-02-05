from rpd_generator.models.base_definition import BaseDefinition


class EquipCtrl(BaseDefinition):
    """EquipCtrl object in the tree."""

    bdl_command = "EQUIP-CTRL"

    def __init__(self, u_name):
        super().__init__(u_name)

    def __repr__(self):
        return f"EquipCtrl('{self.u_name}')"