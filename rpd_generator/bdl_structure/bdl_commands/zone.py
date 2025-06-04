from rpd_generator.bdl_structure.child_node import ChildNode
from rpd_generator.schema.schema_enums import SchemaEnums
from rpd_generator.bdl_structure.bdl_commands.system import FanSystem, Fan
from rpd_generator.bdl_structure.bdl_enumerations.bdl_enums import BDLEnums

HeatingSourceOptions = SchemaEnums.schema_enums["HeatingSourceOptions"]
CoolingSourceOptions = SchemaEnums.schema_enums["CoolingSourceOptions"]
TerminalOptions = SchemaEnums.schema_enums["TerminalOptions"]
TerminalFanConfigurationOptions = SchemaEnums.schema_enums[
    "TerminalFanConfigurationOptions"
]
TerminalTemperatureControlOptions = SchemaEnums.schema_enums[
    "TerminalTemperatureControlOptions"
]
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
BDL_SystemFanControlOptions = BDLEnums.bdl_enums["SystemFanControlOptions"]
BDL_SystemCoolControlOptions = BDLEnums.bdl_enums["SystemCoolControlOptions"]
BDL_SystemHeatControlOptions = BDLEnums.bdl_enums["SystemHeatControlOptions"]
BDL_ZoneHeatSourceOptions = BDLEnums.bdl_enums["ZoneHeatSourceOptions"]
BDL_TerminalTypes = BDLEnums.bdl_enums["TerminalTypes"]
BDL_BaseboardControlOptions = BDLEnums.bdl_enums["BaseboardControlOptions"]
BDL_SystemMinimumOutdoorAirControlOptions = BDLEnums.bdl_enums[
    "SystemMinimumOutdoorAirControlOptions"
]
BDL_DOASAttachedToOptions = BDLEnums.bdl_enums["DOASAttachedToOptions"]
BDL_ZoneFanRunOptions = BDLEnums.bdl_enums["ZoneFanRunOptions"]
BDL_ZoneFanControlOptions = BDLEnums.bdl_enums["ZoneFanControlOptions"]
BDL_ZoneCWValveOptions = BDLEnums.bdl_enums["ZoneCWValveOptions"]
BDL_ZoneInductionSourceOptions = BDLEnums.bdl_enums["ZoneInductionSourceOptions"]
BDL_OutputCoolingTypes = BDLEnums.bdl_enums["OutputCoolingTypes"]
BDL_OutputHeatingTypes = BDLEnums.bdl_enums["OutputHeatingTypes"]
BDL_ZoneOAMethodsOptions = BDLEnums.bdl_enums["ZoneOAMethodOptions"]
BDL_SpaceKeywords = BDLEnums.bdl_enums["SpaceKeywords"]
BDL_MinFlowControlOptions = BDLEnums.bdl_enums["MinFlowControlOptions"]


