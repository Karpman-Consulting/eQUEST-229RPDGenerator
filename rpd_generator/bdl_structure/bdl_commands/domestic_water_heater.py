from rpd_generator.bdl_structure.base_node import BaseNode


class DomesticWaterHeater(BaseNode):
    """DomesticWaterHeater object in the tree."""

    bdl_command = "DW-HEATER"

    fuel_type_map = {
        "ELECTRICITY": "ELECTRICITY",
        "NATURAL-GAS": "NATURAL_GAS",
        "LPG": "PROPANE",
        "FUEL-OIL": "FUEL_OIL",
        "DIESEL-OIL": "OTHER",
        "COAL": "OTHER",
        "METHANOL": "OTHER",
        "OTHER-FUEL": "OTHER",
    }

    heater_type_map = {
        "GAS": "CONVENTIONAL",
        "ELEC": "CONVENTIONAL",
        "HEAT-PUMP": "HEAT_PUMP_PACKAGED",
    }

    location_map = {
        "OUTDOOR": "OUTSIDE",
        "ZONE": "IN_ZONE",
    }

    def __init__(self, u_name, rmd):
        super().__init__(u_name, rmd)

        self.swh_equipment_data_structure = {}

        # data elements with children
        self.output_validation_points = []
        self.compressor_capacity_validation_points = []
        self.compressor_power_validation_points = []
        self.tank = {}
        self.solar_thermal_systems = []

        # data elements with no children
        self.heater_fuel_type = None
        self.distribution_system = None
        self.energy_factor = None
        self.thermal_efficiency = None
        self.standby_loss_fraction = None
        self.uniform_energy_factor = None
        self.first_hour_rating = None
        self.input_power = None
        self.rated_capacity = None
        self.minimum_capacity = None
        self.recovery_efficiency = None
        self.setpoint_temperature = None
        self.compressor_location = None
        self.compressor_zone = None
        self.compressor_heat_rejection_source = None
        self.compressor_heat_rejection_zone = None
        self.draft_fan_power = None
        self.has_electrical_ignition = None
        self.heater_type = None
        self.status_type = None
        self.hot_water_loop = None

        # Tank data elements
        self.storage_capacity = None
        self.type = None
        self.height = None
        self.interior_insulation = None
        self.exterior_insulation = None
        self.location = None
        self.location_zone = None

    def __repr__(self):
        return f"DomesticWaterHeater(u_name='{self.u_name}')"

    def populate_data_elements(self):
        """Populate data elements for domestic water heater object."""

        fuel_meter_ref = self.keyword_value_pairs.get("FUEL-METER")
        fuel_meter = self.rmd.bdl_obj_instances.get(fuel_meter_ref)
        # If the fuel meter is not found, then it must be a MasterMeter.
        if fuel_meter is None:
            # This assumes the Master Fuel Meter is Natural Gas
            self.heater_fuel_type = "NATURAL_GAS"
        else:
            fuel_meter_type = fuel_meter.keyword_value_pairs.get("TYPE")
            self.heater_fuel_type = self.fuel_type_map.get(fuel_meter_type)

        self.distribution_system = self.keyword_value_pairs.get("DHW-LOOP")

        loop = self.rmd.bdl_obj_instances.get(self.distribution_system)
        loop_stpt = None
        if loop is not None:
            loop_stpt = loop.design_supply_temperature[1]
        tank_stpt = self.keyword_value_pairs.get("AQUASTAT-SETPT-T")
        if tank_stpt is not None and loop_stpt is not None:
            self.setpoint_temperature = max(loop_stpt, tank_stpt)
        elif tank_stpt is None:
            self.setpoint_temperature = loop_stpt

        self.heater_type = self.heater_type_map.get(
            self.keyword_value_pairs.get("TYPE")
        )

        self.storage_capacity = self.try_float(
            self.keyword_value_pairs.get("TANK-VOLUME")
        )

        self.location = self.location_map.get(self.keyword_value_pairs.get("LOCATION"))

        self.location_zone = self.keyword_value_pairs.get("ZONE-NAME")

    def get_output_requests(self):
        """Get the output requests for the domestic water heater object."""
        pass
        # DW Heaters - Design Parameters - Capacity
        # 2321003
        # DW Heaters - Design Parameters - Flow
        # 2321004
        # DW Heaters - Design Parameters - Electric Input Ratio
        # 2321005
        # DW Heaters - Design Parameters - Fuel Input Ratio
        # 2321006
        # DW Heaters - Design Parameters - Auxiliary Power
        # 2321007
        # DW Heaters - Design Parameters - Tank Volume
        # 2321008
        # DW Heaters - Design Parameters - Tank Loss Coefficient
        # 2321009

    def populate_data_group(self):
        """Populate schema structure for domestic water heater object."""

        self.swh_equipment_data_structure = {
            "id": self.u_name,
            "output_validation_points": self.output_validation_points,
            "tank": self.tank,
            "solar_thermal_systems": self.solar_thermal_systems,
            "compressor_capacity_validation_points": self.compressor_capacity_validation_points,
            "compressor_power_validation_points": self.compressor_power_validation_points,
        }

        if self.storage_capacity is not None and self.storage_capacity > 0:
            self.tank["id"] = self.u_name + " Tank"
            tank_data_elements = [
                "storage_capacity",
                "type",
                "height",
                "interior_insulation",
                "exterior_insulation",
                "location",
                "location_zone",
            ]

            for attr in tank_data_elements:
                value = getattr(self, attr, None)
                if value is not None:
                    self.tank[attr] = value

        no_children_attributes = [
            "reporting_name",
            "notes",
            "heater_fuel_type",
            "distribution_system",
            "energy_factor",
            "thermal_efficiency",
            "standby_loss_fraction",
            "uniform_energy_factor",
            "first_hour_rating",
            "input_power",
            "rated_capacity",
            "minimum_capacity",
            "recovery_efficiency",
            "setpoint_temperature",
            "compressor_location",
            "compressor_zone",
            "compressor_heat_rejection_source",
            "compressor_heat_rejection_zone",
            "draft_fan_power",
            "has_electrical_ignition",
            "heater_type",
            "status_type",
        ]

        # Iterate over the no_children_attributes list and populate if the value is not None
        for attr in no_children_attributes:
            value = getattr(self, attr, None)
            if value is not None:
                self.swh_equipment_data_structure[attr] = value

    def insert_to_rpd(self, rmd):
        """Insert window object into the rpd data structure."""
        rmd.service_water_heating_equipment.append(self.swh_equipment_data_structure)
