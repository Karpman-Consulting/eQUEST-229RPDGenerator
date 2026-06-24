from rpd_generator.bdl_structure.base_node import BaseNode
from rpd_generator.bdl_structure.bdl_commands.schedule import Schedule
from rpd_generator.schema.schema_enums import SchemaEnums
from rpd_generator.bdl_structure.bdl_enumerations.bdl_enums import BDLEnums
from rpd_generator.artifacts.building_segment import BuildingSegment

FluidLoopOptions = SchemaEnums.schema_enums["FluidLoopOptions"]
FluidLoopOperationOptions = SchemaEnums.schema_enums["FluidLoopOperationOptions"]
FluidLoopFlowControlOptions = SchemaEnums.schema_enums["FluidLoopFlowControlOptions"]
TemperatureResetOptions = SchemaEnums.schema_enums["TemperatureResetOptions"]
ComponentLocationOptions = SchemaEnums.schema_enums["ComponentLocationOptions"]
ServiceWaterHeatingUseUnitOptions = SchemaEnums.schema_enums[
    "ServiceWaterHeatingUseUnitOptions"
]
BDL_Commands = BDLEnums.bdl_enums["Commands"]
BDL_CirculationLoopKeywords = BDLEnums.bdl_enums["CirculationLoopKeywords"]
BDL_CirculationLoopTypes = BDLEnums.bdl_enums["CirculationLoopTypes"]
BDL_CirculationLoopSubtypes = BDLEnums.bdl_enums["CirculationLoopSubtypes"]
BDL_CirculationLoopSizingOptions = BDLEnums.bdl_enums["CirculationLoopSizingOptions"]
BDL_CirculationLoopSetpointControlOptions = BDLEnums.bdl_enums[
    "CirculationLoopSetpointControlOptions"
]
BDL_CirculationLoopOperationOptions = BDLEnums.bdl_enums[
    "CirculationLoopOperationOptions"
]
BDL_CirculationLoopTemperatureResetOptions = BDLEnums.bdl_enums[
    "CirculationLoopTemperatureResetOptions"
]
BDL_CirculationLoopLocationOptions = BDLEnums.bdl_enums[
    "CirculationLoopLocationOptions"
]
BDL_SecondaryLoopValveTypes = BDLEnums.bdl_enums["CirculationLoopSecondaryValveTypes"]
BDL_SystemCoolingValveTypes = BDLEnums.bdl_enums["SystemCoolingValveTypes"]
BDL_SystemCondenserValveTypes = BDLEnums.bdl_enums["SystemCondenserValveTypes"]
BDL_SystemHeatingValveTypes = BDLEnums.bdl_enums["SystemHeatingValveTypes"]
BDL_FlowControlOptions = BDLEnums.bdl_enums["FlowControlOptions"]
BDL_ZoneCondenserValveOptions = BDLEnums.bdl_enums["ZoneCWValveOptions"]
BDL_ScheduleTypes = BDLEnums.bdl_enums["ScheduleTypes"]
BDL_ChillerKeywords = BDLEnums.bdl_enums["ChillerKeywords"]
BDL_BoilerKeywords = BDLEnums.bdl_enums["BoilerKeywords"]
BDL_HeatRejectionKeywords = BDLEnums.bdl_enums["HeatRejectionKeywords"]
BDL_SystemKeywords = BDLEnums.bdl_enums["SystemKeywords"]
BDL_GroundLoopHXKeywords = BDLEnums.bdl_enums["GroundLoopHXKeywords"]
BDL_ZoneKeywords = BDLEnums.bdl_enums["ZoneKeywords"]
BDL_EquipCtrlKeywords = BDLEnums.bdl_enums["EquipCtrlKeywords"]


