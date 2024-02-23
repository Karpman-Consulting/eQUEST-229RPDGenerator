from rpd_generator.bdl_structure.child_node import ChildNode


class Zone(ChildNode):
    """Zone object in the tree."""

    bdl_command = "ZONE"

    heat_source_map = {
        "NONE": None,
        "ELECTRIC": "ELECTRIC",
        "HOT-WATER": "HOT_WATER",
        "FURNACE": "OTHER",
        "DHW-LOOP": "OTHER",
        "STEAM": "OTHER",
        "HEAT-PUMP": "OTHER",
    }

    def __init__(self, u_name, parent, rmd):
        super().__init__(u_name, parent, rmd)
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
        self.thermostat_heating_setpoint_schedulue = None
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

        # terminal data elements as a list of MainTerminal, Baseboard Terminal, DOAS Terminal
        self.terminals_id = [None, None, None]
        self.terminals_reporting_name = [None, None, None]
        self.terminals_notes = [None, None, None]
        self.terminals_type = [None, None, None]
        self.terminals_served_by_heating_ventilating_air_conditioning_system = [
            None,
            None,
            None,
        ]
        self.terminals_heating_source = [None, None, None]
        self.terminals_heating_from_loop = [None, None, None]
        self.terminals_cooling_source = [None, None, None]
        self.terminals_cooling_from_loop = [None, None, None]
        self.terminals_fan = [None, None, None]
        self.terminals_fan_configuration = [None, None, None]
        self.terminals_primary_airflow = [None, None, None]
        self.terminals_secondary_airflow = [None, None, None]
        self.terminals_max_heating_airflow = [None, None, None]
        self.terminals_supply_design_heating_setpoint_temperature = [None, None, None]
        self.terminals_supply_design_cooling_setpoint_temperature = [None, None, None]
        self.terminals_temperature_control = [None, None, None]
        self.terminals_minimum_airflow = [None, None, None]
        self.terminals_minimum_outdoor_airflow = [None, None, None]
        self.terminals_minimum_outdoor_airflow_multiplier_schedule = [None, None, None]
        self.terminals_heating_capacity = [None, None, None]
        self.terminals_cooling_capacity = [None, None, None]
        self.terminals_is_supply_ducted = [None, None, None]
        self.terminals_has_demand_control_ventilation = [None, None, None]
        self.terminals_is_fan_first_stage_heat = [None, None, None]

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
        self.zonal_exhaust_fan_id = None
        self.zonal_exhaust_fan_reporting_name = None
        self.zonal_exhaust_fan_notes = None
        self.zonal_exhaust_fan_design_airflow = None
        self.zonal_exhaust_fan_is_airflow_sized_based_on_design_day = None
        self.zonal_exhaust_fan_specification_method = None
        self.zonal_exhaust_fan_design_electric_power = None
        self.zonal_exhaust_fan_design_pressure_rise = None
        self.zonal_exhaust_fan_total_efficiency = None
        self.zonal_exhaust_fan_output_validation_points = []

    def __repr__(self):
        return f"Zone(u_name='{self.u_name}', parent='{self.parent}')"

    def populate_data_elements(self):
        """Populate data elements for zone object."""
        is_piu = self.keyword_value_pairs.get("TERMINAL-TYPE") in [
            "SERIES-PIU",
            "PARALLEL-PIU",
        ]

        self.design_thermostat_cooling_setpoint = self.try_float(
            self.keyword_value_pairs.get("DESIGN-COOL-T")
        )

        self.thermostat_cooling_setpoint_schedule = self.keyword_value_pairs.get(
            "COOL-TEMP-SCH"
        )

        self.design_thermostat_heating_setpoint = self.try_float(
            self.keyword_value_pairs.get("DESIGN-HEAT-T")
        )

        self.thermostat_heating_setpoint_schedulue = self.keyword_value_pairs.get(
            "HEAT-TEMP-SCH"
        )

        self.exhaust_airflow_rate_multiplier_schedule = self.keyword_value_pairs.get(
            "EXHAUST-FAN-SCH"
        )

        # if the zone is served by a SUM system don't populate the MainTerminal data elements
        if self.parent.keyword_value_pairs.get("TYPE") == "SUM":
            return

        requests = self.get_output_requests()
        output_data = self.get_output_data(
            self.rmd.dll_path, self.rmd.doe2_data_path, self.rmd.file_path, requests
        )
        supply_airflow = self.try_float(
            output_data.get(
                "HVAC Systems - Design Parameters - Zone Design Data - General - Supply Airflow"
            )
        )
        minimum_airflow_ratio = self.try_float(
            output_data.get(
                "HVAC Systems - Design Parameters - Zone Design Data - General - Minimum Airflow Ratio"
            )
        )
        minimum_outdoor_airflow = self.try_float(
            output_data.get(
                "HVAC Systems - Design Parameters - Zone Design Data - General - Outside Airflow"
            )
        )
        heating_capacity = self.try_float(
            output_data.get(
                "HVAC Systems - Design Parameters - Zone Design Data - General - Heating Capacity"
            )
        )
        cooling_capacity = self.try_float(
            output_data.get(
                "HVAC Systems - Design Parameters - Zone Design Data - General - Cooling Capacity"
            )
        )

        # Populate MainTerminal data elements
        self.terminals_id[0] = self.u_name + " MainTerminal"
        self.terminals_served_by_heating_ventilating_air_conditioning_system[0] = (
            self.parent.u_name
        )
        self.terminals_heating_source[0] = self.heat_source_map.get(
            self.parent.keyword_value_pairs.get("ZONE-HEAT-SOURCE")
        )
        self.terminals_heating_from_loop[0] = self.keyword_value_pairs.get("HW-LOOP")
        self.terminals_primary_airflow[0] = supply_airflow
        if supply_airflow is not None and minimum_airflow_ratio is not None:
            self.terminals_minimum_airflow[0] = supply_airflow * minimum_airflow_ratio
        self.terminals_minimum_outdoor_airflow[0] = minimum_outdoor_airflow
        self.terminals_heating_capacity[0] = heating_capacity
        self.terminals_cooling_capacity[0] = cooling_capacity
        exhaust_airflow = self.try_float(self.keyword_value_pairs.get("EXHAUST-FLOW"))

        # Populate Baseboard Terminal data elements if applicable
        baseboard_control = self.keyword_value_pairs.get("BASEBOARD-CTRL")
        if baseboard_control not in [None, "NONE"]:
            self.terminals_id[1] = self.u_name + " Baseboard Terminal"
            # noinspection PyTypeChecker
            self.terminals_type[1] = "BASEBOARD"
            # noinspection PyTypeChecker
            self.terminals_is_supply_ducted[1] = False
            self.terminals_heating_source[1] = self.heat_source_map.get(
                self.keyword_value_pairs.get("BASEBOARD-SOURCE")
            )
            self.terminals_heating_from_loop[1] = self.parent.keyword_value_pairs.get("BBRD-LOOP")
            # noinspection PyTypeChecker
            self.terminals_primary_airflow[1] = 0.0
            # noinspection PyTypeChecker
            self.terminals_minimum_airflow[1] = 0.0
            # noinspection PyTypeChecker
            self.terminals_minimum_outdoor_airflow[1] = 0.0
            self.terminals_heating_capacity[1] = self.keyword_value_pairs.get("BASEBOARD-RATING")
            # noinspection PyTypeChecker
            self.terminals_cooling_capacity[1] = 0.0

        # Populate DOAS Terminal data elements if applicable
        if self.keyword_value_pairs.get("DOA-SYSTEM") is not None:
            self.terminals_id[2] = self.u_name + " DOAS Terminal"
            # noinspection PyTypeChecker
            self.terminals_heating_capacity[2] = 0.0
            # noinspection PyTypeChecker
            self.terminals_cooling_capacity[2] = 0.0

        # Only populate MainTerminal Fan data elements here if the zone TERMINAL-TYPE is SERIES-PIU or PARALLEL-PIU
        if is_piu:

            self.terminal_fan_id = self.u_name + " MainTerminal Fan"

            self.terminal_fan_design_airflow = self.try_float(
                output_data.get(
                    "HVAC Systems - Design Parameters - Zone Design Data - Powered Induction Units - Fan Flow"
                )
            )

            self.terminal_fan_specification_method = "SIMPLE"

            self.terminal_fan_design_electric_power = self.try_float(
                output_data.get(
                    "HVAC Systems - Design Parameters - Zone Design Data - Powered Induction Units - Fan kW"
                )
            )

        # Only populate MainTerminal Fan data elements here if the parent system type is FC with HW or no heat
        elif self.parent.is_terminal:

            self.terminal_fan_id = self.u_name + " MainTerminal Fan"

            self.terminal_fan_design_airflow = self.try_float(
                output_data.get(
                    "HVAC Systems - Design Parameters - Zone Design Data - General - Supply Airflow"
                )
            )

            self.terminal_fan_design_electric_power = self.try_float(
                output_data.get(
                    "HVAC Systems - Design Parameters - Zone Design Data - General - Zone Fan Power"
                )
            )

            self.terminal_fan_specification_method = "SIMPLE"

        if exhaust_airflow is not None and exhaust_airflow > 0.0:
            self.zonal_exhaust_fan_id = self.u_name + " EF"
            self.zonal_exhaust_fan_design_airflow = exhaust_airflow
            if self.keyword_value_pairs.get("EXHAUST-STATIC") is not None:
                self.zonal_exhaust_fan_specification_method = "DETAILED"
                self.zonal_exhaust_fan_design_pressure_rise = self.try_float(
                    self.keyword_value_pairs.get("EXHAUST-STATIC")
                )
                self.zonal_exhaust_fan_total_efficiency = self.try_float(
                    self.keyword_value_pairs.get("EXHAUST-EFF")
                )
                zone_fan_power = output_data.get(
                    "HVAC Systems - Design Parameters - Zone Design Data - General - Zone Fan Power"
                )
                self.zonal_exhaust_fan_design_electric_power = (
                    zone_fan_power - self.terminal_fan_design_electric_power
                )
            else:
                self.zonal_exhaust_fan_specification_method = "SIMPLE"
                zone_ef_power_per_flow = self.try_float(
                    self.keyword_value_pairs.get("EXHAUST-KW/FLOW")
                )
                self.zonal_exhaust_fan_design_electric_power = (
                    zone_ef_power_per_flow * exhaust_airflow
                )
            return

    def populate_data_group(self):
        """Populate schema structure for zone object."""

        attributes = [attr for attr in dir(self) if attr.startswith("terminals_")]
        keys = [
            attr.replace("terminals_", "") for attr in attributes
        ]  # Move outside the loop

        # Extract values for each attribute from the object only once
        terminal_value_lists = [getattr(self, attr) for attr in attributes]

        # Iterate over the values, creating dictionaries directly from zipped keys and values
        for values in zip(*terminal_value_lists):
            terminal_dict = {
                key: value for key, value in zip(keys, values) if value is not None
            }
            if terminal_dict:  # Only append if the dictionary is not empty
                self.terminals.append(terminal_dict)

        zonal_exhaust_fan_attributes = [
            "zonal_exhaust_fan_id",
            "zonal_exhaust_fan_reporting_name",
            "zonal_exhaust_fan_notes",
            "zonal_exhaust_fan_design_airflow",
            "zonal_exhaust_fan_is_airflow_sized_based_on_design_day",
            "zonal_exhaust_fan_specification_method",
            "zonal_exhaust_fan_design_electric_power",
            "zonal_exhaust_fan_design_pressure_rise",
            "zonal_exhaust_fan_total_efficiency",
        ]

        for attr in zonal_exhaust_fan_attributes:
            value = getattr(self, attr, None)
            if value is not None:
                self.zonal_exhaust_fan[attr.split("zonal_exhaust_fan_")[1]] = value

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
            "thermostat_heating_setpoint_schedulue",
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
        #      2201045,  38,  1,  6,  9,  1,  1,  1,  0, 25, 2019,  8,  1,  0, 2010   ; HVAC Systems - Design Parameters - Zone Design Data - General - Supply Airflow
        #      2201046,  38,  1,  6, 10,  1,  1,  1,  0, 25, 2019,  8,  1,  0, 2010   ; HVAC Systems - Design Parameters - Zone Design Data - General - Exhaust Airflow
        #      2201047,  38,  1,  6, 11,  1,  1,  1,  0, 28, 2019,  8,  1,  0, 2010   ; HVAC Systems - Design Parameters - Zone Design Data - General - Zone Fan Power
        #      2201048,  38,  1,  6, 12,  1,  1,  1,  0, 22, 2019,  8,  1,  0, 2010   ; HVAC Systems - Design Parameters - Zone Design Data - General - Minimum Airflow Ratio
        #      2201049,  38,  1,  6, 13,  1,  1,  1,  0, 25, 2019,  8,  1,  0, 2010   ; HVAC Systems - Design Parameters - Zone Design Data - General - Outside Airflow
        #      2201050,  38,  1,  6, 14,  1,  1,  1,  0, 64, 2019,  8,  1,  0, 2010   ; HVAC Systems - Design Parameters - Zone Design Data - General - Cooling Capacity
        #      2201051,  38,  1,  6, 15,  1,  1,  1,  0, 22, 2019,  8,  1,  0, 2010   ; HVAC Systems - Design Parameters - Zone Design Data - General - Sensible Heat Ratio
        #      2201052,  38,  1,  6, 16,  1,  1,  1,  0, 64, 2019,  8,  1,  0, 2010   ; HVAC Systems - Design Parameters - Zone Design Data - General - Heat Extraction Rate
        #      2201053,  38,  1,  6, 17,  1,  1,  1,  0, 64, 2019,  8,  1,  0, 2010   ; HVAC Systems - Design Parameters - Zone Design Data - General - Heating Capacity
        #      2201054,  38,  1,  6, 18,  1,  1,  1,  0, 64, 2019,  8,  1,  0, 2010   ; HVAC Systems - Design Parameters - Zone Design Data - General - Heat Addition Rate
        #      2201055,  38,  1,  6, 19,  1,  1,  1,  0,  1, 2019,  8,  1,  0, 2010   ; HVAC Systems - Design Parameters - Zone Design Data - General - Zone Multiplier
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

        if self.keyword_value_pairs.get("TERMINAL-TYPE") in [
            "SERIES-PIU",
            "PARALLEL-PIU",
        ]:
            #      2202001,  57,  1,  2,  9,  1,  1,  1,  0, 25, 2019,  8,  1,  0, 2010   ; HVAC Systems - Design Parameters - Zone Design Data - Powered Induction Units - Fan Flow
            #      2202002,  57,  1,  2, 10,  1,  1,  1,  0, 25, 2019,  8,  1,  0, 2010   ; HVAC Systems - Design Parameters - Zone Design Data - Powered Induction Units - Cold Deck Flow
            #      2202003,  57,  1,  2, 11,  1,  1,  1,  0, 22, 2019,  8,  1,  0, 2010   ; HVAC Systems - Design Parameters - Zone Design Data - Powered Induction Units - Cold Deck Minimum Airflow Ratio
            #      2202004,  57,  1,  2, 12,  1,  1,  1,  0, 74, 2019,  8,  1,  0, 2010   ; HVAC Systems - Design Parameters - Zone Design Data - Powered Induction Units - Reheat Temperature Rise
            #      2202005,  57,  1,  2, 13,  1,  1,  1,  0, 74, 2019,  8,  1,  0, 2010   ; HVAC Systems - Design Parameters - Zone Design Data - Powered Induction Units - Fan Air Temperature Rise
            #      2202006,  57,  1,  2, 14,  1,  1,  1,  0, 28, 2019,  8,  1,  0, 2010   ; HVAC Systems - Design Parameters - Zone Design Data - Powered Induction Units - Fan kW
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
