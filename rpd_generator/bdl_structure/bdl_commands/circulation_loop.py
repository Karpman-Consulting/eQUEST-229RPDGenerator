from rpd_generator.bdl_structure.base_node import BaseNode


# noinspection PyUnresolvedReferences
class CirculationLoop(BaseNode):
    """CirculationLoop object in the tree."""

    bdl_command = "CIRCULATION-LOOP"

    loop_type_map = {
        "CHW": "COOLING",
        "HW": "HEATING",
        "CW": "CONDENSER",
        "PIPE2": "HEATING_AND_COOLING",
        "WLHP": "OTHER",
    }

    sizing_option_map = {
        "COINCIDENT": True,
        "NON-COINCIDENT": False,
        "PRIMARY": False,
        "SECONDARY": True,
    }

    loop_operation_map = {
        "STANDBY": "INTERMITTENT",
        "DEMAND-ONLY": "INTERMITTENT",
        "SNAP": "INTERMITTENT",
        "SCHEDULED": "SCHEDULED",
        "SUBHOUR-DEMAND": "INTERMITTENT",
    }

    temp_reset_map = {
        "FIXED": "NO_RESET",
        "OA-RESET": "OUTSIDE_AIR_RESET",
        "SCHEDULED": "OTHER",
        "LOAD-RESET": "LOAD_RESET",
        "WETBULB-RESET": "OTHER",
    }

    def __init__(self, u_name, rmd):
        super().__init__(u_name, rmd)

        # keep track of the type of circulation loop (different from self.type which is the FluidLoop type)
        self.circulation_loop_type = None

        # Initialize the data structure for the different types of circulation loops
        self.data_structure = {}

        # FluidLoop data elements with children
        self.cooling_or_condensing_design_and_control = {}
        self.heating_design_and_control = {}
        self.child_loops = []
        # FluidLoop data elements with no children
        self.type = None
        self.pump_power_per_flow_rate = None

        # ServiceWaterHeatingDistributionSystem data elements with children
        self.service_water_piping = {}
        self.tanks = {}

        # FluidLoopDesignAndControl data elements with no children [cooling, heating]
        self.design_supply_temperature = [None, None]
        self.design_return_temperature = [None, None]
        self.is_sized_using_coincident_loads = [None, None]
        self.minimum_flow_fraction = [None, None]
        self.operation = [None, None]
        self.operation_schedule = [None, None]
        self.flow_control = [None, None]
        self.temperature_reset_type = [None, None]
        self.outdoor_high_for_loop_supply_reset_temperature = [None, None]
        self.outdoor_low_for_loop_supply_reset_temperature = [None, None]
        self.loop_supply_temperature_at_outdoor_high = [None, None]
        self.loop_supply_temperature_at_outdoor_low = [None, None]
        self.loop_supply_temperature_at_low_load = [None, None]
        self.has_integrated_waterside_economizer = [None, None]

        # ServiceWaterHeatingDistributionSystem data elements with no children
        self.swh_design_supply_temperature = None
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

        # ServiceWaterPiping data elements with no children
        self.is_recirculation_loop = None
        self.insulation_thickness = None
        self.loop_pipe_location = None
        self.location_zone = None
        self.length = None
        self.diameter = None
        # self.child = None   this is commented out because in eQUEST every secondary loop is a child of a primary loop

    def __repr__(self):
        return f"CirculationLoop(u_name='{self.u_name}')"

    # noinspection PyUnresolvedReferences
    def populate_data_elements(self):
        """Populate data elements from the keyword_value pairs returned from model_input_reader"""

        # Assign pump data elements populated from the circulation loop keyword value pairs
        pump_name = self.keyword_value_pairs.get("LOOP-PUMP")
        if pump_name is not None:
            pump = self.rmd.bdl_obj_instances.get(pump_name)
            if pump is not None:
                pump.loop_or_piping = [self.u_name] * pump.qty

        self.circulation_loop_type = self.determine_circ_loop_type()
        if self.circulation_loop_type in ["FluidLoop", "SecondaryFluidLoop"]:
            loop_type = self.keyword_value_pairs.get("TYPE")
            self.type = self.loop_type_map.get(loop_type, "OTHER")

            # Populate the data elements for FluidLoopDesignAndControl
            if self.circulation_loop_type in ["FluidLoop", "SecondaryFluidLoop"]:
                if self.type == "COOLING":
                    self.populate_cool_fluid_loop_design_and_control()
                elif self.type == "CONDENSER":
                    self.populate_cond_fluid_loop_design_and_control()
                elif self.type == "HEATING":
                    self.populate_heat_fluid_loop_design_and_control()
                elif self.type == "HEATING_AND_COOLING":
                    self.populate_heat_cool_fluid_loop_design_and_control()

        if self.circulation_loop_type == "ServiceWaterHeatingDistributionSystem":
            self.swh_design_supply_temperature = self.try_float(
                self.keyword_value_pairs.get("DESIGN-HEAT-T")
            )
            inlet_t = self.keyword_value_pairs.get("DHW-INLET-T")
            inlet_t_sch = self.keyword_value_pairs.get("DHW-INLET-T-SCH")
            if inlet_t is not None or inlet_t_sch is not None:
                self.is_ground_temperature_used_for_entering_water = False
            else:
                self.is_ground_temperature_used_for_entering_water = True

        if self.circulation_loop_type == "ServiceWaterPiping":
            # None of the data elements for ServiceWaterPiping can be populated from model inputs or outputs
            pass

        # Populate pump_power_per_flow_rate
        if pump_name is not None:
            loop_pump = self.rmd.bdl_obj_instances.get(pump_name)
            output_data = loop_pump.output_data
            self.pump_power_per_flow_rate = (
                output_data.get("Pump - Power (kW)")
                / output_data.get("Pump - Flow (gal/min)")
                * 1000
            )

    def populate_data_group(self):
        """Populate schema structure for circulation loop object."""
        self.circulation_loop_type = self.determine_circ_loop_type()

        design_and_control_elements = [
            "design_supply_temperature",
            "design_return_temperature",
            "is_sized_using_coincident_loads",
            "minimum_flow_fraction",
            "operation",
            "operation_schedule",
            "flow_control",
            "temperature_reset_type",
            "outdoor_high_for_loop_supply_reset_temperature",
            "outdoor_low_for_loop_supply_reset_temperature",
            "loop_supply_temperature_at_outdoor_high",
            "loop_supply_temperature_at_outdoor_low",
            "loop_supply_temperature_at_low_load",
            "has_integrated_waterside_economizer",
        ]

        service_water_heating_distribution_system_elements = [
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
        ]

        service_water_piping_elements = [
            "is_recirculation_loop",
            "insulation_thickness",
            "loop_pipe_location",
            "location_zone",
            "length",
            "diameter",
        ]

        if self.circulation_loop_type == "ServiceWaterPiping":
            self.data_structure = {
                "id": self.u_name,
            }

            for attr in service_water_piping_elements:
                value = getattr(self, attr, None)
                if value is not None:
                    self.data_structure[attr] = value

        elif self.circulation_loop_type == "ServiceWaterHeatingDistributionSystem":
            self.data_structure = {
                "id": self.u_name,
                "tanks": self.tanks,
                "service_water_piping": self.service_water_piping,
            }

            for attr in service_water_heating_distribution_system_elements:
                # design_supply_temperature exists in both the circulation loop and the swh distribution system
                if attr == "design_supply_temperature":
                    value = self.swh_design_supply_temperature
                else:
                    value = getattr(self, attr, None)
                if value is not None:
                    self.data_structure[attr] = value

        else:
            for attr in design_and_control_elements:
                value_list = getattr(self, attr, None)
                if value_list[0] is not None:
                    self.cooling_or_condensing_design_and_control[attr] = value_list[0]
                if value_list[1] is not None:
                    self.heating_design_and_control[attr] = value_list[1]

            self.data_structure = {
                "id": self.u_name,
                "cooling_or_condensing_design_and_control": self.cooling_or_condensing_design_and_control,
                "heating_design_and_control": self.heating_design_and_control,
                "child_loops": self.child_loops,
            }

            fluid_loop_elements = [
                "reporting_name",
                "notes",
                "type",
                "pump_power_per_flow_rate",
            ]

            # Iterate over the no_children_attributes list and populate if the value is not None
            for attr in fluid_loop_elements:
                value = getattr(self, attr, None)
                if value is not None:
                    self.data_structure[attr] = value

    def insert_to_rpd(self, rmd):

        if self.circulation_loop_type == "FluidLoop":
            rmd.fluid_loops.append(self.data_structure)

        elif self.circulation_loop_type == "SecondaryFluidLoop":
            primary_loop = self.keyword_value_pairs.get("PRIMARY-LOOP")
            for fluid_loop in rmd.fluid_loops:
                if fluid_loop["id"] == primary_loop:
                    fluid_loop["child_loops"].append(self.data_structure)

        elif self.circulation_loop_type == "ServiceWaterHeatingDistributionSystem":
            rmd.service_water_heating_distribution_systems.append(self.data_structure)

        elif self.circulation_loop_type == "ServiceWaterPiping":
            primary_loop = self.keyword_value_pairs.get("PRIMARY-LOOP")
            for swh_distribution_sys in rmd.service_water_heating_distribution_systems:
                if swh_distribution_sys["id"] == primary_loop:
                    swh_distribution_sys["service_water_piping"].append(
                        self.data_structure
                    )

    def determine_circ_loop_type(self):

        if (
            self.keyword_value_pairs["TYPE"] == "DHW"
            and self.keyword_value_pairs["SUBTYPE"] == "SECONDARY"
        ):
            return "ServiceWaterPiping"

        elif self.keyword_value_pairs["TYPE"] == "DHW":
            return "ServiceWaterHeatingDistributionSystem"

        elif self.keyword_value_pairs.get("PRIMARY-LOOP") is None:
            return "FluidLoop"

        else:
            return "SecondaryFluidLoop"

    def populate_heat_fluid_loop_design_and_control(self):
        self.heating_design_and_control["id"] = self.u_name + " HeatingDesign/Control"
        self.design_supply_temperature[1] = self.try_float(
            self.keyword_value_pairs.get("DESIGN-HEAT-T")
        )
        loop_design_dt = self.try_float(self.keyword_value_pairs.get("LOOP-DESIGN-DT"))
        if loop_design_dt is None:
            pass
        else:
            self.design_return_temperature[1] = (
                self.design_supply_temperature[1] - loop_design_dt
            )
        self.is_sized_using_coincident_loads[1] = self.sizing_option_map.get(
            self.keyword_value_pairs.get("SIZING-OPTION")
        )
        self.minimum_flow_fraction[1] = self.try_float(
            self.keyword_value_pairs.get("LOOP-MIN-FLOW")
        )
        self.temperature_reset_type[1] = self.temp_reset_map.get(
            self.keyword_value_pairs.get("HEAT-SETPT-CTRL")
        )
        self.loop_supply_temperature_at_low_load[1] = self.try_float(
            self.keyword_value_pairs.get("MIN-RESET-T")
        )

    def populate_cool_fluid_loop_design_and_control(self):
        self.cooling_or_condensing_design_and_control["id"] = (
            self.u_name + " CoolingDesign/Control"
        )
        self.design_supply_temperature[0] = self.try_float(
            self.keyword_value_pairs.get("DESIGN-COOL-T")
        )
        loop_design_dt = self.try_float(self.keyword_value_pairs.get("LOOP-DESIGN-DT"))
        if loop_design_dt is None:
            pass
        else:
            self.design_return_temperature[0] = (
                self.design_supply_temperature[0] + loop_design_dt
            )
        self.is_sized_using_coincident_loads[0] = self.sizing_option_map.get(
            self.keyword_value_pairs.get("SIZING-OPTION")
        )
        self.minimum_flow_fraction[0] = self.try_float(
            self.keyword_value_pairs.get("LOOP-MIN-FLOW")
        )
        self.temperature_reset_type[0] = self.temp_reset_map.get(
            self.keyword_value_pairs.get("COOL-SETPT-CTRL")
        )
        self.loop_supply_temperature_at_low_load[0] = self.try_float(
            self.keyword_value_pairs.get("MAX-RESET-T")
        )

    def populate_cond_fluid_loop_design_and_control(self):
        self.cooling_or_condensing_design_and_control["id"] = (
            self.u_name + " CondensingDesign/Control"
        )
        self.design_supply_temperature[0] = self.try_float(
            self.keyword_value_pairs.get("DESIGN-COOL-T")
        )
        loop_design_dt = self.try_float(self.keyword_value_pairs.get("LOOP-DESIGN-DT"))
        if loop_design_dt is None:
            pass
        else:
            self.design_return_temperature[0] = (
                self.design_supply_temperature[0] + loop_design_dt
            )
        self.is_sized_using_coincident_loads[0] = self.sizing_option_map.get(
            self.keyword_value_pairs.get("SIZING-OPTION")
        )
        self.minimum_flow_fraction[0] = self.try_float(
            self.keyword_value_pairs.get("LOOP-MIN-FLOW")
        )
        self.temperature_reset_type[0] = self.temp_reset_map.get(
            self.keyword_value_pairs.get("COOL-SETPT-CTRL")
        )
        self.loop_supply_temperature_at_low_load[0] = self.try_float(
            self.keyword_value_pairs.get("MAX-RESET-T")
        )

    def populate_heat_cool_fluid_loop_design_and_control(self):
        self.cooling_or_condensing_design_and_control["id"] = (
            self.u_name + " CoolingDesign/Control"
        )
        self.design_supply_temperature[0] = self.try_float(
            self.keyword_value_pairs.get("DESIGN-COOL-T")
        )
        loop_design_dt = self.try_float(self.keyword_value_pairs.get("LOOP-DESIGN-DT"))
        if loop_design_dt is None:
            pass
        else:
            self.design_return_temperature[0] = (
                self.design_supply_temperature[0] + loop_design_dt
            )
        self.is_sized_using_coincident_loads[0] = self.sizing_option_map.get(
            self.keyword_value_pairs.get("SIZING-OPTION")
        )
        self.minimum_flow_fraction[0] = self.try_float(
            self.keyword_value_pairs.get("LOOP-MIN-FLOW")
        )
        self.temperature_reset_type[0] = self.temp_reset_map.get(
            self.keyword_value_pairs.get("COOL-SETPT-CTRL")
        )
        self.loop_supply_temperature_at_low_load[0] = self.try_float(
            self.keyword_value_pairs.get("MAX-RESET-T")
        )
        self.heating_design_and_control["id"] = self.u_name + " HeatingDesign/Control"
        self.design_supply_temperature[1] = self.try_float(
            self.keyword_value_pairs.get("DESIGN-HEAT-T")
        )
        if loop_design_dt is None:
            pass
        else:
            self.design_return_temperature[1] = (
                self.design_supply_temperature[1] - loop_design_dt
            )
        self.is_sized_using_coincident_loads[1] = self.sizing_option_map.get(
            self.keyword_value_pairs.get("SIZING-OPTION")
        )
        self.minimum_flow_fraction[1] = self.try_float(
            self.keyword_value_pairs.get("LOOP-MIN-FLOW")
        )
        self.temperature_reset_type[1] = self.temp_reset_map.get(
            self.keyword_value_pairs.get("HEAT-SETPT-CTRL")
        )
        self.loop_supply_temperature_at_low_load[1] = self.try_float(
            self.keyword_value_pairs.get("MIN-RESET-T")
        )

    def populate_service_water_heating_distribution_system(self):
        pass

    def populate_service_water_piping(self):
        pass