class CirculationLoop(BaseNode):
    """CirculationLoop object in the tree."""

    bdl_command = BDL_Commands.CIRCULATION_LOOP

    sizing_option_map = {
        BDL_CirculationLoopSizingOptions.COINCIDENT: True,
        BDL_CirculationLoopSizingOptions.NON_COINCIDENT: False,
        BDL_CirculationLoopSizingOptions.PRIMARY: False,
        BDL_CirculationLoopSizingOptions.SECONDARY: True,
    }
    loop_operation_map = {
        BDL_CirculationLoopOperationOptions.STANDBY: None,  # This is a special case
        BDL_CirculationLoopOperationOptions.DEMAND: FluidLoopOperationOptions.INTERMITTENT,
        BDL_CirculationLoopOperationOptions.SNAP: FluidLoopOperationOptions.INTERMITTENT,
        BDL_CirculationLoopOperationOptions.SCHEDULED: None,  # This is a special case
        BDL_CirculationLoopOperationOptions.SUBHOUR_DEMAND: FluidLoopOperationOptions.INTERMITTENT,
    }
    temp_reset_map = {
        BDL_CirculationLoopTemperatureResetOptions.FIXED: TemperatureResetOptions.NO_RESET,
        BDL_CirculationLoopTemperatureResetOptions.OA_RESET: TemperatureResetOptions.OUTSIDE_AIR_RESET,
        BDL_CirculationLoopTemperatureResetOptions.SCHEDULED: TemperatureResetOptions.OTHER,
        BDL_CirculationLoopTemperatureResetOptions.LOAD_RESET: TemperatureResetOptions.LOAD_RESET,
        BDL_CirculationLoopTemperatureResetOptions.WETBULB_RESET: TemperatureResetOptions.OTHER,
    }
    piping_location_map = {
        BDL_CirculationLoopLocationOptions.OUTDOORS: ComponentLocationOptions.OUTSIDE,
        BDL_CirculationLoopLocationOptions.ZONE: None,  # TODO ZONE must be mapped to CONDITIONED, UNCONDITIONED, SEMICONDITIONED, etc
        BDL_CirculationLoopLocationOptions.TUNNEL: ComponentLocationOptions.CRAWL_SPACE,
        BDL_CirculationLoopLocationOptions.UNDERGROUND: ComponentLocationOptions.UNDERGROUND,
    }

    def __init__(self, u_name, rmd):
        super().__init__(u_name, rmd)
        self.rmd.circulation_loop_names.append(u_name)
        self.rmd.bdl_obj_instances[u_name] = self

        # keep track of the type of circulation loop (different from self.type which is the schema data element: FluidLoop.type)
        self.circulation_loop_type = None  # "ServiceWaterHeatingDistributionSystem", "FluidLoop", or "SecondaryFluidLoop"
        self.associated_data_group = (
            None  # Object instance corresponding to the circulation loop type
        )
        self.cooling_fluid_loop_design_and_control = None  # store reference to the Cooling DesignAndControl object for easy access
        self.condenser_fluid_loop_design_and_control = None  # store reference to the Condenser DesignAndControl object for easy access
        self.heating_fluid_loop_design_and_control = None  # store reference to the Heating DesignAndControl object for easy access
        self.service_water_heating_design_and_control = None  # store reference to the Service Water Heating DesignAndControl object for easy access

    def __repr__(self):
        return f"CirculationLoop(u_name='{self.u_name}')"

    def populate_data_elements(self):
        """Populate data elements from the keyword_value pairs returned from model_input_reader"""

        self.circulation_loop_type = self.determine_circ_loop_type()

        # Assign pump data elements populated from the circulation loop keyword value pairs
        pump_name = self.get_inp(BDL_CirculationLoopKeywords.LOOP_PUMP)
        if pump_name is not None:
            self.populate_pump_data_elements(pump_name)

        if self.circulation_loop_type in ["FluidLoop", "SecondaryFluidLoop"]:
            self.associated_data_group = FluidLoop(self)
            self.associated_data_group.populate_data_elements()

            # Populate the data elements for FluidLoopDesignAndControl
            if self.associated_data_group.type == FluidLoopOptions.COOLING:
                self.cooling_fluid_loop_design_and_control = FluidLoopDesignAndControl(
                    self
                )
                self.cooling_fluid_loop_design_and_control.populate_data_elements(
                    "cooling"
                )
                self.cooling_fluid_loop_design_and_control.populate_data_group()
                self.cooling_fluid_loop_design_and_control.insert_to_rpd("cooling")

            elif self.associated_data_group.type == FluidLoopOptions.CONDENSER:
                self.condenser_fluid_loop_design_and_control = (
                    FluidLoopDesignAndControl(self)
                )
                self.condenser_fluid_loop_design_and_control.populate_data_elements(
                    "condensing"
                )
                self.condenser_fluid_loop_design_and_control.populate_data_group()
                self.condenser_fluid_loop_design_and_control.insert_to_rpd("condensing")

            elif self.associated_data_group.type == FluidLoopOptions.HEATING:
                self.heating_fluid_loop_design_and_control = FluidLoopDesignAndControl(
                    self
                )
                self.heating_fluid_loop_design_and_control.populate_data_elements(
                    "heating"
                )
                self.heating_fluid_loop_design_and_control.populate_data_group()
                self.heating_fluid_loop_design_and_control.insert_to_rpd("heating")

            elif (
                self.associated_data_group.type == FluidLoopOptions.HEATING_AND_COOLING
            ):
                self.heating_fluid_loop_design_and_control = FluidLoopDesignAndControl(
                    self
                )
                self.heating_fluid_loop_design_and_control.populate_data_elements(
                    "heating"
                )
                self.heating_fluid_loop_design_and_control.populate_data_group()
                self.heating_fluid_loop_design_and_control.insert_to_rpd("heating")

                self.cooling_fluid_loop_design_and_control = FluidLoopDesignAndControl(
                    self
                )
                self.cooling_fluid_loop_design_and_control.populate_data_elements(
                    "cooling"
                )
                self.cooling_fluid_loop_design_and_control.populate_data_group()
                self.cooling_fluid_loop_design_and_control.insert_to_rpd("cooling")

        elif self.circulation_loop_type == "ServiceWaterHeatingDistributionSystem":
            self.associated_data_group = ServiceWaterHeatingDistributionSystem(self)
            self.associated_data_group.populate_data_elements()

            self.populate_service_water_heating_uses()

        elif self.circulation_loop_type == "ServiceWaterPiping":
            self.associated_data_group = ServiceWaterPiping(self)
            self.associated_data_group.populate_data_elements()

    def populate_data_group(self):
        self.associated_data_group.populate_data_group()

    def insert_to_rpd(self):
        self.associated_data_group.insert_to_rpd()

    def determine_circ_loop_type(self):

        if (
            self.get_inp(BDL_CirculationLoopKeywords.TYPE)
            == BDL_CirculationLoopTypes.DHW
            and self.get_inp(BDL_CirculationLoopKeywords.SUBTYPE)
            == BDL_CirculationLoopSubtypes.SECONDARY
        ):
            return "ServiceWaterPiping"

        elif (
            self.get_inp(BDL_CirculationLoopKeywords.TYPE)
            == BDL_CirculationLoopTypes.DHW
        ):
            return "ServiceWaterHeatingDistributionSystem"

        elif self.get_inp(BDL_CirculationLoopKeywords.PRIMARY_LOOP) is None:
            return "FluidLoop"

        else:
            return "SecondaryFluidLoop"

    def populate_service_water_heating_uses(self):
        process_flows = self.get_inp(BDL_CirculationLoopKeywords.PROCESS_FLOW)
        process_schedules = self.get_inp(BDL_CirculationLoopKeywords.PROCESS_SCH)
        process_outlet_temps = self.get_inp(BDL_CirculationLoopKeywords.PROCESS_T)

        if not isinstance(process_flows, list):
            self.keyword_value_pairs[BDL_CirculationLoopKeywords.PROCESS_FLOW] = [
                process_flows
            ]
            process_flows = [process_flows]
        if not isinstance(process_schedules, list):
            self.keyword_value_pairs[BDL_CirculationLoopKeywords.PROCESS_SCH] = [
                process_schedules
            ]
            process_schedules = [process_schedules]
        if not isinstance(process_outlet_temps, list):
            self.keyword_value_pairs[BDL_CirculationLoopKeywords.PROCESS_T] = [
                process_outlet_temps
            ]
            process_outlet_temps = [process_outlet_temps]

        for i, data_trio in enumerate(
            zip(process_flows, process_schedules, process_outlet_temps), 1
        ):
            swh_use = ServiceWaterHeatingUse(i, self)
            swh_use.populate_data_elements()

    def populate_pump_data_elements(self, pump_name):
        pump = self.get_obj(pump_name)
        if not pump:
            return

        if self.circulation_loop_type == "ServiceWaterHeatingDistributionSystem":
            loop_or_piping_id = self.u_name + " ServiceWaterPiping"
        else:
            loop_or_piping_id = self.u_name

        pump.loop_or_piping = [loop_or_piping_id] * pump.qty

        for i in range(pump.qty):
            if pump.is_flow_calculated[i]:
                # Override is_flow_calculated if the circulation loop is not sized based on design loads
                pump.is_flow_calculated[i] = (
                    self.get_inp(BDL_CirculationLoopKeywords.SIZING_OPTION)
                    != BDL_CirculationLoopSizingOptions.PRIMARY
                )

    def determine_loop_flow_control(self):
        """Determine the flow control type for the circulation loop"""
        loop_type = self.get_inp(BDL_CirculationLoopKeywords.TYPE)

        for circulation_loop_name in self.rmd.circulation_loop_names:
            circulation_loop = self.get_obj(circulation_loop_name)
            primary_loop = circulation_loop.get_inp(
                BDL_CirculationLoopKeywords.PRIMARY_LOOP
            )
            valve_type = circulation_loop.get_inp(
                BDL_CirculationLoopKeywords.VALVE_TYPE_2ND
            )

            if (
                primary_loop == self.u_name
                and valve_type == BDL_SecondaryLoopValveTypes.TWO_WAY
            ):
                return FluidLoopFlowControlOptions.VARIABLE_FLOW

        for system_name in self.rmd.system_names:
            system = self.get_obj(system_name)
            if loop_type == BDL_CirculationLoopTypes.CHW:
                cooling_loop = system.get_inp(BDL_SystemKeywords.CHW_LOOP)
                valve_type = system.get_inp(BDL_SystemKeywords.CHW_VALVE_TYPE)
                if (
                    cooling_loop == self.u_name
                    and valve_type == BDL_SystemCoolingValveTypes.TWO_WAY
                ):
                    return FluidLoopFlowControlOptions.VARIABLE_FLOW
            elif loop_type == BDL_CirculationLoopTypes.HW:
                heating_loops = [
                    system.get_inp(BDL_SystemKeywords.HW_LOOP),
                    system.get_inp(BDL_SystemKeywords.PHW_LOOP),
                ]
                valve_types = [
                    system.get_inp(BDL_SystemKeywords.HW_VALVE_TYPE),
                    system.get_inp(BDL_SystemKeywords.PHW_VALVE_TYPE),
                ]
                if (
                    self.u_name in heating_loops
                    and BDL_SystemHeatingValveTypes.TWO_WAY in valve_types
                ):
                    return FluidLoopFlowControlOptions.VARIABLE_FLOW
            elif loop_type == BDL_CirculationLoopTypes.CW:
                pass
            elif loop_type == BDL_CirculationLoopTypes.PIPE2:
                cooling_loop = system.get_inp(BDL_SystemKeywords.CHW_LOOP)
                heating_loop = system.get_inp(BDL_SystemKeywords.HW_LOOP)
                cooling_valve_type = system.get_inp(BDL_SystemKeywords.CHW_VALVE_TYPE)
                heating_valve_type = system.get_inp(BDL_SystemKeywords.HW_VALVE_TYPE)
                if (
                    cooling_loop == self.u_name
                    and cooling_valve_type == BDL_SystemCoolingValveTypes.TWO_WAY
                ):
                    return FluidLoopFlowControlOptions.VARIABLE_FLOW
                if (
                    heating_loop == self.u_name
                    and heating_valve_type == BDL_SystemHeatingValveTypes.TWO_WAY
                ):
                    return FluidLoopFlowControlOptions.VARIABLE_FLOW
            elif loop_type == BDL_CirculationLoopTypes.WLHP:
                # This only sets the default value for zones, which are captured below
                pass

        for zone_name in self.rmd.zone_names:
            zone = self.get_obj(zone_name)
            if loop_type == BDL_CirculationLoopTypes.CHW:
                cooling_loop = zone.get_inp(BDL_ZoneKeywords.CHW_LOOP)
                valve_type = zone.get_inp(BDL_ZoneKeywords.CHW_VALVE_TYPE)
                if (
                    cooling_loop == self.u_name
                    and valve_type == BDL_FlowControlOptions.VARIABLE_FLOW
                ):
                    return FluidLoopFlowControlOptions.VARIABLE_FLOW
            elif loop_type == BDL_CirculationLoopTypes.HW:
                heating_loop = zone.get_inp(BDL_ZoneKeywords.HW_LOOP)
                valve_type = zone.get_inp(BDL_ZoneKeywords.HW_VALVE_TYPE)
                if (
                    heating_loop == self.u_name
                    and valve_type == BDL_FlowControlOptions.VARIABLE_FLOW
                ):
                    return FluidLoopFlowControlOptions.VARIABLE_FLOW
            elif loop_type in [
                BDL_CirculationLoopTypes.CW,
                BDL_CirculationLoopTypes.WLHP,
            ]:
                condensing_loop = zone.get_inp(BDL_ZoneKeywords.CW_LOOP)
                has_valve = zone.get_inp(BDL_ZoneKeywords.CW_VALVE)
                if (
                    condensing_loop == self.u_name
                    and has_valve == BDL_ZoneCondenserValveOptions.YES
                ):
                    return FluidLoopFlowControlOptions.VARIABLE_FLOW
            elif loop_type == BDL_CirculationLoopTypes.PIPE2:
                heating_loop = zone.get_inp(BDL_ZoneKeywords.HW_LOOP)
                cooling_loop = zone.get_inp(BDL_ZoneKeywords.CHW_LOOP)
                heating_valve_type = zone.get_inp(BDL_ZoneKeywords.HW_VALVE_TYPE)
                cooling_valve_type = zone.get_inp(BDL_ZoneKeywords.CHW_VALVE_TYPE)
                if (
                    heating_loop == self.u_name
                    and heating_valve_type == BDL_FlowControlOptions.VARIABLE_FLOW
                ):
                    return FluidLoopFlowControlOptions.VARIABLE_FLOW
                if (
                    cooling_loop == self.u_name
                    and cooling_valve_type == BDL_FlowControlOptions.VARIABLE_FLOW
                ):
                    return FluidLoopFlowControlOptions.VARIABLE_FLOW

        for chiller_name in self.rmd.chiller_names:
            chiller = self.get_obj(chiller_name)
            if loop_type == BDL_CirculationLoopTypes.CHW:
                cooling_loop = chiller.get_inp(BDL_ChillerKeywords.CHW_LOOP)
                valve_type = chiller.get_inp(BDL_ChillerKeywords.CHW_FLOW_CTRL)
                if (
                    cooling_loop == self.u_name
                    and valve_type == BDL_FlowControlOptions.VARIABLE_FLOW
                ):
                    return FluidLoopFlowControlOptions.VARIABLE_FLOW
            elif loop_type == BDL_CirculationLoopTypes.HW:
                heating_loop = chiller.get_inp(BDL_ChillerKeywords.HTREC_LOOP)
                valve_type = chiller.get_inp(BDL_ChillerKeywords.HTREC_FLOW_CTRL)
                if (
                    heating_loop == self.u_name
                    and valve_type == BDL_FlowControlOptions.VARIABLE_FLOW
                ):
                    return FluidLoopFlowControlOptions.VARIABLE_FLOW
            elif loop_type == BDL_CirculationLoopTypes.CW:
                condensing_loop = chiller.get_inp(BDL_ChillerKeywords.CW_LOOP)
                valve_type = chiller.get_inp(BDL_ChillerKeywords.CW_FLOW_CTRL)
                if (
                    condensing_loop == self.u_name
                    and valve_type == BDL_FlowControlOptions.VARIABLE_FLOW
                ):
                    return FluidLoopFlowControlOptions.VARIABLE_FLOW
            elif loop_type == BDL_CirculationLoopTypes.PIPE2:
                cooling_loop = chiller.get_inp(BDL_ChillerKeywords.CHW_LOOP)
                heating_loop = chiller.get_inp(BDL_ChillerKeywords.HTREC_LOOP)
                cooling_valve_type = chiller.get_inp(BDL_ChillerKeywords.CHW_FLOW_CTRL)
                heating_valve_type = chiller.get_inp(
                    BDL_ChillerKeywords.HTREC_FLOW_CTRL
                )
                if (
                    cooling_loop == self.u_name
                    and cooling_valve_type == BDL_FlowControlOptions.VARIABLE_FLOW
                ):
                    return FluidLoopFlowControlOptions.VARIABLE_FLOW
                if (
                    heating_loop == self.u_name
                    and heating_valve_type == BDL_FlowControlOptions.VARIABLE_FLOW
                ):
                    return FluidLoopFlowControlOptions.VARIABLE_FLOW
            elif loop_type == BDL_CirculationLoopTypes.WLHP:
                pass  # Unused for chillers

        for boiler_name in self.rmd.boiler_names:
            boiler = self.get_obj(boiler_name)

            if loop_type in [
                BDL_CirculationLoopTypes.CHW,
                BDL_CirculationLoopTypes.CW,
            ]:
                pass  # Unused for boilers

            elif loop_type in [
                BDL_CirculationLoopTypes.HW,
                BDL_CirculationLoopTypes.PIPE2,
                BDL_CirculationLoopTypes.WLHP,
            ]:
                heating_loop = boiler.get_inp(BDL_BoilerKeywords.HW_LOOP)
                valve_type = boiler.get_inp(BDL_BoilerKeywords.HW_FLOW_CTRL)
                if (
                    heating_loop == self.u_name
                    and valve_type == BDL_FlowControlOptions.VARIABLE_FLOW
                ):
                    return FluidLoopFlowControlOptions.VARIABLE_FLOW

        for heat_rejection_name in self.rmd.heat_rejection_names:
            heat_rejection = self.get_obj(heat_rejection_name)

            if loop_type in [
                BDL_CirculationLoopTypes.CHW,
                BDL_CirculationLoopTypes.HW,
                BDL_CirculationLoopTypes.PIPE2,
            ]:
                pass  # Unused for heat rejections

            elif loop_type in [
                BDL_CirculationLoopTypes.CW,
                BDL_CirculationLoopTypes.WLHP,
            ]:
                condensing_loop = heat_rejection.get_inp(
                    BDL_HeatRejectionKeywords.CW_LOOP
                )
                valve_type = heat_rejection.get_inp(
                    BDL_HeatRejectionKeywords.CW_FLOW_CTRL
                )
                if (
                    condensing_loop == self.u_name
                    and valve_type == BDL_FlowControlOptions.VARIABLE_FLOW
                ):
                    return FluidLoopFlowControlOptions.VARIABLE_FLOW

        for ground_loop_hx_name in self.rmd.ground_loop_hx_names:
            ground_loop_hx = self.get_obj(ground_loop_hx_name)

            if loop_type in [
                BDL_CirculationLoopTypes.CHW,
                BDL_CirculationLoopTypes.HW,
                BDL_CirculationLoopTypes.PIPE2,
            ]:
                pass  # Unused for ground loop heat exchangers
            elif loop_type in [
                BDL_CirculationLoopTypes.CW,
                BDL_CirculationLoopTypes.WLHP,
            ]:
                condensing_loop = ground_loop_hx.get_inp(
                    BDL_GroundLoopHXKeywords.CIRCULATION_LOOP
                )
                valve_type = ground_loop_hx.get_inp(
                    BDL_GroundLoopHXKeywords.HX_FLOW_CTRL
                )
                if (
                    condensing_loop == self.u_name
                    and valve_type == BDL_FlowControlOptions.VARIABLE_FLOW
                ):
                    return FluidLoopFlowControlOptions.VARIABLE_FLOW

        return FluidLoopFlowControlOptions.FIXED_FLOW

    def is_loop_operation_continuous(self):
        for system_name in self.rmd.system_names:
            system = self.get_obj(system_name)
            system_fan_schedule = system.get_inp(BDL_SystemKeywords.FAN_SCHEDULE)
            if system_fan_schedule:
                if self.is_operation_schedule_continuous(system_fan_schedule):
                    return True
        return False

    def is_operation_schedule_continuous(self, schedule_u_name):
        schedule = self.get_obj(schedule_u_name)
        if schedule:
            hourly_values = schedule.hourly_values
            if hourly_values:
                # If hourly_values contains any 0 or -1, the system is not continuous
                return not any([x == 0 or x == -1 for x in hourly_values])
            else:
                return None
        else:
            raise ValueError(f"Schedule {schedule_u_name} not found in the RMD.")

    def get_hw_equipment_sequencing(self, equip_ctrl=None):
        default_staging_order = tuple(self.rmd.boiler_names)
        if not equip_ctrl:
            return default_staging_order

        sequence = []
        for i in range(1, 6):  # Loop through BOILERS_1 to BOILERS_5
            load_range_key = getattr(BDL_EquipCtrlKeywords, f"BOILERS_{i}")
            load_range_seq = equip_ctrl.get_inp(load_range_key)

            if not load_range_seq:
                continue

            if not sequence:
                sequence = load_range_seq
                continue

            for j in range(len(load_range_seq)):
                if j >= len(
                    sequence
                ):  # Extend the sequence with any new boilers in the load range
                    sequence += (load_range_seq[j],)
                elif (
                    sequence[j] != load_range_seq[j]
                ):  # If any value differs, return an empty tuple
                    return ()

        if len(sequence) < len(default_staging_order):
            sequence += [
                boiler for boiler in default_staging_order if boiler not in sequence
            ]

        return sequence


