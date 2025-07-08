class RulesetProjectDescription:
    """
    This class is used to represent the RulesetProjectDescription object in the 229 schema. It also stores additional project-level data.
    """

    def __init__(self, project_name):
        self.project_name = project_name
        self.rpd_data_structure = {}

        # data elements with children
        self.metadata = {}
        self.output = {}
        self.ruleset_model_descriptions = []

        # data elements with no children
        self.reporting_name = None
        self.notes = None
        self.compliance_path = None
        self.output_format_type = "OUTPUT_SCHEMA_ASHRAE901_2019"

    def populate_data_elements(self):
        output = Output(self)
        output.populate_data_elements()
        output.populate_data_group()
        output.insert_to_rpd()

        metadata = Metadata(self)
        metadata.populate_data_group()
        metadata.insert_to_rpd()

    def populate_data_group(self):
        """
        Populate the RPD data group (only data elements directly under the RPD Data Group)
        """
        self.rpd_data_structure = {
            "id": f"{self.project_name}",
            "metadata": self.metadata,
            "output": self.output,
            "ruleset_model_descriptions": self.ruleset_model_descriptions,
        }

        no_children_attributes = [
            "reporting_name",
            "notes",
            "compliance_path",
            "output_format_type",
        ]

        # Iterate over the no_children_attributes list and populate if the value is not None
        for attr in no_children_attributes:
            value = getattr(self, attr, None)
            if value is not None:
                self.rpd_data_structure[attr] = value


class Output:
    """Class to represent an output in the RPD data structure."""

    def __init__(self, rpd):
        self.rpd = rpd

        self.data_structure = {}

        # Initialize attributes
        self.output_id = "Output2019ASHRAE901"
        self.reporting_name = None
        self.notes = None
        self.performance_cost_index = None
        self.baseline_building_unregulated_energy_cost = None
        self.baseline_building_regulated_energy_cost = None
        self.baseline_building_performance_energy_cost = None
        self.total_area_weighted_building_performance_factor = None
        self.performance_cost_index_target = None
        self.total_proposed_building_energy_cost_including_renewable_energy = None
        self.total_proposed_building_energy_cost_excluding_renewable_energy = None
        self.percent_renewable_energy_savings = None

    def __repr__(self):
        return f"Output()"

    def populate_data_elements(self):
        pass

    def populate_data_group(self):
        self.data_structure["id"] = self.output_id

        no_children_attributes = [
            "reporting_name",
            "notes",
            "performance_cost_index",
            "baseline_building_unregulated_energy_cost",
            "baseline_building_regulated_energy_cost",
            "baseline_building_performance_energy_cost",
            "total_area_weighted_building_performance_factor",
            "performance_cost_index_target",
            "total_proposed_building_energy_cost_including_renewable_energy",
            "total_proposed_building_energy_cost_excluding_renewable_energy",
            "percent_renewable_energy_savings",
        ]

        # Iterate over the no_children_attributes list and populate if the value is not None
        for attr in no_children_attributes:
            value = getattr(self, attr, None)
            if value is not None:
                self.data_structure[attr] = value

    def insert_to_rpd(self):
        """Insert output object into the rpd data structure."""
        self.rpd.output = self.data_structure


class Metadata:
    """Class to represent metadata group in the RPD data structure."""

    def __init__(self, rpd):
        self.rpd = rpd

        self.data_structure = {}

        # Initialize attributes
        self.schema_author = None
        self.schema_name = None
        self.schema_version = None
        self.schema_url = None
        self.author = None
        self.description = None
        self.time_of_creation = None
        self.version = None
        self.source = None
        self.disclaimer = None
        self.notes = None

    def __repr__(self):
        return f"Metadata()"

    def populate_data_group(self):
        no_children_attributes = [
            "schema_author",
            "schema_name",
            "schema_version",
            "schema_url",
            "author",
            "description",
            "time_of_creation",
            "version",
            "source",
            "disclaimer",
            "notes",
        ]

        # Iterate over the no_children_attributes list and populate if the value is not None
        for attr in no_children_attributes:
            value = getattr(self, attr, None)
            if value is not None:
                self.data_structure[attr] = value

    def insert_to_rpd(self):
        """Insert metadata object into the rpd data structure."""
        self.rpd.metadata = self.data_structure
