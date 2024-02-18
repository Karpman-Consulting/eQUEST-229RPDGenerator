from rpd_generator.bdl_structure.base_node import BaseNode


class Chiller(BaseNode):
    """Chiller object in the tree."""

    bdl_command = "CHILLER"

    compressor_type_map = {
        "ELEC-OPEN-CENT": "CENTRIFUGAL",
        "ELEC-OPEN-REC": "RECIPROCATING",
        "ELEC-HERM-CENT": "CENTRIFUGAL",
        "ELEC-HERM-REC": "RECIPROCATING",
        "ELEC-SCREW": "SCREW",
        "ELEC-HTREC": "OTHER",
        "ABSOR-1": "SINGLE_EFFECT_DIRECT_FIRED_ABSORPTION",
        "ABSOR-2": "DOUBLE_EFFECT_DIRECT_FIRED_ABSORPTION",
        "GAS-ABSOR": "OTHER",
        "ENGINE": "OTHER",
        "HEAT-PUMP": "OMIT",  # Omit because it is not a chiller
        "LOOP-TO-LOOP-HP": "OMIT",  # Omit because it is not a chiller
        "WATER-ECONOMIZER": "OMIT",  # Omit because it is not a chiller
        "STRAINER-CYCLE": "OMIT",  # Omit because it is not a chiller
    }

    def __init__(self, u_name, rmd):
        super().__init__(u_name, rmd)

        self.chiller_data_structure = {}

        # data elements with children
        self.capacity_validation_points = []
        self.power_validation_points = []

        # data elements with no children
        self.cooling_loop = None
        self.condensing_loop = None
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
        return f"Chiller(u_name='{self.u_name}')"

    def populate_data_elements(self):
        """Populate data elements for chiller object."""
        self.cooling_loop = self.keyword_value_pairs.get("CHW-LOOP")

        self.condensing_loop = self.keyword_value_pairs.get("CW-LOOP")

        self.compressor_type = self.compressor_type_map.get(
            self.keyword_value_pairs.get("TYPE")
        )

    def populate_data_group(self):
        """Populate schema structure for chiller object."""
        self.chiller_data_structure = {
            "id": self.u_name,
            "capacity_validation_points": self.capacity_validation_points,
            "power_validation_points": self.power_validation_points,
        }

        no_children_attributes = [
            "cooling_loop",
            "condending_loop",
            "compressor_type",
            "energy_source_type",
            "design_capacity",
            "rated_capacity",
            "rated_entering_condenser_temperature",
            "rated_leaving_evaporator_temperature",
            "minimum_load_ratio",
            "design_flow_evaporator",
            "design_flow_condenser",
            "design_entering_condenser_temperature",
            "design_leaving_evaporator_temperature",
            "full_load_efficiency",
            "part_load_efficiency",
            "part_load_efficiency_metric",
            "is_chilled_water_pump_interlocked",
            "is_condenser_water_pump_interlocked",
            "heat_recovery_loop",
            "heat_recovery_fraction",
        ]

        # Iterate over the no_children_attributes list and populate if the value is not None
        for attr in no_children_attributes:
            value = getattr(self, attr, None)
            if value is not None:
                self.chiller_data_structure[attr] = value

    def insert_to_rpd(self, rmd):
        rmd.chillers.append(self.chiller_data_structure)
