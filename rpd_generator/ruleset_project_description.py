from rpd_generator.doe2_file_readers import model_input_reader

OUTPUT_SCHEMA_ASHRAE901_2019 = "OUTPUT_SCHEMA_ASHRAE901_2019"


class RulesetProjectDescription:
    """
    This class is used to store project-level data, including the main rpd_data_structure that is output to json.
    """

    # BDL Command Dictionary maps BDL commands to their corresponding class in the bdl_commands package
    bdl_command_dict = model_input_reader.ModelInputReader.bdl_command_dict

    def __init__(self):

        self.rpd_data_structure = {}

        # data elements with children
        self.ruleset_model_descriptions = []
        self.calendar = {
            "is_leap_year": False,
        }
        self.weather = {}
        self.ground_temperature_schedule = None
        self.file_name = None
        self.data_source_type = None
        self.climate_zone = None
        self.cooling_design_day_type = None
        self.heating_design_day_type = None

        # data elements with no children
        self.reporting_name = None
        self.notes = None
        self.data_timestamp = None
        self.data_version = None
        self.compliance_path = None
        self.output_format_type = OUTPUT_SCHEMA_ASHRAE901_2019

    def populate_data_elements(self):
        """Populate the data elements in the RPD data group."""

    def populate_data_group(self):
        """
        Populate the RPD data group (only data elements directly under the RPD Data Group)
        """
        self.rpd_data_structure = {
            "id": "ASHRAE 229",
            "ruleset_model_descriptions": self.ruleset_model_descriptions,
            "calendar": self.calendar,
            "weather": self.weather,
        }

        no_children_attributes = [
            "reporting_name",
            "notes",
            "data_timestamp",
            "data_version",
            "compliance_path",
        ]

        # Iterate over the no_children_attributes list and populate if the value is not None
        for attr in no_children_attributes:
            value = getattr(self, attr, None)
            if value is not None:
                self.rpd_data_structure["ASHRAE 229"][attr] = value
