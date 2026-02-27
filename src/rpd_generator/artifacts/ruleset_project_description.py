from time import strftime, gmtime

from rpd_generator.utilities.ashrae9012019.baseline_systems.baseline_system_util import (
    HVAC_SYS,
)
from rpd_generator.utilities.ashrae9012019.get_zone_target_baseline_system import (
    get_zone_target_baseline_system,
)
from rpd_generator.utilities.jsonpath_utils import find_all


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
        print("Populating RPD data group...")
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

    def specify_supply_ducting(self):
        """Determine the expected system types for the baseline RMDs, then populate is_supply_ducted accordingly."""
        rpd = self.rpd_data_structure
        rmd_p = next(
            (
                rmd
                for rmd in rpd.get("ruleset_model_descriptions", [])
                if rmd.get("type", "") == "PROPOSED"
            ),
            None,
        )
        if not rmd_p:
            print(
                "Could not specify supply ducting in baseline models because proposed RMD was not found in the RPD data structure."
            )
            return
        for rmd_b in rpd.get("ruleset_model_descriptions", []):
            if "BASELINE" in rmd_b.get("type", ""):
                climate_zone = rmd_b.get("weather", {}).get("climate_zone")

                if not climate_zone:
                    raise ValueError(
                        "You must set a valid ASHRAE 90.1 climate zone "
                        "(e.g., '3A', '5B', '2C')."
                    )

                zone_target_baseline_systems = get_zone_target_baseline_system(
                    rmd_b, rmd_p, climate_zone
                )
                zones = find_all("$.buildings[*].building_segments[*].zones[*]", rmd_b)
                for zone in zones:
                    if zone["id"] not in zone_target_baseline_systems:
                        continue
                    expected_system_type = zone_target_baseline_systems[zone["id"]][
                        "expected_system_type"
                    ]
                    if expected_system_type in [
                        HVAC_SYS.SYS_3,
                        HVAC_SYS.SYS_3A,
                        HVAC_SYS.SYS_3B,
                        HVAC_SYS.SYS_3C,
                        HVAC_SYS.SYS_4,
                        HVAC_SYS.SYS_5,
                        HVAC_SYS.SYS_5B,
                        HVAC_SYS.SYS_6,
                        HVAC_SYS.SYS_6B,
                        HVAC_SYS.SYS_7,
                        HVAC_SYS.SYS_7A,
                        HVAC_SYS.SYS_7B,
                        HVAC_SYS.SYS_7C,
                        HVAC_SYS.SYS_8,
                        HVAC_SYS.SYS_8A,
                        HVAC_SYS.SYS_8B,
                        HVAC_SYS.SYS_8C,
                        HVAC_SYS.SYS_12,
                        HVAC_SYS.SYS_12A,
                        HVAC_SYS.SYS_12B,
                        HVAC_SYS.SYS_13,
                        HVAC_SYS.SYS_13A,
                    ]:
                        for terminal in find_all("$.terminals[*]", zone):
                            terminal["is_supply_ducted"] = True


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
        self.schema_author = "ASHRAE SPC 229 Schema Working Group"
        self.schema_name = "Ruleset Evaluation Schema"
        self.schema_version = "0.1.7"
        self.schema_url = "https://github.com/open229/ruleset-model-description-schema"
        self.author = "Jackson Jarboe, Karpman Consulting LLC"
        self.description = "DOE2.3 Ruleset Project Description (RPD)"
        self.time_of_creation = strftime("%Y-%m-%dT%H:%MZ", gmtime())
        self.version = "1.1.1"
        self.source = "DOE-2.3 Energy Model .INP, .LRP, .SRP, .ERP, .NHR files"
        self.disclaimer = """
        Acknowledgment: This material is based upon work supported by the U.S. Department of Energy’s Office of Energy Efficiency and Renewable Energy (EERE) under the Building Technologies Office - DE-FOA-0002813 - Bipartisan Infrastructure Law Resilient and Efficient Codes Implementation.
        Award Number: DE-EE0010949
        Abridged Disclaimer: The views expressed herein do not necessarily represent the view of the U.S. Department of Energy or the United States Government.
        """
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
