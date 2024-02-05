from rpd_generator.bdl_structure.base_node import BaseNode


class Chiller(BaseNode):
    """Chiller object in the tree."""

    bdl_command = "CHILLER"

    def __init__(self, u_name):
        super().__init__(u_name)

        # data elements with children
        self.capacity_validation_points = []
        self.power_validation_points = []

        # data elements with no children
        self.cooling_loop = None
        self.condending_loop = None
        self.compressor_type = None
        self.energy_source_type = None
        self.design_capacity = None
        self.rated_capacity = None
        self.rated_entering_condenser_temperature = None
        self.rated_leaving_evaporator_temperature = None
        self.minimum_load_ratio = None
        self.design_flow_evaporator = None
        self.design_flow_condenser = None
        self.design_entering_condenser_temperature = None
        self.design_leaving_evaporator_temperature = None
        self.full_load_efficiency = None
        self.part_load_efficiency = None
        self.part_load_efficiency_metric = None
        self.is_chilled_water_pump_interlocked = None
        self.is_condenser_water_pump_interlocked = None
        self.heat_recovery_loop = None
        self.heat_recovery_fraction = None

    def __repr__(self):
        return f"Chiller({self.u_name})"

    def populate_data_group(self):
        """Populate schema structure for chiller object."""
        return {}
