from rpd_generator.bdl_structure.base_node import BaseNode


class DomesticWaterHeater(BaseNode):
    """DomesticWaterHeater object in the tree."""

    bdl_command = "DW-HEATER"

    def __init__(self, u_name):
        super().__init__(u_name)

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

    def __repr__(self):
        return f"DomesticWaterHeater(u_name='{self.u_name}')"

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

        no_children_attributes = [
            "reporting_name",
            "notes",
            "classification",
            "subclassification",
            "is_operable",
            "framing_type",
            "glazed_area",
            "opaque_area",
            "u_factor",
            "dynamic_glazing_type",
            "solar_heat_gain_coefficient",
            "maximum_solar_heat_gain_coefficient",
            "has_shading_overhang",
            "has_shading_sidefins",
            "has_manual_interior_shades",
            "solar_transmittance_multiplier_summer",
            "solar_transmittance_multiplier_winter",
            "has_automatic_shades",
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
