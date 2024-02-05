from rpd_generator.bdl_structure.base_definition import BaseDefinition


class EquipCtrl(BaseDefinition):
    """EquipCtrl object in the tree."""

    bdl_command = "EQUIP-CTRL"

    def __init__(self, u_name):
        super().__init__(u_name)

    def __repr__(self):
        return f"EquipCtrl('{self.u_name}')"

    def populate_schema_structure(self):
        """Populate schema structure for equip ctrl object."""
        return {}
