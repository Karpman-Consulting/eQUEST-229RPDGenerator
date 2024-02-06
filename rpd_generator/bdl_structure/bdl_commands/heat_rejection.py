from rpd_generator.bdl_structure.base_node import BaseNode


class HeatRejection(BaseNode):
    """Heat Rejection object in the tree."""

    bdl_command = "HEAT-REJECTION"

    def __init__(self, u_name):
        super().__init__(u_name)

        self.heat_rejection_data_structure = {}

        # data elements with no children
        self.loop = None
        self.type = None
        self.fan_type = None
        self.fluid = None
        self.range = None
        self.approach = None
        self.fan_shaft_power = None
        self.fan_motor_efficiency = None
        self.fan_motor_nameplate_power = None
        self.fan_speed_control = None
        self.design_wetbulb_temperature = None
        self.design_water_flowrate = None
        self.rated_water_flowrate = None
        self.leaving_water_setpoint_temperature = None

    def __repr__(self):
        return f"HeatRejection(u_name='{self.u_name}')"

    def populate_data_group(self):
        """Populate schema structure for heat rejection object."""
        self.heat_rejection_data_structure = {
            "id": self.u_name,
        }

        no_children_attributes = [
            "reporting_name",
            "notes",
            "loop",
            "type",
            "fan_type",
            "fluid",
            "range",
            "approach",
            "fan_shaft_power",
            "fan_motor_efficiency",
            "fan_motor_nameplate_power",
            "fan_speed_control",
            "design_wetbulb_temperature",
            "design_water_flowrate",
            "rated_water_flowrate",
            "leaving_water_setpoint_temperature",
        ]

        # Iterate over the no_children_attributes list and populate if the value is not None
        for attr in no_children_attributes:
            value = getattr(self, attr, None)
            if value is not None:
                self.heat_rejection_data_structure[attr] = value

    def insert_to_rpd(self, rmd):
        """Insert window object into the rpd data structure."""
        rmd.heat_rejections.append(self.heat_rejection_data_structure)
