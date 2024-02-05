from rpd_generator.bdl_structure.child_node import ChildNode


class Zone(ChildNode):
    """Zone object in the tree."""

    bdl_command = "ZONE"

    def __init__(self, u_name, parent):
        super().__init__(u_name, parent)

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
        self.heating_thermostat_setpoint_schedulue = None
        self.minimum_humidity_setpoint_schedule = None
        self.maximum_humidity_setpoint_schedule = None
        self.served_by_service_water_heating_system = None
        self.transfer_airflow_rate = None
        self.transfer_airflow_source_zone = None
        self.zonal_exhaust_flow = None
        self.exhaust_airflow_rate_multiplier_schedule = None
        self.makeup_airflow_rate = None
        self.non_mechanical_cooling_fan_power = None
        self.non_mechanical_cooling_fan_airflow = None
        self.air_distribution_effectiveness = None
        self.aggregation_factor = None

    def __repr__(self):
        return f"Zone(u_name='{self.u_name}', parent={self.parent.__class__.__name__}('{self.parent.u_name}'))"

    def populate_data_group(self):
        """Populate schema structure for zone object."""
        self.zone_data_structure[self.u_name] = {
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
            "volume"
            "conditioning_type"
            "design_thermostat_cooling_setpoint"
            "thermostat_cooling_setpoint_schedule"
            "design_thermostat_heating_setpoint"
            "heating_thermostat_setpoint_schedulue"
            "minimum_humidity_setpoint_schedule"
            "maximum_humidity_setpoint_schedule"
            "served_by_service_water_heating_system"
            "transfer_airflow_rate"
            "transfer_airflow_source_zone"
            "zonal_exhaust_flow"
            "exhaust_airflow_rate_multiplier_schedule"
            "makeup_airflow_rate"
            "non_mechanical_cooling_fan_power"
            "non_mechanical_cooling_fan_airflow"
            "air_distribution_effectiveness"
            "aggregation_factor"
        ]

        # Iterate over the no_children_attributes list and populate if the value is not None
        for attr in no_children_attributes:
            value = getattr(self, attr, None)
            if value is not None:
                self.zone_data_structure[self.u_name][attr] = value

    def insert_to_rpd(self, building_segment):
        """Insert zone object into the rpd data structure."""
        building_segment.zones.append(self.zone_data_structure)