class Zone(ChildNode):
    """Zone object in the tree."""

    bdl_command = BDL_Commands.ZONE

    def __init__(self, u_name, parent, rmd):
        super().__init__(u_name, parent, rmd)
        self.rmd.zone_names.append(u_name)
        self.rmd.bdl_obj_instances[u_name] = self

        # On initialization the parent building segment is not known. It will be set in the GUI.
        self.parent_building_segment = self.get_obj("Default Building Segment")

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

        # Store object instances for easy access
        self.main_terminal = None
        self.baseboard_terminal = None
        self.doas_terminal = None
        self.exhaust_fan = None
        self.terminal_fan = None

    def __repr__(self):
        return f"Zone(u_name='{self.u_name}', parent='{self.parent}')"

    def populate_data_elements(self):
        """Populate data elements for zone object."""
        has_baseboard = self.get_inp(BDL_ZoneKeywords.BASEBOARD_CTRL) not in [
            None,
            BDL_BaseboardControlOptions.NONE,
        ]
        has_doas = bool(self.parent.get_inp(BDL_SystemKeywords.DOA_SYSTEM))

        has_dcv = False
        if self.get_inp(BDL_ZoneKeywords.OUTSIDE_AIR_FLOW) is None and self.try_float(
            self.get_inp(BDL_ZoneKeywords.OA_FLOW_PER)
        ):
            has_dcv = self.determine_if_dcv()

        space = self.get_obj(self.get_inp(BDL_ZoneKeywords.SPACE))

        # Populate zone data elements that originate from Space data
        self.volume = (
            (self.try_float(self.get_inp(BDL_SpaceKeywords.VOLUME)) or 0)
            * (self.try_float(self.get_inp(BDL_SpaceKeywords.FLOOR_MULTIPLIER)) or 1)
            * (self.try_float(self.get_inp(BDL_SpaceKeywords.MULTIPLIER)) or 1)
        )
        space.populate_zone_infiltration() if space else None

        self.floor_name = space.parent.u_name if space else None

        self.design_thermostat_cooling_setpoint = self.try_float(
            self.get_inp(BDL_ZoneKeywords.DESIGN_COOL_T)
        )
        self.thermostat_cooling_setpoint_schedule = self.get_inp(
            BDL_ZoneKeywords.COOL_TEMP_SCH
        )
        self.design_thermostat_heating_setpoint = self.try_float(
            self.get_inp(BDL_ZoneKeywords.DESIGN_HEAT_T)
        )
        self.thermostat_heating_setpoint_schedule = self.get_inp(
            BDL_ZoneKeywords.HEAT_TEMP_SCH
        )
        self.exhaust_airflow_rate_multiplier_schedule = self.get_inp(
            BDL_ZoneKeywords.EXHAUST_FAN_SCH
        )

        # if the zone is served by a SUM system don't populate the data elements below
        if self.parent.get_inp(BDL_SystemKeywords.TYPE) == BDL_SystemTypes.SUM:
            return

        requests = self.get_output_requests()
        output_data = self.get_output_data(requests)
        for key in [
            "Zone Heating Capacity",
            "Zone Cooling Capacity",
        ]:
            if key in output_data:
                output_data[key] = self.try_convert_units(
                    output_data[key], "kBtu/hr", "Btu/hr"
                )

        minimum_outdoor_airflow = output_data.get("Zone Outside Airflow")
        exhaust_airflow = self.try_float(self.get_inp(BDL_ZoneKeywords.EXHAUST_FLOW))

        # Populate Zonal Exhaust Fan data elements prior to MainTerminal data elements for accurate zone fan power calc
        if exhaust_airflow is not None and exhaust_airflow > 0:
            self.populate_zonal_exhaust(exhaust_airflow)

        # Populate MainTerminal data elements
        self.main_terminal = Terminal(self)
        self.main_terminal.populate_data_elements("main", output_data, has_dcv)

        # Populate DOAS Terminal data elements if applicable
        if has_doas:
            self.doas_terminal = Terminal(self)
            self.doas_terminal.populate_data_elements("doas", output_data, has_dcv)
            self.doas_terminal.populate_data_group()
            self.doas_terminal.insert_to_rpd()

        else:
            self.main_terminal.minimum_outdoor_airflow = minimum_outdoor_airflow
            self.main_terminal.minimum_outdoor_airflow_multiplier_schedule = (
                self.get_inp(BDL_ZoneKeywords.MIN_AIR_SCH)
            )
            self.main_terminal.has_demand_control_ventilation = has_dcv

        # Populate Baseboard Terminal data elements if applicable
        if has_baseboard:
            self.baseboard_terminal = Terminal(self)
            self.baseboard_terminal.populate_data_elements(
                "baseboard", output_data, has_dcv
            )
            self.baseboard_terminal.populate_data_group()
            self.baseboard_terminal.insert_to_rpd()

        self.main_terminal.populate_data_group()
        self.main_terminal.insert_to_rpd()

    def populate_data_group(self):
        """Populate schema structure for zone object."""

        # Populate the zonal exhaust fan data structure
        self.exhaust_fan.populate_data_group() if self.exhaust_fan else None
        if self.exhaust_fan:
            self.zonal_exhaust_fan = self.exhaust_fan.data_structure

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
        requests = {}
        if self.parent.is_terminal and self.parent.is_zonal_system:
            requests = {
                "Zone Supply Airflow": (
                    2201045,
                    self.parent.u_name,
                    self.u_name,
                ),
                "Zone Exhaust Airflow": (
                    2201046,
                    self.parent.u_name,
                    self.u_name,
                ),
                "Zone Fan Power": (
                    2201047,
                    self.parent.u_name,
                    self.u_name,
                ),
                "Zone Minimum Airflow Ratio": (
                    2201048,
                    self.parent.u_name,
                    self.u_name,
                ),
                "Zone Outside Airflow": (
                    2201049,
                    self.parent.u_name,
                    self.u_name,
                ),
                "Zone Cooling Capacity": (
                    2201050,
                    self.parent.u_name,
                    self.u_name,
                ),
                "Zone Sensible Heat Ratio": (
                    2201051,
                    self.parent.u_name,
                    self.u_name,
                ),
                "Zone Heating Capacity": (
                    2201053,
                    self.parent.u_name,
                    self.u_name,
                ),
                "Zone Multiplier": (
                    2201055,
                    self.parent.u_name,
                    self.u_name,
                ),
            }

            match self.parent.bdl_output_cool_type:
                case BDL_OutputCoolingTypes.CHILLED_WATER:
                    # Design data for Cooling - chilled water - ZONE - capacity, btu/hr
                    requests["Design Cooling capacity"] = (
                        2203505,
                        self.parent.u_name,
                        self.u_name,
                    )
                    # Design data for Cooling - chilled water - ZONE - SHR
                    requests["Design Cooling SHR"] = (
                        2203506,
                        self.parent.u_name,
                        self.u_name,
                    )
                    # Rated data for Cooling - chilled water - ZONE - capacity, btu/hr
                    requests["Rated Cooling capacity"] = (
                        2203516,
                        self.parent.u_name,
                        self.u_name,
                    )
                    # Rated data for Cooling - chilled water - ZONE - SHR
                    requests["Rated Cooling SHR"] = (
                        2203517,
                        self.parent.u_name,
                        self.u_name,
                    )
                case BDL_OutputCoolingTypes.DX_AIR_COOLED:
                    # Design data for Cooling - DX air cooled - ZONE - capacity, btu/hr
                    requests["Design Cooling capacity"] = (
                        2203557,
                        self.parent.u_name,
                        self.u_name,
                    )
                    # Design data for Cooling - DX air cooled - ZONE - SHR
                    requests["Design Cooling SHR"] = (
                        2203558,
                        self.parent.u_name,
                        self.u_name,
                    )
                    # Rated data for Cooling - DX air cooled - ZONE - capacity, btu/hr
                    requests["Rated Cooling capacity"] = (
                        2203566,
                        self.parent.u_name,
                        self.u_name,
                    )
                    # Rated data for Cooling - DX air cooled - ZONE - SHR
                    requests["Rated Cooling SHR"] = (
                        2203567,
                        self.parent.u_name,
                        self.u_name,
                    )
                case BDL_OutputCoolingTypes.DX_WATER_COOLED:
                    # Design data for Cooling - DX water cooled - ZONE - capacity, btu/hr
                    requests["Design Cooling capacity"] = (
                        2203587,
                        self.parent.u_name,
                        self.u_name,
                    )
                    # Design data for Cooling - DX water cooled - ZONE - SHR
                    requests["Design Cooling SHR"] = (
                        2203588,
                        self.parent.u_name,
                        self.u_name,
                    )
                    # Rated data for Cooling - DX water cooled - ZONE - capacity, btu/hr
                    requests["Rated Cooling capacity"] = (
                        2203596,
                        self.parent.u_name,
                        self.u_name,
                    )
                    # Rated data for Cooling - DX water cooled - ZONE - SHR
                    requests["Rated Cooling SHR"] = (
                        2203597,
                        self.parent.u_name,
                        self.u_name,
                    )
                case BDL_OutputCoolingTypes.VRF:
                    # Design data for Cooling - VRF - ZONE - capacity, btu/hr
                    requests["Design Cooling capacity"] = (
                        2203619,
                        self.parent.u_name,
                        self.u_name,
                    )
                    # Design data for Cooling - VRF - ZONE - SHR
                    requests["Design Cooling SHR"] = (
                        2203620,
                        self.parent.u_name,
                        self.u_name,
                    )
                    # Rated data for Cooling - VRF - ZONE - capacity, btu/hr
                    requests["Rated Cooling capacity"] = (
                        2203628,
                        self.parent.u_name,
                        self.u_name,
                    )
                    # Rated data for Cooling - VRF - ZONE - SHR
                    requests["Rated Cooling SHR"] = (
                        2203629,
                        self.parent.u_name,
                        self.u_name,
                    )

            match self.parent.bdl_output_heat_type:
                case BDL_OutputHeatingTypes.FURNACE:
                    # Design data for Heating - furnace - ZONE - capacity, btu/hr
                    requests["Design Heating capacity"] = (
                        2203708,
                        self.parent.u_name,
                        self.u_name,
                    )
                case BDL_OutputHeatingTypes.HEAT_PUMP_AIR_COOLED:
                    # Design data for Heating - heat pump air cooled - ZONE - capacity, btu/hr
                    requests["Design Heating capacity"] = (
                        2203784,
                        self.parent.u_name,
                        self.u_name,
                    )
                    # Rated data for Heating - heat pump air cooled - ZONE - capacity, btu/hr
                    requests["Rated Heating capacity"] = (
                        2203790,
                        self.parent.u_name,
                        self.u_name,
                    )
                case BDL_OutputHeatingTypes.HEAT_PUMP_WATER_COOLED:
                    # Design data for Heating - heat pump water cooled - ZONE - capacity, btu/hr
                    requests["Design Heating capacity"] = (
                        2203805,
                        self.parent.u_name,
                        self.u_name,
                    )
                    # Rated data for Heating - heat pump water cooled - ZONE - capacity, btu/hr
                    requests["Rated Heating capacity"] = (
                        2203811,
                        self.parent.u_name,
                        self.u_name,
                    )
                case BDL_OutputHeatingTypes.VRF:
                    # Design data for Heating - VRF - ZONE - capacity, btu/hr
                    requests["Design Heating capacity"] = (
                        2203828,
                        self.parent.u_name,
                        self.u_name,
                    )
                    # Rated data for Heating - VRF - ZONE - capacity, btu/hr
                    requests["Rated Heating capacity"] = (
                        2203834,
                        self.parent.u_name,
                        self.u_name,
                    )

        elif self.parent.is_terminal and not self.parent.is_zonal_system:
            requests = {
                "Outside Air Ratio": (2201005, self.parent.u_name, ""),
                "Cooling Capacity": (2201006, self.parent.u_name, ""),
                "Heating Capacity": (2201008, self.parent.u_name, ""),
                "Supply Fan - Airflow": (2201012, self.parent.u_name, ""),
                "Supply Fan - Power": (2201014, self.parent.u_name, ""),
                "Supply Fan - Min Flow Ratio": (2201022, self.parent.u_name, ""),
            }

            match self.parent.output_cool_type:
                case BDL_OutputCoolingTypes.CHILLED_WATER:
                    # Design data for Cooling - chilled water - SYSTEM - capacity, btu/hr
                    requests["Design Cooling capacity"] = (
                        2203015,
                        self.parent.u_name,
                        "",
                    )
                    # Design data for Cooling - chilled water - SYSTEM - SHR
                    requests["Design Cooling SHR"] = (2203016, self.parent.u_name, "")
                    # Rated data for Cooling - chilled water - SYSTEM - capacity, btu/hr
                    requests["Rated Cooling capacity"] = (
                        2203026,
                        self.parent.u_name,
                        "",
                    )
                    # Rated data for Cooling - chilled water - SYSTEM - SHR
                    requests["Rated Cooling SHR"] = (2203027, self.parent.u_name, "")
                case BDL_OutputCoolingTypes.DX_AIR_COOLED:
                    # Design data for Cooling - DX air cooled - SYSTEM - capacity, btu/hr
                    requests["Design Cooling capacity"] = (
                        2203083,
                        self.parent.u_name,
                        "",
                    )
                    # Design data for Cooling - DX air cooled - SYSTEM - SHR
                    requests["Design Cooling SHR"] = (2203084, self.parent.u_name, "")
                    # Rated data for Cooling - DX air cooled - SYSTEM - capacity, btu/hr
                    requests["Rated Cooling capacity"] = (
                        2203092,
                        self.parent.u_name,
                        "",
                    )
                    # Rated data for Cooling - DX air cooled - SYSTEM - SHR
                    requests["Rated Cooling SHR"] = (2203093, self.parent.u_name, "")
                case BDL_OutputCoolingTypes.DX_WATER_COOLED:
                    # Design data for Cooling - DX water cooled - SYSTEM - capacity, btu/hr
                    requests["Design Cooling capacity"] = (
                        2203143,
                        self.parent.u_name,
                        "",
                    )
                    # Design data for Cooling - DX water cooled - SYSTEM - SHR
                    requests["Design Cooling SHR"] = (2203144, self.parent.u_name, "")
                    # Rated data for Cooling - DX water cooled - SYSTEM - capacity, btu/hr
                    requests["Rated Cooling capacity"] = (
                        2203152,
                        self.parent.u_name,
                        "",
                    )
                    # Rated data for Cooling - DX water cooled - SYSTEM - SHR
                    requests["Rated Cooling SHR"] = (2203153, self.parent.u_name, "")
                case BDL_OutputCoolingTypes.VRF:
                    # Design data for Cooling - VRF - SYSTEM - capacity, btu/hr
                    requests["Design Cooling capacity"] = (
                        2203207,
                        self.parent.u_name,
                        "",
                    )
                    # Design data for Cooling - VRF - SYSTEM - SHR
                    requests["Design Cooling SHR"] = (2203208, self.parent.u_name, "")
                    # Rated data for Cooling - VRF - SYSTEM - capacity, btu/hr
                    requests["Rated Cooling capacity"] = (
                        2203216,
                        self.parent.u_name,
                        "",
                    )
                    # Rated data for Cooling - VRF - SYSTEM - SHR
                    requests["Rated Cooling SHR"] = (2203217, self.parent.u_name, "")

            match self.parent.output_heat_type:
                case BDL_OutputHeatingTypes.FURNACE:
                    requests["Design Heating capacity"] = (
                        2203296,
                        self.parent.u_name,
                        "",
                    )
                case BDL_OutputHeatingTypes.HEAT_PUMP_AIR_COOLED:
                    # Design data for Heating - heat pump air cooled - SYSTEM - capacity, btu/hr
                    requests["Design Heating capacity"] = (
                        2203372,
                        self.parent.u_name,
                        "",
                    )
                    # Rated data for Heating - heat pump air cooled - SYSTEM - capacity, btu/hr
                    requests["Rated Heating capacity"] = (
                        2203378,
                        self.parent.u_name,
                        "",
                    )
                case BDL_OutputHeatingTypes.HEAT_PUMP_WATER_COOLED:
                    # Design data for Heating - heat pump water cooled - SYSTEM - capacity, btu/hr
                    requests["Design Heating capacity"] = (
                        2203414,
                        self.parent.u_name,
                        "",
                    )
                    # Rated data for Heating - heat pump water cooled - SYSTEM - capacity, btu/hr
                    requests["Rated Heating capacity"] = (
                        2203420,
                        self.parent.u_name,
                        "",
                    )
                case BDL_OutputHeatingTypes.VRF:
                    # Design data for Heating - VRF - SYSTEM - capacity, btu/hr
                    requests["Design Heating capacity"] = (
                        2203460,
                        self.parent.u_name,
                        "",
                    )
                    # Rated data for Heating - VRF - SYSTEM - capacity, btu/hr
                    requests["Rated Heating capacity"] = (
                        2203466,
                        self.parent.u_name,
                        "",
                    )

        else:
            requests.update(
                {
                    "Zone Supply Airflow": (
                        2201045,
                        self.parent.u_name,
                        self.u_name,
                    ),
                    "Zone Exhaust Airflow": (
                        2201046,
                        self.parent.u_name,
                        self.u_name,
                    ),
                    "Zone Minimum Airflow Ratio": (
                        2201048,
                        self.parent.u_name,
                        self.u_name,
                    ),
                    "Zone Outside Airflow": (
                        2201049,
                        self.parent.u_name,
                        self.u_name,
                    ),
                    "Zone Cooling Capacity": (
                        2201050,
                        self.parent.u_name,
                        self.u_name,
                    ),
                    "Zone Sensible Heat Ratio": (
                        2201051,
                        self.parent.u_name,
                        self.u_name,
                    ),
                    "Zone Heating Capacity": (
                        2201053,
                        self.parent.u_name,
                        self.u_name,
                    ),
                    "Zone Multiplier": (
                        2201055,
                        self.parent.u_name,
                        self.u_name,
                    ),
                }
            )

        if self.get_inp(BDL_ZoneKeywords.TERMINAL_TYPE) in [
            BDL_TerminalTypes.TERMINAL_IU,
            BDL_TerminalTypes.CEILING_IU,
            BDL_TerminalTypes.SERIES_PIU,
            BDL_TerminalTypes.PARALLEL_PIU,
        ]:
            requests.update(
                {
                    "Powered Induction Units - Fan Flow": (
                        2202001,
                        self.parent.u_name,
                        self.u_name,
                    ),
                    "Powered Induction Units - Cold Deck Flow": (
                        2202002,
                        self.parent.u_name,
                        self.u_name,
                    ),
                    "Powered Induction Units - Cold Deck Minimum Airflow Ratio": (
                        2202003,
                        self.parent.u_name,
                        self.u_name,
                    ),
                }
            )

        if self.get_inp(BDL_ZoneKeywords.TERMINAL_TYPE) in [
            BDL_TerminalTypes.SERIES_PIU,
            BDL_TerminalTypes.PARALLEL_PIU,
        ]:
            requests.update(
                {
                    "Powered Induction Units - Fan kW": (
                        2202006,
                        self.parent.u_name,
                        self.u_name,
                    ),
                }
            )

        if self.get_inp(BDL_ZoneKeywords.TERMINAL_TYPE) in [
            BDL_TerminalTypes.DUAL_DUCT,
            BDL_TerminalTypes.MULTIZONE,
        ]:
            requests.update(
                {
                    "Dual-Duct/Multizone Boxes - Cold Deck Airflow": (
                        2201056,
                        self.parent.u_name,
                        self.u_name,
                    ),
                    "Dual-Duct/Multizone Boxes - Cold Deck Minimum Flow Ratio": (
                        2201057,
                        self.parent.u_name,
                        self.u_name,
                    ),
                    "Dual-Duct/Multizone Boxes - Hot Deck Airflow": (
                        2201058,
                        self.parent.u_name,
                        self.u_name,
                    ),
                    "Dual-Duct/Multizone Boxes - Hot Deck Minimum Flow Ratio": (
                        2201059,
                        self.parent.u_name,
                        self.u_name,
                    ),
                    "Dual-Duct/Multizone Boxes - Outlet Airflow": (
                        2201060,
                        self.parent.u_name,
                        self.u_name,
                    ),
                    "Dual-Duct/Multizone Boxes - Outlet Minimum Flow Ratio": (
                        2201061,
                        self.parent.u_name,
                        self.u_name,
                    ),
                }
            )

        return requests

    def insert_to_rpd(self):
        """Insert zone object into the rpd data structure."""
        self.parent_building_segment.zones.append(self.zone_data_structure)

    def determine_if_dcv(self):
        # Default flag values
        occ_cfm_allows_dcv_to_take_effect = (
            self.parent.get_inp(BDL_SystemKeywords.ZONE_OA_METHOD)
            == BDL_ZoneOAMethodsOptions.SUM_OCC_AND_AREA
        )
        min_oa_sch_allows_dcv_to_take_effect = (
            self.parent.get_obj(self.parent.get_inp(BDL_SystemKeywords.MIN_AIR_SCH))
            is None
        )
        zone_is_attached_to_sys_with_terminal_inputs = (
            self.parent.get_inp(BDL_SystemKeywords.TYPE)
            in self.parent.terminal_selection_system_types
        )

        # If parent system uses MAX-OCC-OR-AREA, determine if occupancy-based OA flow rate ever takes precedence
        if (
            self.parent.get_inp(BDL_SystemKeywords.ZONE_OA_METHOD)
            == BDL_ZoneOAMethodsOptions.MAX_OCC_OR_AREA
        ):
            space = self.get_obj(self.get_inp(BDL_ZoneKeywords.SPACE))
            space_occ_sch = space.get_obj(
                space.get_inp(BDL_SpaceKeywords.PEOPLE_SCHEDULE)
            )
            max_occ_fraction = self.try_max(space_occ_sch.hourly_values)
            space_number_of_people = self.try_float(
                space.get_inp(BDL_SpaceKeywords.NUMBER_OF_PEOPLE)
            )

            # Calculate the total cfm for each scenario
            occ_based_cfm = (
                self.try_float(self.get_inp(BDL_ZoneKeywords.OA_FLOW_PER))
                * space_number_of_people
                * max_occ_fraction
                if (space_number_of_people and max_occ_fraction)
                else None
            )
            ach_based_cfm = (
                (
                    self.try_float(space.get_inp(BDL_SpaceKeywords.VOLUME))
                    * self.try_float(self.get_inp(BDL_ZoneKeywords.OA_CHANGES))
                )
                / 60
                if self.try_float(self.get_inp(BDL_ZoneKeywords.OA_CHANGES))
                else 0
            )
            area_based_cfm = (
                self.try_float(space.get_inp(BDL_SpaceKeywords.AREA))
                * self.try_float(self.get_inp(BDL_ZoneKeywords.OA_FLOW_AREA))
                if self.try_float(self.get_inp(BDL_ZoneKeywords.OA_FLOW_AREA))
                else 0
            )

            # Determine whether the OA/person rate exceeds the OA CFM/sf and the ACH rate during max occupancy periods
            occ_cfm_allows_dcv_to_take_effect = (
                occ_based_cfm > ach_based_cfm and occ_based_cfm > area_based_cfm
            )

        system_min_oa_sch = self.parent.get_obj(
            self.parent.get_inp(BDL_SystemKeywords.MIN_AIR_SCH)
        )
        system_min_oa_method = self.parent.get_inp(BDL_SystemKeywords.MIN_OA_METHOD)
        system_fan_sch = self.parent.get_obj(
            self.parent.get_inp(BDL_SystemKeywords.FAN_SCHEDULE)
        )
        system_dcv_oa_methods = [
            BDL_SystemMinimumOutdoorAirControlOptions.DCV_RETURN_SENSOR,
            BDL_SystemMinimumOutdoorAirControlOptions.DCV_ZONE_SENSORS,
        ]
        zone_dcv_flow_reset_options = [
            BDL_MinFlowControlOptions.DCV_RESET_DOWN,
            BDL_MinFlowControlOptions.DCV_RESET_UP_DOWN,
        ]

        if system_min_oa_sch and (
            not zone_is_attached_to_sys_with_terminal_inputs
            or (
                zone_is_attached_to_sys_with_terminal_inputs
                and self.get_inp(BDL_ZoneKeywords.MIN_FLOW_CTRL)
                not in zone_dcv_flow_reset_options
            )
        ):
            min_oa_sch_allows_dcv_to_take_effect = (
                any(
                    system_min_oa_sch.hourly_values[i] == -999
                    for i in range(len(system_min_oa_sch.hourly_values))
                )
                if system_fan_sch is None
                else any(
                    system_min_oa_sch.hourly_values[i] == -999
                    for i in range(len(system_fan_sch.hourly_values))
                    if system_fan_sch.hourly_values[i] == 1
                )
            )

        if (
            zone_is_attached_to_sys_with_terminal_inputs
            and self.get_inp(BDL_ZoneKeywords.MIN_FLOW_CTRL)
            in zone_dcv_flow_reset_options
        ):
            terminal_flow_schedules = [
                sch
                for sch in [
                    self.get_obj(self.get_inp(BDL_ZoneKeywords.MIN_FLOW_SCH)),
                    self.get_obj(self.get_inp(BDL_ZoneKeywords.CMIN_FLOW_SCH)),
                    self.get_obj(self.get_inp(BDL_ZoneKeywords.HMIN_FLOW_SCH)),
                ]
                if sch is not None
            ]

            # if MIN-FLOW-SCH, CMIN-FLOW-SCH or HMIN-FLOW-SCH are specified
            if any(terminal_flow_schedules):
                # check the system min OA method to determine if the terminal flow schedules could affect DCV
                if system_min_oa_method in system_dcv_oa_methods:
                    min_oa_sch_allows_dcv_to_take_effect = True

                else:
                    # check if hourly value is -999 for all flow schedules while the fan schedule value is 1
                    min_oa_sch_allows_dcv_to_take_effect = False
                    for i in range(len(terminal_flow_schedules[0].hourly_values)):
                        if (
                            system_fan_sch is None
                            or system_fan_sch.hourly_values[i] == 1
                        ):
                            if all(
                                sched.hourly_values[i] == -999
                                for sched in terminal_flow_schedules
                            ):
                                min_oa_sch_allows_dcv_to_take_effect = True
                                break

            else:
                min_oa_sch_allows_dcv_to_take_effect = True

        # Check if DCV conditions are met
        dcv_conditions_are_met = (
            min_oa_sch_allows_dcv_to_take_effect
            and occ_cfm_allows_dcv_to_take_effect
            and (
                (
                    zone_is_attached_to_sys_with_terminal_inputs
                    and self.get_inp(BDL_ZoneKeywords.MIN_FLOW_CTRL)
                    in zone_dcv_flow_reset_options
                )
                or system_min_oa_method in system_dcv_oa_methods
            )
        )

        return dcv_conditions_are_met

    def calculate_fan_power(self, airflow, pressure_rise, total_efficiency):
        pressure_rise_pa = self.try_convert_units(pressure_rise, "in_WC", "pascal")
        airflow_m3_s = self.try_convert_units(airflow, "cfm", "m3/s")

        if pressure_rise_pa and airflow_m3_s and total_efficiency:
            return pressure_rise_pa * airflow_m3_s / total_efficiency / 1000

    def populate_zonal_exhaust(self, exhaust_airflow):
        self.exhaust_fan = Fan()
        self.exhaust_fan.name = self.u_name + " EF"
        self.rmd.zonal_exh_fan_names.append(self.exhaust_fan.name)
        self.exhaust_fan.design_airflow = exhaust_airflow
        self.exhaust_fan.is_airflow_sized_based_on_design_day = False

        if self.get_inp(BDL_ZoneKeywords.EXHAUST_STATIC) is not None:
            self.exhaust_fan.specification_method = (
                FanSpecificationMethodOptions.DETAILED
            )
            self.exhaust_fan.design_pressure_rise = self.try_float(
                self.get_inp(BDL_ZoneKeywords.EXHAUST_STATIC)
            )
            self.exhaust_fan.total_efficiency = self.try_float(
                self.get_inp(BDL_ZoneKeywords.EXHAUST_EFF)
            )
            if (
                self.exhaust_fan.design_pressure_rise
                and self.exhaust_fan.total_efficiency
            ):
                self.exhaust_fan.design_electric_power = self.calculate_fan_power(
                    exhaust_airflow,
                    self.exhaust_fan.design_pressure_rise,
                    self.exhaust_fan.total_efficiency,
                )

        else:
            self.exhaust_fan.specification_method = FanSpecificationMethodOptions.SIMPLE
            zone_ef_power_per_flow = self.try_float(
                self.get_inp(BDL_ZoneKeywords.EXHAUST_KW_FLOW)
            )
            if zone_ef_power_per_flow:
                self.exhaust_fan.design_electric_power = (
                    zone_ef_power_per_flow * exhaust_airflow
                )


