from rpd_generator.bdl_structure.parent_node import ParentNode
from rpd_generator.doe2_file_readers.model_output_reader import get_multiple_results
from itertools import islice


class System(ParentNode):
    """System object in the tree."""

    bdl_command = "SYSTEM"

    heat_type_map = {
        "HEAT-PUMP": "HEAT_PUMP",
        "FURNACE": "FURNACE",
        "ELECTRIC": "ELECTRIC_RESISTANCE",
        "HOT-WATER": "FLUID_LOOP",
        "NONE": "NONE",
        "STEAM": "OTHER",
        "DHW-LOOP": "OTHER",
    }
    cool_type_map = {
        "ELEC-DX": "DIRECT_EXPANSION",
        "CHILLED-WATER": "FLUID_LOOP",
        "NONE": "NONE",
    }
    supply_fan_map = {
        "CONSTANT-VOLUME": "CONSTANT",
        "SPEED": "VARIABLE_SPEED_DRIVE",
        #  "": "MULTISPEED",  no eQUEST options map to MULTISPEED in DOE2.3
        "INLET": "INLET_VANE",
        "DISCHARGE": "DISCHARGE_DAMPER",
        "FAN-EIR-FPLR": "VARIABLE_SPEED_DRIVE",
    }
    unocc_fan_operation_map = {
        "CYCLE-ON-ANY": "CYCLING",
        "CYCLE-ON-FIRST": "CYCLING",
        "STAY-OFF": "KEEP_OFF",
        "ZONE-FANS-ONLY": "OTHER",
    }
    system_cooling_type_map = {
        "PSZ": "DIRECT_EXPANSION",
        "PMZS": "DIRECT_EXPANSION",
        "PVAVS": "DIRECT_EXPANSION",
        "PVVT": "DIRECT_EXPANSION",
        "HP": "DIRECT_EXPANSION",  # IS WATER LOOP HEAT PUMP CONSIDERED DIRECT_EXPANSION???
        "SZRH": "FLUID_LOOP",
        "VAVS": "FLUID_LOOP",
        "RHFS": "FLUID_LOOP",
        "DDS": "FLUID_LOOP",
        "MZS": "FLUID_LOOP",
        "PIU": None,  # Mapping updated in populate_cooling_system method
        "FC": "FLUID_LOOP",
        "IU": "FLUID_LOOP",
        "UVT": "NONE",
        "UHT": "NONE",
        "RESYS2": "DIRECT_EXPANSION",
        "CBVAV": "FLUID_LOOP",
        "SUM": "NONE",
        "DOAS": None,  # Mapping updated in populate_cooling_system method
    }
    economizer_map = {
        "FIXED": "FIXED_FRACTION",
        "OA-TEMP": "FIXED_DRY_BULB",
        "OA-ENTHALPY": "FIXED_ENTHALPY",
        "DUAL-TEMP": "DIFFERENTIAL_TEMPERATURE",
        "DUAL-ENTHALPY": "DIFFERENTIAL_ENTHALPY",
    }
    recovery_type_map = {
        "SENSIBLE-HX": "SENSIBLE_HEAT_EXCHANGE",
        "ENTHALPY-HX": "ENTHALPY_HEAT_EXCHANGE",
        "SENSIBLE-WHEEL": "SENSIBLE_HEAT_WHEEL",
        "ENTHALPY-WHEEL": "ENTHALPY_HEAT_WHEEL",
        "HEAT-PIPE": "HEAT_PIPE",
    }
    air_energy_recovery_map = {
        "NO": "NONE",
        "RELIEF-ONLY": None,  # Mapping updated in populate_air_energy_recovery method
        "EXHAUST-ONLY": None,  # Mapping updated in populate_air_energy_recovery method
        "RELIEF+EXHAUST": None,  # Mapping updated in populate_air_energy_recovery method
        "YES": None,  # Mapping updated in populate_air_energy_recovery method
    }
    er_operation_map = {
        "WHEN-FANS-ON": "WHEN_FANS_ON",
        "WHEN-MIN-OA": "WHEN_MINIMUM_OUTSIDE_AIR",
        "ERV-SCHEDULE": "SCHEDULED",
        "OA-EXHAUST-DT": "OTHER",
        "OA-EXHAUST-DH": "OTHER",
    }
    er_sat_control_map = {
        "FLOAT": "OTHER",
        "FIXED-SETPT": "FIXED_SETPOINT",
        "MIXED-AIR-RESET": "MIXED_AIR_RESET",
    }
    dcv_map = {
        "FRAC-OF-DESIGN-FLOW": "NONE",
        "FRAC-OF-HOURLY-FLOW": "NONE",
        "DCV-RETURN-SENSOR": "CO2_RETURN_AIR",
        "DCV-ZONE-SENSORS": "CO2_ZONE",
    }

    def __init__(self, u_name):
        super().__init__(u_name)

        self.system_data_structure = {}
        self.omit = False

        # system data elements with children
        self.fan_system = {}
        self.heating_system = {}
        self.cooling_system = {}
        self.preheat_system = {}

        # fan system data elements
        self.fan_sys_id = None
        self.fan_sys_reporting_name = None
        self.fan_sys_notes = None
        self.fan_sys_supply_fans = []
        self.fan_sys_return_fans = []
        self.fan_sys_exhaust_fans = []
        self.fan_sys_relief_fans = []
        self.fan_sys_air_economizer = {}
        self.fan_sys_air_energy_recovery = {}
        self.fan_sys_temp_control = None
        self.fan_sys_operation_during_occ = None
        self.fan_sys_operation_during_unocc = None
        self.fan_sys_has_unocc_central_heat_lockout = None
        self.fan_sys_fan_control = None
        self.fan_sys_reset_diff_temp = None
        self.fan_sys_sat_reset_load_fraction = None
        self.fan_sys_sat_reset_schedule = None
        self.fan_sys_fan_volume_reset_type = None
        self.fan_sys_fan_volume_reset_fraction = None
        self.fan_sys_operating_schedule = None
        self.fan_sys_min_airflow = None
        self.fan_sys_min_oa_airflow = None
        self.fan_sys_max_oa_airflow = None
        self.fan_sys_air_filter_merv = None
        self.fan_sys_has_fully_ducted_return = None
        self.fan_sys_dcv_control = None

        # heating system data elements
        self.heat_sys_id = None
        self.heat_sys_reporting_name = None
        self.heat_sys_notes = None
        self.heat_sys_type = None
        self.heat_sys_phase = None
        self.heat_sys_efficiency = None
        self.heat_sys_capacity = None
        self.heat_sys_peak_load = None

        # cooling system data elements
        self.cool_sys_id = None
        self.cool_sys_reporting_name = None
        self.cool_sys_notes = None
        self.cool_sys_type = None
        self.cool_sys_design_total_capacity = None
        self.cool_sys_design_sensible_capacity = None
        self.cool_sys_rated_total_capacity = None
        self.cool_sys_rated_sensible_capacity = None
        self.cool_sys_oversizing_factor = None
        self.cool_sys_is_sized_based_on_design_day = None
        self.cool_sys_chw_loop = None
        self.cool_sys_cw_loop = None
        self.cool_sys_efficiency_metric_values = []
        self.cool_sys_efficiency_metric_types = []
        self.cool_sys_dehumidification_type = None
        self.cool_sys_turndown_ratio = None

        # preheat system data elements
        self.preheat_sys_id = None
        self.preheat_sys_reporting_name = None
        self.preheat_sys_notes = None
        self.preheat_sys_type = None
        self.preheat_sys_phase = None
        self.preheat_sys_efficiency = None
        self.preheat_sys_capacity = None
        self.preheat_sys_peak_load = None

        # [supply, return, relief, exhaust] fan data elements
        self.fan_id = [None, None, None, None]
        self.fan_reporting_name = [None, None, None, None]
        self.fan_notes = [None, None, None, None]
        self.fan_design_airflow = [None, None, None, None]
        self.fan_is_airflow_sized_based_on_design_day = [None, None, None, None]
        self.fan_specification_method = [None, None, None, None]
        self.fan_design_electric_power = [None, None, None, None]
        self.fan_design_pressure_rise = [None, None, None, None]
        self.fan_motor_nameplate_power = [None, None, None, None]
        self.fan_shaft_power = [None, None, None, None]
        self.fan_total_efficiency = [None, None, None, None]
        self.fan_motor_efficiency = [None, None, None, None]
        self.fan_motor_heat_to_airflow_fraction = [None, None, None, None]
        self.fan_motor_heat_to_zone_fraction = [None, None, None, None]
        self.fan_motor_location_zone = [None, None, None, None]
        self.fan_status_type = [None, None, None, None]
        self.fan_output_validation_points = [[], [], [], []]

        # air economizer data elements
        self.air_econ_id = None
        self.air_econ_reporting_name = None
        self.air_econ_notes = None
        self.air_econ_type = None
        self.air_econ_high_limit_shutoff_temperature = None
        self.air_econ_is_integrated = None

        # air energy recovery data elements
        self.air_energy_recovery_id = None
        self.air_energy_recovery_reporting_name = None
        self.air_energy_recovery_notes = None
        self.air_energy_recovery_type = None
        self.air_energy_recovery_enthalpy_recovery_ratio = None
        self.air_energy_recovery_operation = None
        self.air_energy_recovery_sat_control = None
        self.air_energy_recovery_sensible_effectiveness = None
        self.air_energy_recovery_latent_effectiveness = None
        self.air_energy_recovery_outdoor_airflow = None
        self.air_energy_recovery_exhaust_airflow = None

        # terminal data elements
        self.terminals_id = [None]
        self.terminals_reporting_name = [None]
        self.terminals_notes = [None]
        self.terminals_type = [None]
        self.terminals_served_by_hvac_system = [None]
        self.terminals_heating_source = [None]
        self.terminals_heating_from_loop = [None]
        self.terminals_cooling_source = [None]
        self.terminals_cooling_from_loop = [None]
        self.terminals_fan = [{}]
        self.terminals_fan_configuration = [None]
        self.terminals_primary_airflow = [None]
        self.terminals_secondary_airflow = [None]
        self.terminals_max_heating_airflow = [None]
        self.terminals_supply_design_heat_t_setpoint = [None]
        self.terminals_supply_design_cool_t_setpoint = [None]
        self.terminals_temp_control = [None]
        self.terminals_minimum_airflow = [None]
        self.terminals_minimum_outdoor_airflow = [None]
        self.terminals_min_oa_multiplier_schedule = [None]
        self.terminals_heating_capacity = [None]
        self.terminals_cooling_capacity = [None]
        self.terminals_is_supply_ducted = [None]
        self.terminals_has_dcv = [None]
        self.terminals_is_fan_first_stage_heat = [None]

    def __repr__(self):
        return f"System(u_name='{self.u_name}')"

    def populate_data_elements(self):
        """Populate data elements from the keyword_value pairs returned from model_input_reader."""

        # self.get_output_data()

    def get_output_data(self, dll_path, doe2_data_path, project_path_name):
        """
        Get data from the simulation output.
        :param dll_path: (string) path to user's eQUEST D2Result.dll file included with installation files
        :param doe2_data_path: (binary string) path to DOE-2 data directory with NHRList.txt
        :param project_path_name: (binary string) path to project with project name NOT INCLUDING FILE EXTENSION
        :return: dictionary of system data elements
        """

        requests = self.get_output_requests()
        chunk_size = 12  # Max number of requests to process at a time
        results = {}  # To store the reassociated keys and values

        # Split requests into chunks of at most 12
        for chunk in _chunked_dict(requests, chunk_size):
            # Extract and combine values into a list of tuples for get_multiple_results
            values_list = list(chunk.values())

            # Call the function with the current chunk of values
            chunk_results = get_multiple_results(dll_path, doe2_data_path, project_path_name, values_list)

            # Reassociate returned values with their corresponding keys
            if len(chunk_results) == len(chunk):
                results.update(zip(chunk.keys(), chunk_results))
        return results

    def get_output_requests(self):
        """Get the output requests for the system dependent on various system component types."""
        requests = {
            # HVAC Systems - Design Parameters - General - Outside Air Ratio
            "Outside Air Ratio": (2201005, self.u_name.encode('utf-8'), b""),
            # HVAC Systems - Design Parameters - General - Cooling Capacity
            "Cooling Capacity": (2201006, self.u_name.encode('utf-8'), b""),
            # HVAC Systems - Design Parameters - General - Heating Capacity
            "Heating Capacity": (2201008, self.u_name.encode('utf-8'), b""),
            # HVAC Systems - Design Parameters - General - Cooling EIR
            "Cooling EIR": (2201009, self.u_name.encode('utf-8'), b""),
            # HVAC Systems - Design Parameters - General - Heating EIR
            "Heating EIR": (2201010, self.u_name.encode('utf-8'), b"")}

        if len(self.fan_system["supply_fans"]) > 0:
            # HVAC Systems - Design Parameters - Supply Fan - Airflow
            requests["Supply Fan - Airflow"] = (2201012, self.u_name.encode('utf-8'), b"")
            # HVAC Systems - Design Parameters - Supply Fan - Power
            requests["Supply Fan - Power"] = (2201014, self.u_name.encode('utf-8'), b"")
            # HVAC Systems - Design Parameters - Supply Fan - Total Static Pressure
            # 2201016
            # HVAC Systems - Design Parameters - Supply Fan - Overall Efficiency
            # 2201017
        if len(self.fan_system["return_fans"]) > 0:
            # HVAC Systems - Design Parameters - Return Fan - Airflow
            requests["Return Fan - Airflow"] = (2201023, self.u_name.encode('utf-8'), b"")
            # HVAC Systems - Design Parameters - Return Fan - Power
            # 2201025
            # HVAC Systems - Design Parameters - Return Fan - Total Static Pressure
            # 2201027
            # HVAC Systems - Design Parameters - Return Fan - Overall Efficiency
            # 2201028

        if self.cooling_system["type"] == "FLUID_LOOP":
            # Design Day data for Cooling - chilled water - SYSTEM - capacity, btu/hr
            requests["Design Day Cooling - chilled water - SYSTEM - capacity, btu/hr"] = (2203006, self.u_name.encode('utf-8'), b"")
            # Design data for Cooling - chilled water - SYSTEM - capacity, btu/hr
            requests["Design Cooling - chilled water - SYSTEM - capacity, btu/hr"] = (2203015, self.u_name.encode('utf-8'), b"")
            # Rated data for Cooling - chilled water - SYSTEM - capacity, btu/hr
            # requests["Rated Cooling - chilled water - SYSTEM - capacity, btu/hr"] = (2203026, self.u_name.encode('utf-8'), b"")

        match self.preheat_sys_type:
            case "FLUID_LOOP":
                pass
                # Design data for Preheat - hot water - SYSTEM - capacity, btu/hr IS NOT AVAILABLE. PARSE SIM FILE?
                # # Design Day data for Preheat - hot water - SYSTEM - capacity, btu/hr
                # requests["Design Day Preheat - hot water - SYSTEM - capacity, btu/hr"] = (2203269, self.u_name.encode('utf-8'), b"")
            case "ELECTRIC_RESISTANCE":
                pass
                # Design data for Preheat - electric - SYSTEM - capacity, btu/hr IS NOT AVAILABLE. PARSE SIM FILE?
                # # Design Day data for Preheat - electric - SYSTEM - capacity, btu/hr
                # requests["Design Day Preheat - electric - SYSTEM - capacity, btu/hr"] = (2203346, self.u_name.encode('utf-8'), b"")
            case "FURNACE":
                # # Design Day data for Preheat - furnace - SYSTEM - capacity, btu/hr
                # requests["Design Day Preheat - furnace - SYSTEM - capacity, btu/hr"] = (2203306, self.u_name.encode('utf-8'), b"")
                # Design data for Preheat - furnace - SYSTEM - capacity, btu/hr
                requests["Design Preheat - furnace - SYSTEM - capacity, btu/hr"] = (2203311, self.u_name.encode('utf-8'), b"")
            # case "HEAT_PUMP":  # THIS IS COMMENTED OUT BECAUSE EQUEST DOES NOT LET YOU SELECT HEAT PUMP AS A PREHEAT SOURCE
            #     # Design Day data for Preheat - heat pump air cooled - SYSTEM - capacity, btu/hr
            #     requests["Design Day Preheat - heat pump air cooled - SYSTEM - capacity, btu/hr"] = (2203387, self.u_name.encode('utf-8'), b"")
            #     # Design data for Preheat - heat pump air cooled - SYSTEM - capacity, btu/hr
            #     requests["Design Preheat - heat pump air cooled - SYSTEM - capacity, btu/hr"] = (2203393, self.u_name.encode('utf-8'), b"")
            #     # Rated data for Preheat - heat pump air cooled - SYSTEM - capacity, btu/hr
            #     requests["Rated Preheat - heat pump air cooled - SYSTEM - capacity, btu/hr"] = (2203399, self.u_name.encode('utf-8'), b"")

        if self.heat_sys_type == "FLUID_LOOP":
            # Design Day data for Heating - hot water - SYSTEM - capacity, btu/hr
            requests["Design Day Heating - hot water - SYSTEM - capacity, btu/hr"] = (2203258, self.u_name.encode('utf-8'), b"")

            # HVAC Systems - Design Parameters - Zone Design Data - General - Supply Airflow
            # 2201045
            # HVAC Systems - Design Parameters - Zone Design Data - General - Exhaust Airflow
            # 2201046
            # HVAC Systems - Design Parameters - Zone Design Data - General - Zone Fan Power
            # 2201047
            # HVAC Systems - Design Parameters - Zone Design Data - General - Minimum Airflow Ratio
            # 2201048
            # HVAC Systems - Design Parameters - Zone Design Data - General - Outside Airflow
            # 2201049
            # HVAC Systems - Design Parameters - Zone Design Data - General - Cooling Capacity
            # 2201050
            # HVAC Systems - Design Parameters - Zone Design Data - General - Sensible Heat Ratio
            # 2201051
            # HVAC Systems - Design Parameters - Zone Design Data - General - Heating Capacity
            # 2201053
            # HVAC Systems - Design Parameters - Zone Design Data - General - Baseboards
            # 2201063

        return requests

    def populate_data_group(self):
        """
        Populate schema structure for system object.
        System configurations that typically are at the zone and include a compressor (such as packaged terminal air
        conditioning, packaged terminal heat pumps, window air conditioning units, and water loop heat pumps) should be
        reported in the schema using HeatingSystem and CoolingSystem. Systems that include gas or electric furnaces
        should be reported in the schema using HeatingSystem. System configurations that are at the zone and only
        include fans and coils (such as four-pipe fan coil, two-pipe fan coil, radiant systems, baseboards, and chilled
        beams) should be reported in the schema using Terminal with the chilled water and hot water systems described
        in the cooling_source and heating_source data elements (and any other relevant Terminal Data elements).
        Evaporative cooling systems should be described in CoolingSystem. Passive diffusers with no coil or fan should
        be described in Terminal. One FanSystem for each HeatingVentilatingAirConditioningSystem so if a direct outdoor
        air system is used a second Zone Terminal should be specified with a separate
        HeatingVentilatingAirConditioningSystem.
        """

        cool_source = self.keyword_value_pairs.get("COOL-SOURCE")
        cool_type = self.cool_type_map.get(cool_source)
        heat_type = self.heat_type_map.get(self.keyword_value_pairs.get("HEAT-SOURCE"))

        # Update the cooling type map according to the COOL-SOURCE keyword (only used for PIU and DOAS)
        self.system_cooling_type_map.update({
            "PIU": cool_type,
            "DOAS": cool_type,
        })

        if self.keyword_value_pairs.get("TYPE") == "SUM":
            self.omit = True
            return

        self.system_data_structure["id"] = self.u_name

        terminal_system_conditions = self.keyword_value_pairs.get("TYPE") in ["FC", "IU"] and heat_type == "FLUID_LOOP"
        if terminal_system_conditions:
            self.populate_terminal_system()
        if not terminal_system_conditions:
            self.populate_fan_system()
            self.system_data_structure["fan_system"] = self.fan_system
            self.populate_heating_system()
            self.system_data_structure["heating_system"] = self.heating_system
            self.populate_cooling_system()
            self.system_data_structure["cooling_system"] = self.cooling_system
            self.populate_preheat_system()
            self.system_data_structure["preheat_system"] = self.preheat_system
        self.populate_data_elements()

    def insert_to_rpd(self, building_segment):
        """Insert system data structure into the rpd data structure."""
        if self.omit:
            return
        building_segment.hvac_systems.append(self.system_data_structure)

    def populate_fan_system(self):
        self.fan_sys_fan_control = self.supply_fan_map.get(self.keyword_value_pairs.get("TYPE"))
        self.fan_sys_operation_during_occ = self.unocc_fan_operation_map.get(self.keyword_value_pairs.get("NIGHT-CYCLE-CTRL"))
        self.fan_sys_dcv_control = self.dcv_map.get(self.keyword_value_pairs.get("MIN-OA-METHOD"))

    def populate_heating_system(self):
        self.heat_sys_type = self.heat_type_map.get(self.keyword_value_pairs.get("HEAT-SOURCE"))

    def populate_cooling_system(self):
        self.cool_sys_type = self.system_cooling_type_map.get(self.keyword_value_pairs.get("TYPE"))

    def populate_preheat_system(self):
        self.preheat_sys_type = self.heat_type_map.get(self.keyword_value_pairs.get("PREHEAT-SOURCE"))

    def populate_fans(self):
        pass

    def populate_air_economizer(self):
        self.air_econ_type = self.economizer_map.get(self.keyword_value_pairs.get("OA-CONTROL"))

    def populate_air_energy_recovery(self):
        recover_exhaust = self.keyword_value_pairs.get("RECOVER-EXHAUST")
        recovery_type = self.recovery_type_map.get(self.keyword_value_pairs.get("ERV-RECOVER-TYPE"))
        self.air_energy_recovery_map.update({
            "RELIEF-ONLY": recovery_type,
            "EXHAUST-ONLY": recovery_type,
            "RELIEF+EXHAUST": recovery_type,
            "YES": recovery_type,
        })

        self.air_energy_recovery_type = self.air_energy_recovery_map.get(recover_exhaust)
        self.air_energy_recovery_operation = self.er_operation_map.get(self.keyword_value_pairs.get("ERV-RUN-CTRL"))
        self.air_energy_recovery_sat_control = self.er_sat_control_map.get(self.keyword_value_pairs.get("ERV-TEMP-CTRL"))

    def populate_system_terminals(self):
        pass

    def populate_terminal_system(self):
        pass


def _chunked_dict(d, n):
    """Yield successive n-sized chunks from dictionary d."""
    it = iter(d)
    for i in range(0, len(d), n):
        yield {k: d[k] for k in islice(it, n)}
