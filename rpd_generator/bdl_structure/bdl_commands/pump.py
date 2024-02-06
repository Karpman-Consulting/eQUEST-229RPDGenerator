from rpd_generator.bdl_structure.base_node import BaseNode


class Pump(BaseNode):
    """Pump object in the tree."""

    bdl_command = "PUMP"

    def __init__(self, u_name):
        super().__init__(u_name)

        self.pump_data_structure = {}

        # data elements with children
        self.output_validation_points = []

        # data elements with no children
        self.loop_or_piping = None
        self.specification_method = None
        self.design_electric_power = None
        self.motor_nameplate_power = None
        self.design_head = None
        self.impeller_efficiency = None
        self.motor_efficiency = None
        self.speed_control = None
        self.design_flow = None
        self.is_flow_sized_bsed_on_design_day = None

    def __repr__(self):
        return f"Pump(u_name='{self.u_name}')"

    def populate_data_group(self):
        """Populate schema structure for pump object."""

        self.pump_data_structure = {
            "id": self.u_name,
            "output_validation_points": self.output_validation_points,
        }

        no_children_attributes = [
            "reporting_name",
            "notes",
            "loop_or_piping",
            "specification_method",
            "design_electric_power",
            "motor_nameplate_power",
            "design_head",
            "impeller_efficiency",
            "motor_efficiency",
            "speed_control",
            "design_flow",
            "is_flow_sized_based_on_design_day",
        ]

        # Iterate over the no_children_attributes list and populate if the value is not None
        for attr in no_children_attributes:
            value = getattr(self, attr, None)
            if value is not None:
                self.pump_data_structure[attr] = value

    def insert_to_rpd(self, rmd):
        """Insert window object into the rpd data structure."""
        rmd.pumps.append(self.pump_data_structure)