class Terminal:

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

    terminal_fan_type_map = {
        BDL_ZoneFanControlOptions.CONSTANT_VOLUME: TerminalOptions.CONSTANT_AIR_VOLUME,
        BDL_ZoneFanControlOptions.VARIABLE_VOLUME: TerminalOptions.VARIABLE_AIR_VOLUME,
    }

    def __init__(self, zone):
        self.zone = zone
        self.data_structure = {}

        # terminal data elements as a list of [Main Terminal, Baseboard Terminal, DOAS Terminal]
        self.name = None
        self.reporting_name = None
        self.notes = None
        self.type = None
        self.served_by_heating_ventilating_air_conditioning_system = None
        self.heating_source = None
        self.heating_from_loop = None
        self.cooling_source = None
        self.cooling_from_loop = None
        self.fan = None
        self.fan_configuration = None
        self.primary_airflow = None
        self.secondary_airflow = None
        self.max_heating_airflow = None
        self.supply_design_heating_setpoint_temperature = None
        self.supply_design_cooling_setpoint_temperature = None
        self.temperature_control = None
        self.minimum_airflow = None
        self.minimum_outdoor_airflow = None
        self.minimum_outdoor_airflow_multiplier_schedule = None
        self.heating_capacity = None
        self.cooling_capacity = None
        self.is_supply_ducted = None
        self.has_demand_control_ventilation = None
        self.is_fan_first_stage_heat = None

    def populate_data_elements(self, terminal_type, output_data, has_dcv):
        """Populate data elements for terminal object."""

        has_induction = self.zone.get_inp(BDL_ZoneKeywords.TERMINAL_TYPE) in [
            BDL_TerminalTypes.TERMINAL_IU,
            BDL_TerminalTypes.CEILING_IU,
            BDL_TerminalTypes.SERIES_PIU,
            BDL_TerminalTypes.PARALLEL_PIU,
        ]

        zone_supply_airflow = output_data.get("Zone Supply Airflow")
        minimum_outdoor_airflow = output_data.get("Zone Outside Airflow")

        if terminal_type == "main":
            self.name = self.zone.u_name + " MainTerminal"
            self.type = self.populate_main_terminal_type()
            self.served_by_heating_ventilating_air_conditioning_system = (
                self.zone.parent.u_name
            )
            self.supply_design_heating_setpoint_temperature = self.zone.try_float(
                self.zone.parent.get_inp(BDL_SystemKeywords.MAX_SUPPLY_T)
            )
            self.supply_design_cooling_setpoint_temperature = self.zone.try_float(
                self.zone.parent.get_inp(BDL_SystemKeywords.MIN_SUPPLY_T)
            )

            if self.zone.parent.is_terminal:
                self.zone.terminal_fan = Fan()
                self.zone.terminal_fan.name = self.zone.u_name + " MainTerminal Fan"
                self.zone.terminal_fan.specification_method = (
                    FanSpecificationMethodOptions.DETAILED
                    if self.zone.parent.get_inp(BDL_SystemKeywords.SUPPLY_STATIC)
                    is not None
                    else FanSpecificationMethodOptions.SIMPLE
                )
                self.zone.terminal_fan.design_pressure_rise = self.zone.try_float(
                    self.zone.parent.get_inp(BDL_SystemKeywords.SUPPLY_STATIC)
                )
                self.zone.terminal_fan.motor_efficiency = self.zone.try_float(
                    self.zone.parent.get_inp(BDL_SystemKeywords.SUPPLY_MTR_EFF)
                )
                supply_mech_eff = self.zone.try_float(
                    self.zone.parent.get_inp(BDL_SystemKeywords.SUPPLY_MECH_EFF)
                )
                if self.zone.terminal_fan.motor_efficiency and supply_mech_eff:
                    self.zone.terminal_fan.total_efficiency = (
                        self.zone.terminal_fan.motor_efficiency * supply_mech_eff
                    )
                self.temperature_control = (
                    self.get_terminal_system_temperature_control()
                )
                if self.zone.parent.get_inp(BDL_SystemKeywords.SUPPLY_FLOW) is not None:
                    self.zone.terminal_fan.is_airflow_sized_based_on_design_day = False
                if self.zone.terminal_fan.is_airflow_sized_based_on_design_day is None:
                    self.zone.terminal_fan.is_airflow_sized_based_on_design_day = (
                        # If the zone has assigned flow rates, the fan is not sized based on design day
                        not (
                            self.zone.get_inp(BDL_ZoneKeywords.ASSIGNED_FLOW)
                            or self.zone.get_inp(BDL_ZoneKeywords.HASSIGNED_FLOW)
                            or self.zone.get_inp(BDL_ZoneKeywords.FLOW_AREA)
                            or self.zone.get_inp(BDL_ZoneKeywords.HFLOW_AREA)
                            or self.zone.get_inp(BDL_ZoneKeywords.AIR_CHANGES_HR)
                            or self.zone.get_inp(BDL_ZoneKeywords.HAIR_CHANGES_HR)
                            or self.zone.get_inp(BDL_ZoneKeywords.MIN_FLOW_AREA)
                            or self.zone.get_inp(BDL_ZoneKeywords.HMIN_FLOW_AREA)
                        )
                    )

                self.heating_capacity = self.zone.try_abs(
                    self.zone.try_float(
                        self.zone.parent.get_inp(BDL_SystemKeywords.HEATING_CAPACITY)
                    )
                )
                if not self.heating_capacity:
                    self.heating_capacity = self.zone.try_abs(
                        output_data.get("Rated Heating capacity")
                    )
                if not self.heating_capacity:
                    self.heating_capacity = self.zone.try_abs(
                        output_data.get("Heating Capacity")
                    )
                self.cooling_capacity = self.zone.try_abs(
                    self.zone.try_float(
                        self.zone.parent.get_inp(BDL_SystemKeywords.COOLING_CAPACITY)
                    )
                )
                if not self.cooling_capacity:
                    self.cooling_capacity = self.zone.try_abs(
                        output_data.get("Rated Cooling capacity")
                    )
                if not self.cooling_capacity:
                    self.cooling_capacity = self.zone.try_abs(
                        output_data.get("Cooling Capacity")
                    )
                self.heating_source = self.heat_source_map.get(
                    self.zone.parent.get_inp(BDL_SystemKeywords.HEAT_SOURCE)
                )
                self.heating_from_loop = self.zone.parent.get_inp(
                    BDL_SystemKeywords.HW_LOOP
                )
                self.cooling_source = (
                    CoolingSourceOptions.CHILLED_WATER
                    if self.cooling_capacity
                    else None
                )

                if self.zone.parent.is_zonal_system:
                    self.zone.terminal_fan.design_airflow = output_data.get(
                        "Zone Supply Airflow"
                    )
                    zone_fan_power = output_data.get("Zone Fan Power", 0)
                    self.zone.terminal_fan.design_electric_power = max(
                        0,
                        (
                            zone_fan_power
                            if self.zone.exhaust_fan is None
                            or self.zone.exhaust_fan.design_electric_power is None
                            else zone_fan_power
                            - self.zone.exhaust_fan.design_electric_power
                        ),
                    )

                else:
                    self.zone.terminal_fan.design_airflow = output_data.get(
                        "Supply Fan - Airflow"
                    )
                    self.zone.terminal_fan.design_electric_power = output_data.get(
                        "Supply Fan - Power"
                    )

            else:  # not self.parent.is_terminal:
                if self.zone.parent.is_zonal_system:
                    self.zone.parent.supply_fan.design_electric_power = max(
                        0,
                        (
                            self.zone.parent.supply_fan.design_electric_power
                            if self.zone.exhaust_fan is None
                            or self.zone.exhaust_fan.design_electric_power is None
                            else self.zone.parent.supply_fan.design_electric_power
                            - self.zone.exhaust_fan.design_electric_power
                        ),
                    )

                else:
                    self.heating_source = self.heat_source_map.get(
                        self.zone.parent.get_inp(BDL_SystemKeywords.ZONE_HEAT_SOURCE)
                    )
                    self.heating_from_loop = self.zone.get_inp(BDL_ZoneKeywords.HW_LOOP)
                    self.heating_capacity = self.zone.try_abs(
                        output_data.get("Zone Heating Capacity")
                    )
                    self.cooling_capacity = output_data.get("Zone Cooling Capacity")
                    self.cooling_source = (
                        CoolingSourceOptions.CHILLED_WATER
                        if self.cooling_capacity
                        else None
                    )

                if self.zone.parent.is_derived_system:
                    self.served_by_heating_ventilating_air_conditioning_system = (
                        self.zone.parent.sys_id
                    )

                else:
                    self.served_by_heating_ventilating_air_conditioning_system = (
                        self.zone.parent.u_name
                    )

                zone_supply_airflow = output_data.get("Zone Supply Airflow")
                minimum_airflow_ratio = output_data.get("Zone Minimum Airflow Ratio")
                if (
                    zone_supply_airflow is not None
                    and minimum_airflow_ratio is not None
                ):
                    self.minimum_airflow = zone_supply_airflow * minimum_airflow_ratio

            if has_induction:
                zone_supply_airflow = output_data.get("Zone Supply Airflow")
                piu_fan_flow = output_data.get("Powered Induction Units - Fan Flow")
                piu_fan_kw = output_data.get("Powered Induction Units - Fan kW")
                piu_cd_flow = output_data.get(
                    "Powered Induction Units - Cold Deck Flow"
                )
                piu_cd_min_airflow_ratio = output_data.get(
                    "Powered Induction Units - Cold Deck Minimum Airflow Ratio"
                )

                if (
                    self.zone.get_inp(BDL_ZoneKeywords.INDUCED_AIR_SRC)
                    == BDL_ZoneInductionSourceOptions.SUPPLY_AIR
                ):
                    self.primary_airflow = zone_supply_airflow
                    self.secondary_airflow = 0

                elif (
                    self.zone.get_inp(BDL_ZoneKeywords.TERMINAL_TYPE)
                    == BDL_TerminalTypes.SERIES_PIU
                ):
                    self.primary_airflow = piu_cd_flow
                    if (
                        self.primary_airflow
                        and piu_fan_flow
                        and piu_cd_min_airflow_ratio
                    ):
                        self.secondary_airflow = (
                            piu_fan_flow
                            - self.primary_airflow * piu_cd_min_airflow_ratio
                        )
                    self.fan_configuration = TerminalFanConfigurationOptions.SERIES

                else:
                    self.primary_airflow = piu_cd_flow
                    self.secondary_airflow = piu_fan_flow

                # Only populate MainTerminal Fan data elements here if the zone TERMINAL-TYPE is SERIES-PIU or PARALLEL-PIU
                if self.zone.get_inp(BDL_ZoneKeywords.TERMINAL_TYPE) in [
                    BDL_TerminalTypes.SERIES_PIU,
                    BDL_TerminalTypes.PARALLEL_PIU,
                ]:
                    self.zone.terminal_fan.name = self.zone.u_name + " MainTerminal Fan"
                    self.zone.terminal_fan.design_airflow = piu_fan_flow
                    self.is_fan_first_stage_heat = self.is_fan_first_stage_map.get(
                        self.zone.get_inp(BDL_ZoneKeywords.ZONE_FAN_RUN)
                    )
                    if self.zone.get_inp(BDL_ZoneKeywords.ZONE_FAN_FLOW):
                        self.zone.terminal_fan.is_airflow_sized_based_on_design_day = (
                            False
                        )
                    self.zone.terminal_fan.specification_method = (
                        FanSpecificationMethodOptions.SIMPLE
                    )
                    self.zone.terminal_fan.design_electric_power = piu_fan_kw
                    self.type = self.terminal_fan_type_map.get(
                        self.zone.get_inp(BDL_ZoneKeywords.ZONE_FAN_CTRL)
                    )
                    self.fan_configuration = (
                        self.fan_configuration
                        or TerminalFanConfigurationOptions.PARALLEL
                    )

            elif self.zone.get_inp(BDL_ZoneKeywords.TERMINAL_TYPE) in [
                BDL_TerminalTypes.DUAL_DUCT,
                BDL_TerminalTypes.MULTIZONE,
            ]:
                self.primary_airflow = output_data.get(
                    "Dual-Duct/Multizone Boxes - Outlet Airflow", 0
                )
                self.secondary_airflow = 0

            else:
                self.primary_airflow = zone_supply_airflow
                self.secondary_airflow = 0

        elif terminal_type == "baseboard":
            self.name = self.zone.u_name + " BaseboardTerminal"
            self.type = TerminalOptions.BASEBOARD
            self.is_supply_ducted = False
            self.has_demand_control_ventilation = False
            self.cooling_capacity = 0.0
            self.heating_source = self.heat_source_map.get(
                self.zone.parent.get_inp(BDL_SystemKeywords.BASEBOARD_SOURCE)
            )
            self.heating_from_loop = self.zone.parent.get_inp(
                BDL_SystemKeywords.BBRD_LOOP
            )
            self.heating_capacity = self.zone.try_abs(
                self.zone.try_float(
                    self.zone.get_inp(BDL_ZoneKeywords.BASEBOARD_RATING)
                )
            )
            self.has_demand_control_ventilation = False

        elif terminal_type == "doas":
            doas_system = self.zone.get_obj(
                self.zone.parent.get_inp(BDL_SystemKeywords.DOA_SYSTEM)
            )
            self.name = self.zone.u_name + " DOASTerminal"
            self.served_by_heating_ventilating_air_conditioning_system = (
                doas_system.u_name
            )
            self.supply_design_heating_setpoint_temperature = self.zone.try_float(
                doas_system.get_inp(BDL_SystemKeywords.MAX_SUPPLY_T)
            )
            self.supply_design_cooling_setpoint_temperature = self.zone.try_float(
                doas_system.get_inp(BDL_SystemKeywords.MIN_SUPPLY_T)
            )
            self.cooling_capacity = 0.0
            self.heating_capacity = 0.0
            self.minimum_outdoor_airflow = minimum_outdoor_airflow
            self.minimum_outdoor_airflow_multiplier_schedule = self.zone.get_inp(
                BDL_ZoneKeywords.MIN_AIR_SCH
            )
            self.primary_airflow = minimum_outdoor_airflow
            self.minimum_airflow = minimum_outdoor_airflow
            if (
                doas_system.fan_system.fan_control
                == FanSystemSupplyFanControlOptions.CONSTANT
                or self.zone.get_inp(BDL_ZoneKeywords.MIN_FLOW_RATIO) == 1
            ):
                self.type = TerminalOptions.CONSTANT_AIR_VOLUME
            # TODO: Account for zone minimum air flow schedule(s)
            else:
                self.type = TerminalOptions.VARIABLE_AIR_VOLUME

            # Special condition for DOAS attached to conditioned zone where the terminal DCV parameters are ignored.
            is_doas_attached_to_system = (
                self.zone.parent.get_inp(BDL_SystemKeywords.DOAS_ATTACHED_TO)
                == BDL_DOASAttachedToOptions.AHU_MIXED_AIR
            )

            self.has_demand_control_ventilation = has_dcv and (
                self.zone.parent.get_inp(BDL_SystemKeywords.MIN_OA_METHOD)
                in [
                    BDL_SystemMinimumOutdoorAirControlOptions.DCV_RETURN_SENSOR,
                    BDL_SystemMinimumOutdoorAirControlOptions.DCV_ZONE_SENSORS,
                ]
                or is_doas_attached_to_system
            )

            # Set Main Terminal DCV to False when the DOAS provides DCV directly to the zone
            self.zone.main_terminal.has_demand_control_ventilation = (
                has_dcv and is_doas_attached_to_system
            )

    def populate_data_group(self):
        self.data_structure["id"] = self.name

        terminal_data_elements = [
            "reporting_name",
            "notes",
            "type",
            "served_by_heating_ventilating_air_conditioning_system",
            "heating_source",
            "heating_from_loop",
            "cooling_source",
            "cooling_from_loop",
            "fan",
            "fan_configuration",
            "primary_airflow",
            "secondary_airflow",
            "max_heating_airflow",
            "supply_design_heating_setpoint_temperature",
            "supply_design_cooling_setpoint_temperature",
            "temperature_control",
            "minimum_airflow",
            "minimum_outdoor_airflow",
            "minimum_outdoor_airflow_multiplier_schedule",
            "heating_capacity",
            "cooling_capacity",
            "is_supply_ducted",
            "has_demand_control_ventilation",
            "is_fan_first_stage_heat",
        ]

        for attr in terminal_data_elements:
            value = getattr(self, attr, None)
            if value is not None:
                self.data_structure[attr] = value

    def insert_to_rpd(self):
        self.zone.terminals.append(self.data_structure)

    def populate_main_terminal_type(self):
        system_min_flow_ratio = self.zone.try_float(
            self.zone.parent.get_inp(BDL_SystemKeywords.MIN_FLOW_RATIO)
        )
        system_fan_control = self.zone.parent.get_inp(BDL_SystemKeywords.FAN_CONTROL)
        zone_min_flow_ratio = self.zone.try_float(
            self.zone.get_inp(BDL_ZoneKeywords.MIN_FLOW_RATIO)
        )

        if system_min_flow_ratio is None and zone_min_flow_ratio is None:
            if system_fan_control == BDL_SystemFanControlOptions.CONSTANT_VOLUME:
                return TerminalOptions.CONSTANT_AIR_VOLUME
            else:
                return TerminalOptions.VARIABLE_AIR_VOLUME
        elif (zone_min_flow_ratio and zone_min_flow_ratio < 1) or (
            system_min_flow_ratio and system_min_flow_ratio < 1
        ):
            # Override fan control of systems that have CONSTANT_VOLUME fans with a minimum flow ratio less than 1
            if (
                self.zone.parent.fan_system
                and self.zone.parent.fan_system.fan_control
                == FanSystemSupplyFanControlOptions.CONSTANT
            ):
                self.zone.parent.fan_system.fan_control = (
                    FanSystemSupplyFanControlOptions.DISCHARGE_DAMPER
                )
            return TerminalOptions.VARIABLE_AIR_VOLUME
        else:
            return TerminalOptions.CONSTANT_AIR_VOLUME

    def get_terminal_system_temperature_control(self):
        system_type = self.zone.parent.get_inp(BDL_SystemKeywords.TYPE)
        cool_control = self.zone.parent.get_inp(BDL_SystemKeywords.COOL_CONTROL)
        cool_set_t = self.zone.parent.get_inp(BDL_SystemKeywords.COOL_SET_T)
        heat_control = self.zone.parent.get_inp(BDL_SystemKeywords.HEAT_CONTROL)
        heat_set_t = self.zone.parent.get_inp(BDL_SystemKeywords.HEAT_SET_T)
        min_flow_ratio = self.zone.try_float(
            self.zone.parent.get_inp(BDL_SystemKeywords.MIN_FLOW_RATIO)
        )

        if system_type in FanSystem.multi_duct_system_types:
            return TerminalTemperatureControlOptions.OTHER

        elif system_type in FanSystem.single_duct_system_types:

            if (
                cool_control == BDL_SystemCoolControlOptions.CONSTANT
                and heat_control == BDL_SystemHeatControlOptions.CONSTANT
            ):
                if heat_set_t and cool_set_t and heat_set_t >= cool_set_t:
                    return TerminalTemperatureControlOptions.CONSTANT

            elif cool_control == BDL_SystemCoolControlOptions.WARMEST:
                return TerminalTemperatureControlOptions.OTHER

            elif cool_control == BDL_SystemCoolControlOptions.SCHEDULED:
                return TerminalTemperatureControlOptions.SCHEDULED

            elif cool_control == BDL_SystemCoolControlOptions.RESET:
                return TerminalTemperatureControlOptions.OTHER

        elif system_type in FanSystem.single_zone_system_types:
            if min_flow_ratio and min_flow_ratio < 1:
                if cool_set_t and heat_set_t and cool_set_t == heat_set_t:
                    return TerminalTemperatureControlOptions.CONSTANT
                else:
                    return TerminalTemperatureControlOptions.OTHER
            else:
                return TerminalTemperatureControlOptions.OTHER
