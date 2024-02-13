from rpd_generator.bdl_structure.parent_node import ParentNode


class System(ParentNode):
    """System object in the tree."""

    bdl_command = "SYSTEM"

    def __init__(self, u_name):
        super().__init__(u_name)

        self.system_data_structure = {}

        # data elements with children
        self.fan_system = {}
        self.heating_system = {}
        self.cooling_system = {}
        self.preheat_system = {}
        self.air_economizer = {}
        self.air_energy_recovery = {}

        # data elements with no children
        self.status_type = None

    def __repr__(self):
        return f"System(u_name='{self.u_name}')"

    def populate_data_elements(self):
        """Populate data elements from the keyword_value pairs returned from model_input_reader."""
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
            "CYCLING": "MULTISPEED",
            "INLET": "INLET_VANE",
            "DISCHARGE": "DISCHARGE_DAMPER",
            "FAN-EIR-FPLR": "VARIABLE_SPEED_DRIVE",
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
            "PIU": cool_type_map.get(self.keyword_value_pairs.get("COOL-SOURCE")),
            "FC": "FLUID_LOOP",
            "IU": "FLUID_LOOP",
            "UVT": "NONE",
            "UHT": "NONE",
            "RESYS2": "DIRECT_EXPANSION",
            "CBVAV": "FLUID_LOOP",
            "SUM": "NONE",
            "DOAS": cool_type_map.get(self.keyword_value_pairs.get("COOL-SOURCE")),
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
            "RELIEF-ONLY": recovery_type_map.get(
                self.keyword_value_pairs.get("RECOVER-EXHAUST")
            ),
            "EXHAUST-ONLY": recovery_type_map.get(
                self.keyword_value_pairs.get("RECOVER-EXHAUST")
            ),
            "RELIEF+EXHAUST": recovery_type_map.get(
                self.keyword_value_pairs.get("RECOVER-EXHAUST")
            ),
            "YES": recovery_type_map.get(
                self.keyword_value_pairs.get("RECOVER-EXHAUST")
            ),
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

        if self.keyword_value_pairs.get("HEAT-SOURCE") is not None:
            self.heating_system["type"] = heat_type_map[
                self.keyword_value_pairs.get("HEAT-SOURCE")
            ]
        if self.keyword_value_pairs.get("FAN-CONTROL") is not None:
            self.fan_system["fan_control"] = supply_fan_map[
                self.keyword_value_pairs.get("FAN-CONTROL")
            ]
        self.cooling_system["type"] = system_cooling_type_map[
            self.keyword_value_pairs.get("TYPE")
        ]
        if self.keyword_value_pairs.get("PREHEAT-SOURCE") is not None:
            self.preheat_system["type"] = heat_type_map[
                self.keyword_value_pairs.get("PREHEAT-SOURCE")
            ]
        if self.keyword_value_pairs.get("OA-CONTROL") is not None:
            self.air_economizer["type"] = economizer_map[
                self.keyword_value_pairs.get("OA-CONTROL")
            ]
        if self.keyword_value_pairs.get("RECOVER-EXHAUST") is not None:
            self.air_energy_recovery["type"] = air_energy_recovery_map[
                self.keyword_value_pairs.get("RECOVER-EXHAUST")
            ]
        if self.keyword_value_pairs.get("ERV-RUN-CTRL") is not None:
            self.air_energy_recovery["energy_recovery_operation"] = er_operation_map[
                self.keyword_value_pairs.get("ERV-RUN-CTRL")
            ]
        if self.keyword_value_pairs.get("ERV-TEMP-CTRL") is not None:
            self.air_energy_recovery["energy_recovery_supply_air_temperature_control"] = er_sat_control_map[
                self.keyword_value_pairs.get("ERV-TEMP-CTRL")
            ]
        if self.keyword_value_pairs.get("MIN-OA-METHOD") is not None:
            self.fan_system["demand_control_ventilation_control"] = dcv_map[
                self.keyword_value_pairs.get("MIN-OA-METHOD")
            ]

    def populate_data_group(self):
        """Populate schema structure for system object."""

        self.system_data_structure = {
            "id": self.u_name,
            "fan_system": self.fan_system,
            "heating_system": self.heating_system,
            "cooling_system": self.cooling_system,
            "preheat_system": self.preheat_system,
            "air_economizer": self.air_economizer,
            "air_energy_recovery": self.air_energy_recovery,
        }

        self.populate_data_elements()

        no_children_attributes = [
            "status_type",
        ]

        # Iterate over the no_children_attributes list and populate if the value is not None
        for attr in no_children_attributes:
            value = getattr(self, attr, None)
            if value is not None:
                self.system_data_structure[attr] = value

    def insert_to_rpd(self, building_segment):
        """Insert zone object into the rpd data structure."""
        building_segment.hvac_systems.append(self.system_data_structure)
