from rpd_generator.bdl_structure.child_node import ChildNode
from rpd_generator.schema.schema_enums import SchemaEnums
from rpd_generator.bdl_structure.bdl_enumerations.bdl_enums import BDLEnums


HeatingSourceOptions = SchemaEnums.schema_enums["HeatingSourceOptions"]
TerminalOptions = SchemaEnums.schema_enums["TerminalOptions"]
FanSystemSupplyFanControlOptions = SchemaEnums.schema_enums[
    "FanSystemSupplyFanControlOptions"
]
FanSpecificationMethodOptions = SchemaEnums.schema_enums[
    "FanSpecificationMethodOptions"
]
BDL_Commands = BDLEnums.bdl_enums["Commands"]
BDL_ZoneKeywords = BDLEnums.bdl_enums["ZoneKeywords"]
BDL_SystemKeywords = BDLEnums.bdl_enums["SystemKeywords"]
BDL_SystemTypes = BDLEnums.bdl_enums["SystemTypes"]
BDL_ZoneHeatSourceOptions = BDLEnums.bdl_enums["ZoneHeatSourceOptions"]
BDL_TerminalTypes = BDLEnums.bdl_enums["TerminalTypes"]
BDL_BaseboardControlOptions = BDLEnums.bdl_enums["BaseboardControlOptions"]
BDL_ZoneFanRunOptions = BDLEnums.bdl_enums["ZoneFanRunOptions"]