class FluidLoop:

    loop_type_map = {
        BDL_CirculationLoopTypes.CHW: FluidLoopOptions.COOLING,
        BDL_CirculationLoopTypes.HW: FluidLoopOptions.HEATING,
        BDL_CirculationLoopTypes.CW: FluidLoopOptions.CONDENSER,
        BDL_CirculationLoopTypes.PIPE2: FluidLoopOptions.HEATING_AND_COOLING,
        BDL_CirculationLoopTypes.WLHP: FluidLoopOptions.CONDENSER,
    }

    def __init__(self, loop):
        self.loop = loop

        self.data_structure = {}

        # FluidLoop data elements with children
        self.cooling_or_condensing_design_and_control = {}
        self.heating_design_and_control = {}
        self.child_loops = []

        # FluidLoop data elements with no children
        self.type = None
        self.pump_power_per_flow_rate = None

    def __repr__(self):
        return "FluidLoop()"

    def populate_data_elements(self):
        loop_type = self.loop.get_inp(BDL_CirculationLoopKeywords.TYPE)
        self.type = self.loop_type_map.get(loop_type, FluidLoopOptions.OTHER)

        pump_name = self.loop.get_inp(BDL_CirculationLoopKeywords.LOOP_PUMP)
        # Populate pump_power_per_flow_rate
        if pump_name is not None:
            loop_pump = self.loop.get_obj(pump_name)
            output_data = loop_pump.output_data
            if output_data.get("Pump - Flow (gal/min)") and output_data.get(
                "Pump - Power (kW)"
            ):
                self.pump_power_per_flow_rate = (
                    output_data.get("Pump - Power (kW)")
                    / output_data.get("Pump - Flow (gal/min)")
                    * 1000
                )

    def populate_data_group(self):
        self.data_structure = {
            "id": self.loop.u_name,
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

    def insert_to_rpd(self):
        if self.loop.circulation_loop_type == "FluidLoop":
            # Primary loops go directly into the RMD list
            self.loop.rmd.fluid_loops.append(self.data_structure)

        elif self.loop.circulation_loop_type == "SecondaryFluidLoop":
            primary_loop_obj = self.loop.get_obj(
                self.loop.get_inp(BDL_CirculationLoopKeywords.PRIMARY_LOOP)
            )
            primary_loop = primary_loop_obj.associated_data_group

            if not any(
                child_loop.get("id") == self.data_structure["id"]
                for child_loop in primary_loop.child_loops
            ):
                primary_loop.child_loops.append(self.data_structure)


class ServiceWaterPiping:
    def __init__(self, loop):
        self.loop = loop
        self.service_water_heating_design_and_control_obj = FluidLoopDesignAndControl(
            loop, self
        )

        self.data_structure = {}

        # ServiceWaterPiping data elements with children
        self.child = []
        self.service_water_heating_design_and_control = {}

        # ServiceWaterPiping data elements with no children
        self.is_recirculation_loop = None
        self.are_thermal_losses_modeled = None
        self.insulation_thickness = None
        self.loop_pipe_location = None
        self.location_zone = None
        self.length = None
        self.diameter = None

    def __repr__(self):
        return "ServiceWaterPiping()"

    def populate_data_elements(self):
        self.service_water_heating_design_and_control_obj.populate_data_elements(
            "heating"
        )

        self.are_thermal_losses_modeled = bool(
            self.loop.try_float(
                self.loop.get_inp(BDL_CirculationLoopKeywords.SUPPLY_UA)
            )
            or self.loop.try_float(
                self.loop.get_inp(BDL_CirculationLoopKeywords.SUPPLY_LOSS_DT)
            )
        )
        self.is_recirculation_loop = bool(
            self.loop.try_float(
                self.loop.get_inp(BDL_CirculationLoopKeywords.LOOP_RECIRC_FLOW)
            )
        )
        self.loop_pipe_location = self.loop.piping_location_map.get(
            self.loop.get_inp(BDL_CirculationLoopKeywords.LOOP_LOCN)
        )
        self.location_zone = self.loop.get_inp(
            BDL_CirculationLoopKeywords.LOOP_LOSS_ZONE
        )

    def populate_data_group(self):
        self.service_water_heating_design_and_control_obj.populate_data_group()
        self.service_water_heating_design_and_control = (
            self.service_water_heating_design_and_control_obj.data_structure
        )

        self.data_structure = {
            "id": self.loop.u_name + " ServiceWaterPiping",
            "child": self.child,
            "service_water_heating_design_and_control": self.service_water_heating_design_and_control,
        }

        service_water_piping_elements = [
            "is_recirculation_loop",
            "are_thermal_losses_modeled",
            "insulation_thickness",
            "loop_pipe_location",
            "location_zone",
            "length",
            "diameter",
        ]
        for attr in service_water_piping_elements:
            value = getattr(self, attr, None)
            if value is not None:
                self.data_structure[attr] = value

    def insert_to_rpd(self):
        if self.loop.circulation_loop_type == "ServiceWaterPiping":
            primary_loop = self.loop.get_obj(
                self.loop.get_inp(BDL_CirculationLoopKeywords.PRIMARY_LOOP)
            ).associated_data_group
            primary_loop.service_water_piping_obj.child.append(self.data_structure)
        elif self.loop.circulation_loop_type == "ServiceWaterHeatingDistributionSystem":
            self.loop.associated_data_group.service_water_piping = self.data_structure


class ServiceWaterHeatingDistributionSystem:
    def __init__(self, loop):
        self.loop = loop
        self.data_structure = {}

        self.service_water_piping_obj = ServiceWaterPiping(loop)

        # ServiceWaterHeatingDistributionSystem data elements with children
        self.service_water_piping = {}
        self.tanks = []

        # ServiceWaterHeatingDistributionSystem data elements with no children
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

    def __repr__(self):
        return "ServiceWaterHeatingDistributionSystem()"

    def populate_data_elements(self):
        self.service_water_piping_obj.populate_data_elements()

        self.design_supply_temperature = self.loop.try_float(
            self.loop.get_inp(BDL_CirculationLoopKeywords.DESIGN_HEAT_T)
        )
        self.design_supply_temperature_difference = self.loop.try_float(
            self.loop.get_inp(BDL_CirculationLoopKeywords.LOOP_DESIGN_DT)
        )
        self.is_ground_temperature_used_for_entering_water = not (
            self.loop.get_inp(BDL_CirculationLoopKeywords.DHW_INLET_T)
            or self.loop.get_inp(BDL_CirculationLoopKeywords.DHW_INLET_T_SCH)
        )
        self.entering_water_mains_temperature_schedule = self.loop.get_inp(
            BDL_CirculationLoopKeywords.DHW_INLET_T_SCH
        )
        if (
            self.is_ground_temperature_used_for_entering_water
            and "Ground Temperature Schedule" in self.loop.rmd.bdl_obj_instances
        ):
            self.entering_water_mains_temperature_schedule = (
                "Ground Temperature Schedule"
            )
        if (
            self.entering_water_mains_temperature_schedule is None
            and self.loop.try_float(
                self.loop.get_inp(BDL_CirculationLoopKeywords.DHW_INLET_T)
            )
        ):
            inlet_t_schedule = Schedule("DHW Inlet Temperature Schedule", self.loop.rmd)
            inlet_t_schedule.type = BDL_ScheduleTypes.TEMPERATURE
            inlet_t_schedule.hourly_values = 8760 * [
                self.loop.try_float(
                    self.loop.get_inp(BDL_CirculationLoopKeywords.DHW_INLET_T)
                )
            ]

    def populate_data_group(self):
        self.service_water_piping_obj.populate_data_group()
        self.service_water_piping_obj.insert_to_rpd()

        self.data_structure = {
            "id": self.loop.u_name,
            "tanks": self.tanks,
            "service_water_piping": self.service_water_piping,
        }

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
        for attr in service_water_heating_distribution_system_elements:
            value = getattr(self, attr, None)
            if value is not None:
                self.data_structure[attr] = value

    def insert_to_rpd(self):
        self.loop.rmd.service_water_heating_distribution_systems.append(
            self.data_structure
        )


class FluidLoopDesignAndControl:
    def __init__(self, loop, service_water_piping=None):
        self.loop = loop
        self.service_water_piping = service_water_piping

        self.data_structure = {}

        # FluidLoopDesignAndControl data elements with no children
        self.design_supply_temperature = None
        self.design_return_temperature = None
        self.is_sized_using_coincident_load = None
        self.minimum_flow_fraction = None
        self.operation = None
        self.operation_schedule = None
        self.flow_control = None
        self.temperature_reset_type = None
        self.outdoor_high_for_loop_supply_reset_temperature = None
        self.outdoor_low_for_loop_supply_reset_temperature = None
        self.loop_supply_temperature_at_outdoor_high = None
        self.loop_supply_temperature_at_outdoor_low = None
        self.loop_supply_temperature_at_low_load = None
        self.has_integrated_waterside_economizer = None

    def __repr__(self):
        return "FluidLoopDesignAndControl()"

    def populate_data_elements(self, mode):
        self.data_structure["id"] = (
            f"{self.loop.u_name} {mode.capitalize()}Design/Control"
        )

        if mode == "heating":
            self.design_supply_temperature = self.loop.try_float(
                self.loop.get_inp(BDL_CirculationLoopKeywords.DESIGN_HEAT_T)
            )
            setpt_ctrl = self.loop.get_inp(BDL_CirculationLoopKeywords.HEAT_SETPT_CTRL)
            reset_schedule_name = self.loop.get_inp(
                BDL_CirculationLoopKeywords.HEAT_RESET_SCH
            )
            reset_temp_key = BDL_CirculationLoopKeywords.MIN_RESET_T
            sched_key = BDL_CirculationLoopKeywords.HEATING_SCHEDULE

        else:  # mode in ["cooling", "condensing"]
            self.design_supply_temperature = self.loop.try_float(
                self.loop.get_inp(BDL_CirculationLoopKeywords.DESIGN_COOL_T)
            )
            setpt_ctrl = self.loop.get_inp(BDL_CirculationLoopKeywords.COOL_SETPT_CTRL)
            reset_schedule_name = self.loop.get_inp(
                BDL_CirculationLoopKeywords.COOL_RESET_SCH
            )
            reset_temp_key = BDL_CirculationLoopKeywords.MAX_RESET_T
            sched_key = BDL_CirculationLoopKeywords.COOLING_SCHEDULE

        # Return temp via delta-T
        loop_design_dt = self.loop.try_float(
            self.loop.get_inp(BDL_CirculationLoopKeywords.LOOP_DESIGN_DT)
        )
        if loop_design_dt is not None and self.design_supply_temperature is not None:
            self.design_return_temperature = (
                self.design_supply_temperature - loop_design_dt
                if mode == "heating"
                else self.design_supply_temperature + loop_design_dt
            )

        self.is_sized_using_coincident_load = self.loop.sizing_option_map.get(
            self.loop.get_inp(BDL_CirculationLoopKeywords.SIZING_OPTION)
        )
        self.minimum_flow_fraction = self.loop.try_float(
            self.loop.get_inp(BDL_CirculationLoopKeywords.LOOP_MIN_FLOW)
        )
        self.temperature_reset_type = self.loop.temp_reset_map.get(setpt_ctrl)

        if self.temperature_reset_type == TemperatureResetOptions.OUTSIDE_AIR_RESET:
            reset_schedule = self.loop.get_obj(reset_schedule_name)
            if reset_schedule:
                self.outdoor_high_for_loop_supply_reset_temperature = (
                    reset_schedule.outdoor_high_for_loop_supply_reset_temperature
                )
                self.outdoor_low_for_loop_supply_reset_temperature = (
                    reset_schedule.outdoor_low_for_loop_supply_reset_temperature
                )
                self.loop_supply_temperature_at_outdoor_high = (
                    reset_schedule.loop_supply_temperature_at_outdoor_high
                )
                self.loop_supply_temperature_at_outdoor_low = (
                    reset_schedule.loop_supply_temperature_at_outdoor_low
                )

        self.loop_supply_temperature_at_low_load = self.loop.try_float(
            self.loop.get_inp(reset_temp_key)
        )

        self.flow_control = self.loop.determine_loop_flow_control()

        operation = self.loop.get_inp(BDL_CirculationLoopKeywords.LOOP_OPERATION)
        if operation == BDL_CirculationLoopOperationOptions.SCHEDULED:
            self.operation_schedule = self.loop.get_inp(sched_key)
            if self.operation_schedule and self.loop.is_operation_schedule_continuous(
                self.operation_schedule
            ):
                self.operation = FluidLoopOperationOptions.CONTINUOUS
            else:
                self.operation = FluidLoopOperationOptions.SCHEDULED
        elif operation == BDL_CirculationLoopOperationOptions.STANDBY:
            self.operation = (
                FluidLoopOperationOptions.CONTINUOUS
                if self.loop.is_loop_operation_continuous()
                else FluidLoopOperationOptions.INTERMITTENT
            )
        else:
            self.operation = self.loop.loop_operation_map.get(operation)

    def populate_data_group(self):
        design_and_control_elements = [
            "design_supply_temperature",
            "design_return_temperature",
            "is_sized_using_coincident_load",
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

        for attr in design_and_control_elements:
            value = getattr(self, attr, None)
            if value is not None:
                self.data_structure[attr] = value

    def insert_to_rpd(self, mode):
        if mode == "heating":
            self.loop.associated_data_group.heating_design_and_control = (
                self.data_structure
            )
        elif mode in ["cooling", "condensing"]:
            self.loop.associated_data_group.cooling_or_condensing_design_and_control = (
                self.data_structure
            )
        elif mode == "service_water_heating":
            self.service_water_piping.service_water_heating_design_and_control = (
                self.data_structure
            )


class ServiceWaterHeatingUse:
    def __init__(self, n, loop):

        self.parent_building_segment = None

        self.n = n
        self.name = loop.u_name + " Load" + str(n)
        self.loop = loop
        self.loop.rmd.bdl_obj_instances[self.name] = self
        self.loop.rmd.service_water_heating_use_names.append(self.name)

        self.data_structure = {}

        self.area_type = None
        self.water_serves_type = None
        self.served_by_distribution_system = None
        self.use = None
        self.use_units = None
        self.use_multiplier_schedule = None
        self.temperature_at_fixture = None
        self.is_heat_recovered_by_drain = None
        self.is_recovered_heat_used_by_cold_side_feed = None

    def __repr__(self):
        return f"ServiceWaterHeatingUse({self.n}, {self.loop})"

    def populate_data_elements(self):
        self.served_by_distribution_system = self.loop.u_name
        self.use_multiplier_schedule = self.loop.try_access_index(
            self.loop.get_inp(BDL_CirculationLoopKeywords.PROCESS_SCH), self.n - 1
        )
        process_t = self.loop.try_access_index(
            self.loop.get_inp(BDL_CirculationLoopKeywords.PROCESS_T),
            self.n - 1,
        )

        self.temperature_at_fixture = self.loop.try_float(
            process_t
        ) or self.loop.try_float(
            self.loop.get_inp(BDL_CirculationLoopKeywords.HEAT_SETPT_T)
        )

        if (
            self.loop.get_inp(BDL_CirculationLoopKeywords.HEAT_SETPT_CTRL)
            != BDL_CirculationLoopSetpointControlOptions.FIXED
        ):
            # Currently unable to calculate SWH Use when the hot water setpoint is not fixed
            return

        if self.temperature_at_fixture != self.loop.try_float(
            self.loop.get_inp(BDL_CirculationLoopKeywords.HEAT_SETPT_T)
        ):
            if self.loop.get_inp(BDL_CirculationLoopKeywords.DHW_INLET_T) is None:
                # Currently unable to calculate SWH Use when inlet temperature is not fixed
                return

            self.use = (
                self.loop.try_float(
                    self.loop.try_access_index(
                        self.loop.get_inp(BDL_CirculationLoopKeywords.PROCESS_FLOW),
                        self.n - 1,
                    )
                )
                * (
                    self.temperature_at_fixture
                    - self.loop.try_float(
                        self.loop.get_inp(BDL_CirculationLoopKeywords.DHW_INLET_T)
                    )
                )
                / (
                    self.loop.try_float(
                        self.loop.get_inp(BDL_CirculationLoopKeywords.HEAT_SETPT_T)
                    )
                    - self.loop.try_float(
                        self.loop.get_inp(BDL_CirculationLoopKeywords.DHW_INLET_T)
                    )
                )
            )
            self.use_units = ServiceWaterHeatingUseUnitOptions.VOLUME

        else:
            self.use = self.loop.try_float(
                self.loop.try_access_index(
                    self.loop.get_inp(BDL_CirculationLoopKeywords.PROCESS_FLOW),
                    self.n - 1,
                )
            )
            self.use_units = ServiceWaterHeatingUseUnitOptions.VOLUME

    def populate_data_group(self):
        # If the length of building segments and service water heating uses are the same, set 1:1 arbitrarily
        rmd = self.loop.rmd
        building_area_types = list(self.loop.rmd.building_area_types)
        swh_use_names = list(self.loop.rmd.service_water_heating_use_names)

        if len(building_area_types) == len(swh_use_names) and swh_use_names:
            # Build a shared iterator once so each instance gets the "next" segment
            if not hasattr(rmd, "_swh_ba_iter"):
                seg_objs = [
                    self.loop.get_obj(
                        BuildingSegment.lighting_building_area_map.get(
                            bat, "Default Building Segment"
                        )
                    )
                    for bat in building_area_types
                ]
                rmd._swh_ba_iter = {"segments": seg_objs, "i": 0}

            it = rmd._swh_ba_iter
            idx = it["i"] % len(it["segments"])
            self.parent_building_segment = it["segments"][idx]
            it["i"] += 1

        # Otherwise, put all SWH uses on the first building segment by default, until TODO - they can be differentiated
        else:
            building_area_type = building_area_types[0] if building_area_types else None
            self.parent_building_segment = self.loop.get_obj(
                BuildingSegment.lighting_building_area_map.get(
                    building_area_type, "Default Building Segment"
                )
            )

        self.data_structure["id"] = self.name

        service_water_heating_use_elements = [
            "area_type",
            "water_serves_type",
            "served_by_distribution_system",
            "use",
            "use_units",
            "use_multiplier_schedule",
            "temperature_at_fixture",
            "is_heat_recovered_by_drain",
            "is_recovered_heat_used_by_cold_side_feed",
        ]
        for attr in service_water_heating_use_elements:
            value = getattr(self, attr, None)
            if value is not None:
                self.data_structure[attr] = value

    def insert_to_rpd(self):
        self.parent_building_segment.service_water_heating_uses.append(self.name)
        target = self.loop.rmd.service_water_heating_uses
        this_id = self.data_structure.get("id")
        if not any(u.get("id") == this_id for u in target):
            target.append(self.data_structure)
