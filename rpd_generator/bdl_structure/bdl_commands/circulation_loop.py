from rpd_generator.bdl_structure.base_node import BaseNode


class CirculationLoop(BaseNode):
    """CirculationLoop object in the tree."""

    bdl_command = "CIRCULATION-LOOP"

    def __init__(self, u_name):
        super().__init__(u_name)

        # keep track of the type of circulation loop (different from self.type which is the FluidLoop type)
        self.circulation_loop_type = None

        # FluidLoop data
        self.fluid_loop_data_structure = {}

        # data elements with children
        self.cooling_or_condensing_design_and_control = {}
        self.heating_design_and_control = {}
        self.child_loops = []

        # data elements with no children
        self.type = None
        self.pump_power_per_flow_rate = None

        # ServiceWaterHeatingDistributionSystem data
        self.swh_distribution_data_structure = {}

        # data elements with children
        self.service_water_piping = None
        self.tanks = None

        # data elements with no children
        self.design_supply_temperature = None
        self.design_supply_temperature_difference = None
        self.is_central_system = None
        self.distribution_compactness = None
        self.control_type = None
        self.configuration_type = None
        self.is_recovered_heat_from_drain_used_by_water_heater = None
        self.drain_heat_recovery_efficiency = None
        self.drain_heat_recovery_type = None
        self.flow_multiplier_schedule = None
        self.entering_water_mains_temperature_schedule = None
        self.is_ground_temperature_used_for_entering_water = None

        # ServiceWaterPiping data
        self.swh_piping_data_structure = {}

        # data elements with no children
        self.is_recirculation_loop = None
        self.insulation_thickness = None
        self.loop_pipe_location = None
        self.location_zone = None
        self.length = None
        self.diameter = None
        # self.child = None   this is commented out because eQUEST can only have a single tier of secondary loops

    def __repr__(self):
        return f"CirculationLoop(u_name='{self.u_name}')"

    def populate_data_elements(self):
        """Populate data elements from the keyword_value pairs returned from model_input_reader"""
        self.determine_circ_loop_type()

    def populate_data_group(self):
        """Populate schema structure for circulation loop object."""
        if (
            self.keyword_value_pairs["TYPE"] == "DHW"
            and self.keyword_value_pairs["SUBTYPE"] == "SECONDARY"
        ):
            self.swh_piping_data_structure = {
                "id": self.u_name,
            }
        elif self.keyword_value_pairs["TYPE"] == "DHW":
            self.swh_distribution_data_structure = {
                "id": self.u_name,
                "tanks": self.tanks,
                "service_water_piping": self.service_water_piping,
            }
        else:
            self.fluid_loop_data_structure = {
                "id": self.u_name,
                "cooling_or_condensing_design_and_control": self.cooling_or_condensing_design_and_control,
                "heating_design_and_control": self.heating_design_and_control,
                "child_loops": self.child_loops,
            }

        no_children_attributes = [
            "reporting_name",
            "notes",
            "type",
            "pump_power_per_flow_rate",
            "design_supply_temperature",
            "design_supply_temperature_difference",
            "is_central_system",
            "distribution_compactness",
            "control_type",
            "configuration_type",
            "is_recovered_heat_from_drain_used_by_water_heater",
            "drain_heat_recovery_efficiency",
            "drain_heat_recovery_type",
            "flow_multiplier_schedule",
            "entering_water_mains_temperature_schedule",
            "is_ground_temperature_used_for_entering_water",
            "is_recirculation_loop",
            "insulation_thickness",
            "loop_pipe_location",
            "location_zone",
            "length",
            "diameter",
        ]

        structure_map = {
            "FluidLoop": self.fluid_loop_data_structure,
            "ServiceWaterHeatingDistributionSystem": self.swh_distribution_data_structure,
            "ServiceWaterPiping": self.swh_piping_data_structure,
        }

        # Iterate over the no_children_attributes list and populate if the value is not None
        for attr in no_children_attributes:
            value = getattr(self, attr, None)
            if value is not None:
                data_structure = structure_map.get(self.circulation_loop_type)
                data_structure[attr] = value

    def insert_to_rpd(self, rmd):
        self.determine_circ_loop_type()
        if self.circulation_loop_type == "FluidLoop":
            rmd.fluid_loops.append(self.fluid_loop_data_structure)
        elif self.circulation_loop_type == "SecondaryFluidLoop":
            primary_loop = self.keyword_value_pairs.get("PRIMARY-LOOP")
            for fluid_loop in rmd.fluid_loops:
                if fluid_loop["id"] == primary_loop:
                    fluid_loop["child_loops"].append(self.fluid_loop_data_structure)
        elif self.circulation_loop_type == "ServiceWaterHeatingDistributionSystem":
            rmd.service_water_heating_distribution_systems.append(
                self.swh_distribution_data_structure
            )
        elif self.circulation_loop_type == "ServiceWaterPiping":
            primary_loop = self.keyword_value_pairs.get("PRIMARY-LOOP")

    def determine_circ_loop_type(self):
        if (
            self.keyword_value_pairs["TYPE"] == "DHW"
            and self.keyword_value_pairs["SUBTYPE"] == "SECONDARY"
        ):
            self.circulation_loop_type = "ServiceWaterPiping"
        elif self.keyword_value_pairs["TYPE"] == "DHW":
            self.circulation_loop_type = "ServiceWaterHeatingDistributionSystem"
        elif self.keyword_value_pairs.get("PRIMARY-LOOP") is None:
            self.circulation_loop_type = "FluidLoop"
        else:
            self.circulation_loop_type = "SecondaryFluidLoop"