class Zone(ChildNode):
    """Zone object in the tree."""

    bdl_command = BDL_Commands.ZONE

    heat_source_map = {
        BDL_ZoneHeatSourceOptions.NONE: None,
        BDL_ZoneHeatSourceOptions.ELECTRIC: HeatingSourceOptions.ELECTRIC,
        BDL_ZoneHeatSourceOptions.HOT_WATER: HeatingSourceOptions.HOT_WATER,
        BDL_ZoneHeatSourceOptions.FURNACE: HeatingSourceOptions.OTHER,
        BDL_ZoneHeatSourceOptions.DHW_LOOP: HeatingSourceOptions.OTHER,
        BDL_ZoneHeatSourceOptions.STEAM: HeatingSourceOptions.OTHER,
        BDL_ZoneHeatSourceOptions.HEAT_PUMP: HeatingSourceOptions.OTHER,
    }

    is_fan_first_stage_map = {
        BDL_ZoneFanRunOptions.HEATING_ONLY: False,
        BDL_ZoneFanRunOptions.HEATING_DEADBAND: True,
        BDL_ZoneFanRunOptions.CONTINUOUS: True,
        BDL_ZoneFanRunOptions.HEATING_COOLING: False,
    }

    def __init__(self, u_name, parent, rmd):
        super().__init__(u_name, parent, rmd)
        self.rmd.zone_names.append(u_name)

        # On initialization the parent building segment is not known. It will be set in the GUI.
        self.parent_building_segment = rmd.bdl_obj_instances.get(
            "Default Building Segment", None
        )

        self.zone_data_structure = {}

        # data elements with children
        self.spaces = []
        self.surfaces = []
        self.terminals = []
        self.zonal_exhaust_fan = {}
        self.infiltration = {}

        # data elements with no children
        self.floor_name = None
        self.volume = None
        self.conditioning_type = None
        self.design_thermostat_cooling_setpoint = None
        self.thermostat_cooling_setpoint_schedule = None
        self.design_thermostat_heating_setpoint = None
        self.thermostat_heating_setpoint_schedule = None
        self.minimum_humidity_setpoint_schedule = None
        self.maximum_humidity_setpoint_schedule = None
        self.served_by_service_water_heating_system = None
        self.transfer_airflow_rate = None
        self.transfer_airflow_source_zone = None
        self.exhaust_airflow_rate_multiplier_schedule = None
        self.makeup_airflow_rate = None
        self.non_mechanical_cooling_fan_power = None
        self.non_mechanical_cooling_fan_airflow = None
        self.air_distribution_effectiveness = None
        self.aggregation_factor = None

        # terminal data elements as a list of [Main Terminal, Baseboard Terminal, DOAS Terminal]
        self.terminals_id: list = [None, None, None]
        self.terminals_reporting_name: list = [None, None, None]
        self.terminals_notes: list = [None, None, None]
        self.terminals_type: list = [None, None, None]
        self.terminals_served_by_heating_ventilating_air_conditioning_system: list = [
            None,
            None,
            None,
        ]
        self.terminals_heating_source: list = [None, None, None]
        self.terminals_heating_from_loop: list = [None, None, None]
        self.terminals_cooling_source: list = [None, None, None]
        self.terminals_cooling_from_loop: list = [None, None, None]
        self.terminals_fan: list = [None, None, None]
        self.terminals_fan_configuration: list = [None, None, None]
        self.terminals_primary_airflow: list = [None, None, None]
        self.terminals_secondary_airflow: list = [None, None, None]
        self.terminals_max_heating_airflow: list = [None, None, None]
        self.terminals_supply_design_heating_setpoint_temperature: list = [
            None,
            None,
            None,
        ]
        self.terminals_supply_design_cooling_setpoint_temperature: list = [
            None,
            None,
            None,
        ]
        self.terminals_temperature_control: list = [None, None, None]
        self.terminals_minimum_airflow: list = [None, None, None]
        self.terminals_minimum_outdoor_airflow: list = [None, None, None]
        self.terminals_minimum_outdoor_airflow_multiplier_schedule: list = [
            None,
            None,
            None,
        ]
        self.terminals_heating_capacity: list = [None, None, None]
        self.terminals_cooling_capacity: list = [None, None, None]
        self.terminals_is_supply_ducted: list = [None, None, None]
        self.terminals_has_demand_control_ventilation: list = [None, None, None]
        self.terminals_is_fan_first_stage_heat: list = [None, None, None]

        # terminal fan data elements, maximum of 1 terminal fan per zone
        self.terminal_fan_id = None
        self.terminal_fan_reporting_name = None
        self.terminal_fan_notes = None
        self.terminal_fan_design_airflow = None
        self.terminal_fan_is_airflow_sized_based_on_design_day = None
        self.terminal_fan_specification_method = None
        self.terminal_fan_design_electric_power = None
        self.terminal_fan_design_pressure_rise = None
        self.terminal_fan_total_efficiency = None
        self.terminal_fan_output_validation_points = []

        # zonal exhaust fan data elements, maximum of 1 zonal exhaust fan per zone
        self.zone_exhaust_fan_id = None
        self.zone_exhaust_fan_reporting_name = None
        self.zone_exhaust_fan_notes = None
        self.zone_exhaust_fan_design_airflow = None
        self.zone_exhaust_fan_is_airflow_sized_based_on_design_day = None
        self.zone_exhaust_fan_specification_method = None
        self.zone_exhaust_fan_design_electric_power = None
        self.zone_exhaust_fan_design_pressure_rise = None
        self.zone_exhaust_fan_total_efficiency = None
        self.zone_exhaust_fan_output_validation_points = []

        # infiltration data elements
        self.infil_id = None
        self.infil_reporting_name = None
        self.infil_notes = None
        self.infil_modeling_method = None
        self.infil_algorithm_name = None
        self.infil_measured_air_leakage_rate = None
        self.infil_flow_rate = None
        self.infil_multiplier_schedule = None

    def __repr__(self):
        return f"Zone(u_name='{self.u_name}', parent='{self.parent}')"

    def populate_data_elements(self):
        """Populate data elements for zone object."""
        has_doas = bool(
            self.parent.keyword_value_pairs.get(BDL_SystemKeywords.DOA_SYSTEM)
        )
        has_baseboard = self.keyword_value_pairs.get(
            BDL_ZoneKeywords.BASEBOARD_CTRL
        ) not in [
            None,
            BDL_BaseboardControlOptions.NONE,
        ]
        is_piu = self.keyword_value_pairs.get(BDL_ZoneKeywords.TERMINAL_TYPE) in [
            BDL_TerminalTypes.SERIES_PIU,
            BDL_TerminalTypes.PARALLEL_PIU,
        ]

        self.design_thermostat_cooling_setpoint = self.try_float(
            self.keyword_value_pairs.get(BDL_ZoneKeywords.DESIGN_COOL_T)
        )
        self.thermostat_cooling_setpoint_schedule = self.keyword_value_pairs.get(
            BDL_ZoneKeywords.COOL_TEMP_SCH
        )
        self.design_thermostat_heating_setpoint = self.try_float(
            self.keyword_value_pairs.get(BDL_ZoneKeywords.DESIGN_HEAT_T)
        )
        self.thermostat_heating_setpoint_schedule = self.keyword_value_pairs.get(
            BDL_ZoneKeywords.HEAT_TEMP_SCH
        )
        self.exhaust_airflow_rate_multiplier_schedule = self.keyword_value_pairs.get(
            BDL_ZoneKeywords.EXHAUST_FAN_SCH
        )

        # if the zone is served by a SUM system don't populate the data elements
        if (
            self.parent.keyword_value_pairs.get(BDL_SystemKeywords.TYPE)
            == BDL_SystemTypes.SUM
        ):
            return

        requests = self.get_output_requests()
        output_data = self.get_output_data(requests)
        supply_airflow = output_data.get(
            "HVAC Systems - Design Parameters - Zone Design Data - General - Supply Airflow"
        )
        minimum_airflow_ratio = output_data.get(
            "HVAC Systems - Design Parameters - Zone Design Data - General - Minimum Airflow Ratio"
        )
        minimum_outdoor_airflow = output_data.get(
            "HVAC Systems - Design Parameters - Zone Design Data - General - Outside Airflow"
        )

        # Populate MainTerminal data elements
        self.terminals_id[0] = self.u_name + " MainTerminal"
        self.terminals_served_by_heating_ventilating_air_conditioning_system[0] = (
            self.parent.u_name
        )
        self.terminals_heating_source[0] = self.heat_source_map.get(
            self.parent.keyword_value_pairs.get(BDL_SystemKeywords.ZONE_HEAT_SOURCE)
        )
        self.terminals_heating_from_loop[0] = self.keyword_value_pairs.get(
            BDL_ZoneKeywords.HW_LOOP
        )
        self.terminals_primary_airflow[0] = supply_airflow
        self.terminals_heating_capacity[0] = output_data.get(
            "HVAC Systems - Design Parameters - Zone Design Data - General - Heating Capacity"
        )
        self.terminals_cooling_capacity[0] = output_data.get(
            "HVAC Systems - Design Parameters - Zone Design Data - General - Cooling Capacity"
        )
        exhaust_airflow = self.try_float(
            self.keyword_value_pairs.get(BDL_ZoneKeywords.EXHAUST_FLOW)
        )

        if supply_airflow is not None and minimum_airflow_ratio is not None:
            self.terminals_minimum_airflow[0] = supply_airflow * minimum_airflow_ratio

        if not has_doas:
            self.terminals_minimum_outdoor_airflow[0] = minimum_outdoor_airflow
            self.terminals_minimum_outdoor_airflow_multiplier_schedule[0] = (
                self.keyword_value_pairs.get(BDL_ZoneKeywords.MIN_AIR_SCH)
            )

        # Populate Baseboard Terminal data elements if applicable
        if has_baseboard:
            self.terminals_id[1] = self.u_name + " BaseboardTerminal"
            self.terminals_type[1] = TerminalOptions.BASEBOARD
            self.terminals_is_supply_ducted[1] = False
            self.terminals_has_demand_control_ventilation[1] = False
            self.terminals_cooling_capacity[1] = 0.0
            self.terminals_heating_source[1] = self.heat_source_map.get(
                self.keyword_value_pairs.get(BDL_ZoneKeywords.BASEBOARD_SOURCE)
            )
            self.terminals_heating_from_loop[1] = self.parent.keyword_value_pairs.get(
                BDL_SystemKeywords.BBRD_LOOP
            )
            self.terminals_heating_capacity[1] = self.keyword_value_pairs.get(
                BDL_ZoneKeywords.BASEBOARD_RATING
            )

        # Populate DOAS Terminal data elements if applicable
        if has_doas:
            doas_system = self.rmd.bdl_obj_instances.get(
                self.parent.keyword_value_pairs.get(BDL_SystemKeywords.DOA_SYSTEM)
            )
            self.terminals_id[2] = self.u_name + " DOASTerminal"
            self.terminals_cooling_capacity[2] = 0.0
            self.terminals_heating_capacity[2] = 0.0
            self.terminals_minimum_outdoor_airflow[2] = minimum_outdoor_airflow
            self.terminals_minimum_outdoor_airflow_multiplier_schedule[2] = (
                self.keyword_value_pairs.get(BDL_ZoneKeywords.MIN_AIR_SCH)
            )
            self.terminals_primary_airflow[2] = minimum_outdoor_airflow
            self.terminals_minimum_airflow[2] = minimum_outdoor_airflow
            if (
                doas_system.fan_sys_fan_control
                == FanSystemSupplyFanControlOptions.CONSTANT
                or self.keyword_value_pairs.get(BDL_ZoneKeywords.MIN_FLOW_RATIO) == 1
            ):
                self.terminals_type[2] = TerminalOptions.CONSTANT_AIR_VOLUME
            # TODO: Account for zone minimum air flow schedule(s)
            else:
                self.terminals_type[2] = TerminalOptions.VARIABLE_AIR_VOLUME

        # Only populate MainTerminal Fan data elements here if the zone TERMINAL-TYPE is SERIES-PIU or PARALLEL-PIU
        if is_piu:
            self.terminal_fan_id = self.u_name + " MainTerminal Fan"
            self.terminal_fan_design_airflow = self.try_float(
                output_data.get(
                    "HVAC Systems - Design Parameters - Zone Design Data - Powered Induction Units - Fan Flow"
                )
            )
            self.terminals_is_fan_first_stage_heat[0] = self.is_fan_first_stage_map.get(
                self.keyword_value_pairs.get(BDL_ZoneKeywords.ZONE_FAN_RUN)
            )
            if self.keyword_value_pairs.get(BDL_ZoneKeywords.ZONE_FAN_FLOW):
                self.terminal_fan_is_airflow_sized_based_on_design_day = False
            self.terminal_fan_specification_method = (
                FanSpecificationMethodOptions.SIMPLE
            )
            self.terminal_fan_design_electric_power = output_data.get(
                "HVAC Systems - Design Parameters - Zone Design Data - Powered Induction Units - Fan kW"
            )

        # Only populate MainTerminal Fan data elements here if the parent system type is FC with HW or no heat
        elif self.parent.is_terminal:
            self.terminal_fan_id = self.u_name + " MainTerminal Fan"
            self.terminal_fan_design_airflow = output_data.get(
                "HVAC Systems - Design Parameters - Zone Design Data - General - Supply Airflow"
            )
            self.terminal_fan_design_electric_power = output_data.get(
                "HVAC Systems - Design Parameters - Zone Design Data - General - Zone Fan Power"
            )
            self.terminal_fan_specification_method = (
                FanSpecificationMethodOptions.SIMPLE
            )

        if exhaust_airflow is not None and exhaust_airflow > 0:
            self.zone_exhaust_fan_id = self.u_name + " EF"
            self.zone_exhaust_fan_design_airflow = exhaust_airflow
            self.zone_exhaust_fan_is_airflow_sized_based_on_design_day = False
            if (
                self.keyword_value_pairs.get(BDL_ZoneKeywords.EXHAUST_STATIC)
                is not None
            ):
                self.zone_exhaust_fan_specification_method = (
                    FanSpecificationMethodOptions.DETAILED
                )
                self.zone_exhaust_fan_design_pressure_rise = self.try_float(
                    self.keyword_value_pairs.get(BDL_ZoneKeywords.EXHAUST_STATIC)
                )
                self.zone_exhaust_fan_total_efficiency = self.try_float(
                    self.keyword_value_pairs.get(BDL_ZoneKeywords.EXHAUST_EFF)
                )
                zone_fan_power = output_data.get(
                    "HVAC Systems - Design Parameters - Zone Design Data - General - Zone Fan Power"
                )
                self.zone_exhaust_fan_design_electric_power = (
                    None
                    if zone_fan_power is None
                    else (
                        zone_fan_power
                        if self.terminal_fan_design_electric_power is None
                        else zone_fan_power - self.terminal_fan_design_electric_power
                    )
                )
            else:
                self.zone_exhaust_fan_specification_method = (
                    FanSpecificationMethodOptions.SIMPLE
                )
                zone_ef_power_per_flow = self.try_float(
                    self.keyword_value_pairs.get(BDL_ZoneKeywords.EXHAUST_KW_FLOW)
                )
                self.zone_exhaust_fan_design_electric_power = (
                    zone_ef_power_per_flow * exhaust_airflow
                )
            return

    def populate_data_group(self):
        """Populate schema structure for zone object."""
        # Populate the terminals data structure
        self.terminals = self.populate_data_group_with_prefix("terminals_")

        # Populate the zonal exhaust fan data structure
        zonal_exhaust_fan_data = self.populate_data_group_with_prefix(
            "zone_exhaust_fan_"
        )
        self.zonal_exhaust_fan = (
            zonal_exhaust_fan_data[0] if zonal_exhaust_fan_data else {}
        )

        # Populate the infiltration data structure
        infiltration_data = self.populate_data_group_with_prefix("infil_")
        self.infiltration = infiltration_data[0] if infiltration_data else {}

        self.zone_data_structure = {
            "id": self.u_name,
            "spaces": self.spaces,
            "surfaces": self.surfaces,
            "terminals": self.terminals,
            "zonal_exhaust_fan": self.zonal_exhaust_fan,
            "infiltration": self.infiltration,
        }

        no_children_attributes = [
            "reporting_name",
            "notes",
            "floor_name",
            "volume",
            "conditioning_type",
            "design_thermostat_cooling_setpoint",
            "thermostat_cooling_setpoint_schedule",
            "design_thermostat_heating_setpoint",
            "thermostat_heating_setpoint_schedule",
            "minimum_humidity_setpoint_schedule",
            "maximum_humidity_setpoint_schedule",
            "served_by_service_water_heating_system",
            "transfer_airflow_rate",
            "transfer_airflow_source_zone",
            "zonal_exhaust_flow",
            "exhaust_airflow_rate_multiplier_schedule",
            "makeup_airflow_rate",
            "non_mechanical_cooling_fan_power",
            "non_mechanical_cooling_fan_airflow",
            "air_distribution_effectiveness",
            "aggregation_factor",
        ]

        # Iterate over the no_children_attributes list and populate if the value is not None
        for attr in no_children_attributes:
            value = getattr(self, attr, None)
            if value is not None:
                self.zone_data_structure[attr] = value

    def get_output_requests(self):
        """Get the output requests for the zone."""
        requests = {
            "HVAC Systems - Design Parameters - Zone Design Data - General - Supply Airflow": (
                2201045,
                self.parent.u_name,
                self.u_name,
            ),
            "HVAC Systems - Design Parameters - Zone Design Data - General - Exhaust Airflow": (
                2201046,
                self.parent.u_name,
                self.u_name,
            ),
            "HVAC Systems - Design Parameters - Zone Design Data - General - Zone Fan Power": (
                2201047,
                self.parent.u_name,
                self.u_name,
            ),
            "HVAC Systems - Design Parameters - Zone Design Data - General - Minimum Airflow Ratio": (
                2201048,
                self.parent.u_name,
                self.u_name,
            ),
            "HVAC Systems - Design Parameters - Zone Design Data - General - Outside Airflow": (
                2201049,
                self.parent.u_name,
                self.u_name,
            ),
            "HVAC Systems - Design Parameters - Zone Design Data - General - Cooling Capacity": (
                2201050,
                self.parent.u_name,
                self.u_name,
            ),
            "HVAC Systems - Design Parameters - Zone Design Data - General - Sensible Heat Ratio": (
                2201051,
                self.parent.u_name,
                self.u_name,
            ),
            "HVAC Systems - Design Parameters - Zone Design Data - General - Heating Capacity": (
                2201053,
                self.parent.u_name,
                self.u_name,
            ),
            "HVAC Systems - Design Parameters - Zone Design Data - General - Zone Multiplier": (
                2201055,
                self.parent.u_name,
                self.u_name,
            ),
        }

        if self.keyword_value_pairs.get(BDL_ZoneKeywords.TERMINAL_TYPE) in [
            BDL_TerminalTypes.SERIES_PIU,
            BDL_TerminalTypes.PARALLEL_PIU,
        ]:
            requests.update(
                {
                    "HVAC Systems - Design Parameters - Zone Design Data - Powered Induction Units - Fan Flow": (
                        2202001,
                        self.parent.u_name,
                        self.u_name,
                    ),
                    "HVAC Systems - Design Parameters - Zone Design Data - Powered Induction Units - Cold Deck Flow": (
                        2202002,
                        self.parent.u_name,
                        self.u_name,
                    ),
                    "HVAC Systems - Design Parameters - Zone Design Data - Powered Induction Units - Cold Deck Minimum Airflow Ratio": (
                        2202003,
                        self.parent.u_name,
                        self.u_name,
                    ),
                    "HVAC Systems - Design Parameters - Zone Design Data - Powered Induction Units - Fan kW": (
                        2202006,
                        self.parent.u_name,
                        self.u_name,
                    ),
                }
            )

        return requests

    def insert_to_rpd(self, rmd):
        """Insert zone object into the rpd data structure."""
        self.parent_building_segment.zones.append(self.zone_data_structure)
