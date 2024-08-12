class RulesetModelDescription:
    """
    This class is used to represent the RulesetModelDescription object in the 229 schema.
    """

    def __init__(self, obj_id):
        self.file_path = None
        self.doe2_version = None
        self.doe2_data_path = None

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
