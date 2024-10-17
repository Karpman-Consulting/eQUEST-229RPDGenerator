class RulesetModelDescription:
    """
    This class is used to represent the RulesetModelDescription object in the 229 schema. It also stores additional model-level data.
    """

    def __init__(self, obj_id):
        self.file_path = None
        self.doe2_version = None
        self.doe2_data_path = None

        self.building_azimuth = None
        self.master_meters = None
        # False by default, will set to True if a FIXED-SHADE object is found
        self.has_site_shading = False
        self.system_names = []
        self.zone_names = []
        self.circulation_loop_names = []
        self.boiler_names = []
        self.chiller_names = []
        self.heat_rejection_names = []
        self.ground_loop_hx_names = []
        self.steam_meter_names = []
        self.equip_ctrl_names = []

        # store BDL objects for the model associated with the RMD
        self.bdl_obj_instances = {}
        # store space names mapped to their zone objects for quick access
        self.space_map = {}

        self.rmd_data_structure = {}

        # data elements with children
        self.transformers = []
        self.buildings = []
        self.schedules = []
        self.fluid_loops = []
        self.service_water_heating_distribution_systems = []
        self.service_water_heating_equipment = []
        self.pumps = []
        self.boilers = []
        self.chillers = []
        self.heat_rejections = []
        self.external_fluid_sources = []
        self.output = {}

        # data elements with no children
        self.obj_id = obj_id
        self.reporting_name = None
        self.notes = None
        self.type = None
        self.is_measured_infiltration_based_on_test = None

        # output data elements
        self.output_id = None
        self.output_reporting_name = None
        self.output_notes = None
        self.output_instance = {}
        self.output_performance_cost_index = None
        self.output_baseline_building_unregulated_energy_cost = None
        self.output_baseline_building_regulated_energy_cost = None
        self.output_baseline_building_performance_energy_cost = None
        self.output_total_area_weighted_building_performance_factor = None
        self.output_performance_cost_index_target = None
        self.output_total_proposed_building_energy_cost_including_renewable_energy = (
            None
        )
        self.output_total_proposed_building_energy_cost_excluding_renewable_energy = (
            None
        )
        self.output_percent_renewable_energy_savings = None

        # output instance data elements
        self.output_instance_id = None
        self.output_instance_reporting_name = None
        self.output_instance_notes = None
        self.output_instance_ruleset_model_type = None
        self.output_instance_rotation_angle = None
        self.output_instance_unmet_load_hours = None
        self.output_instance_unmet_load_hours_heating = None
        self.output_instance_unmet_occupied_load_hours_heating = None
        self.output_instance_unmet_load_hours_cooling = None
        self.output_instance_unmet_occupied_load_hours_cooling = None
        self.output_instance_annual_source_results = None
        self.output_instance_building_peak_cooling_load = None
        self.output_instance_annual_end_use_results = None

    def populate_data_group(self):
        """Populate the RMD data structure."""
        self.rmd_data_structure = {
            "id": self.obj_id,
            "buildings": self.buildings,
            "schedules": self.schedules,
            "fluid_loops": self.fluid_loops,
            "service_water_heating_distribution_systems": self.service_water_heating_distribution_systems,
            "service_water_heating_equipment": self.service_water_heating_equipment,
            "pumps": self.pumps,
            "boilers": self.boilers,
            "chillers": self.chillers,
            "heat_rejections": self.heat_rejections,
            "external_fluid_sources": self.external_fluid_sources,
            "output": self.output,
        }

    def insert_to_rpd(self, rpd):
        """Insert RMD object into the RPD data structure."""
        rpd.ruleset_model_descriptions.append(self.rmd_data_structure)
