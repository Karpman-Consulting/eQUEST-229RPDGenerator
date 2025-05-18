import atexit
import tempfile

import customtkinter as ctk
from pathlib import Path

from rpd_generator import main as rpd_generator
from rpd_generator.doe2_file_readers.model_input_reader import ModelInputReader
from rpd_generator.config import Config
from rpd_generator.schema.schema_enums import SchemaEnums
from rpd_generator.bdl_structure.bdl_enumerations.bdl_enums import BDLEnums
from rpd_generator.bdl_structure.bdl_commands.space import BDL_SpaceKeywords
from rpd_generator.bdl_structure.bdl_commands.zone import BDL_ZoneKeywords

BDL_ZoneTypeOptions = BDLEnums.bdl_enums["ZoneTypeOptions"]
BDL_LightingSpecMethodOptions = BDLEnums.bdl_enums["LightingSpecMethodOptions"]
CommonRulesetModelOptions = SchemaEnums.schema_enums["CommonRulesetModelOptions"]
ASHRAE9012019ModelOptions = SchemaEnums.schema_enums["RulesetModelOptions2019ASHRAE901"]


class MainAppData:

    def __init__(self):
        self.processing_dir = tempfile.TemporaryDirectory()
        atexit.register(self.processing_dir.cleanup)

        self.bdl_reader = ModelInputReader()
        self.rpd = None

        # Config data
        self.installation_path = ctk.StringVar()
        self.user_lib_path = ctk.StringVar()
        self.files_verified = False

        # Project data
        self.project_name = ctk.StringVar()
        self.selected_ruleset = ctk.StringVar()
        self.selected_ruleset.set("ASHRAE 90.1-2019 PRM")
        self.proposed_reflects_design = ctk.BooleanVar()
        self.has_rotation_exception = ctk.BooleanVar()
        self.ruleset_model_file_paths = {}
        self.output_directory = ctk.StringVar()

        self.rmds = []
        self.warnings = []
        self.errors = []

        self.installation_path.set(Config.EQUEST_INSTALL_PATH)

    @staticmethod
    def verify_associated_files(file_path: str) -> bool:
        """
        Check if the directory of the given file contains files with the same name
        or the same name with the suffix ' - Baseline Design' for the specified file types.

        Args:
            file_path (str): The file path to check.

        Returns:
            bool: True if all related files are found, False otherwise.
        """
        # Expected file extensions
        file_extensions = [".erp", ".srp", ".lrp", ".nhk"]

        file_path = Path(file_path)
        base_name = file_path.stem
        directory = file_path.parent

        # Check for each file type
        for ext in file_extensions:
            # Construct file names to check
            normal_file = directory / f"{base_name}{ext}"
            baseline_file = directory / f"{base_name} - Baseline Design{ext}"
            # Check existence
            if not normal_file.is_file() and not baseline_file.is_file():
                return False

        return True

    def generate_rmd_data(self, rpd):
        active_ruleset = self.selected_ruleset.get()
        for ruleset_model_type, file_path in self.ruleset_model_file_paths[
            active_ruleset
        ].items():
            rmd_type_enum = (
                ruleset_model_type.upper() + "_0"
                if ruleset_model_type == "Baseline"
                else ruleset_model_type.upper().replace(" ", "_")
            )
            if file_path:
                rmd = rpd_generator.generate_rmd_structure_from_inp(
                    rpd, file_path, self.processing_dir
                )

                rmd.populate_all_child_data_elements()
                rmd.type = rmd_type_enum
                self.rmds.append(rmd)

    def call_write_rpd_json_from_rmds(self):
        rpd_generator.write_rpd_json_from_rpd(
            self.rpd,
            self.rmds,
            str(Path(self.output_directory.get()) / f"{self.project_name.get()}.json"),
        )

    def get_rmd(self, rmd_type):
        for rmd in self.rmds:
            if rmd.type == rmd_type:
                return rmd
        return None

    @staticmethod
    def summarize_rmd_surfaces(rmd):
        """
        Returns a data structure like the example shown below to facilitate surface comparisons between models.
        {
            ("Space 1", "Zone 1"): {("Surface 1", "Exterior Wall", 1000), ("Surface 2", "Roof", 500)},
            ("Space 2", "Zone 2"): {("Surface 3", "Exterior Wall", 800), ("Surface 4", "Roof", 200)},
        }
        """
        surface_summary_by_zone = {}
        for space_name in rmd.space_map:
            zone = rmd.space_map[space_name]
            surface_summary_by_zone[(space_name, zone.u_name)] = set()

        for surface_name in (
            rmd.ext_wall_names + rmd.int_wall_names + rmd.undg_wall_names
        ):
            surface_obj = rmd.get_obj(surface_name)
            parent_space = surface_obj.parent
            zone = rmd.space_map[parent_space.u_name]
            surface_summary_by_zone[(parent_space.u_name, zone.u_name)].add(
                (
                    surface_obj.u_name,
                    surface_obj.determine_surface_classification(),
                    surface_obj.determine_surface_area(),
                )
            )

        return surface_summary_by_zone

    def check_input_ratios(self, rmd):
        """
        Create a warning message for any/all Boilers, Domestic Water Heaters, and Systems that have
        values <1 for HEAT-INPUT-RATIO, HEAT-INPUT-RATIO, and FURNACE-HIR respectively
        """
        for boiler in rmd.boiler_names:
            boiler_obj = rmd.get_obj(boiler)
            heat_input_ratio = boiler_obj.get_inp("HEAT-INPUT-RATIO")
            if heat_input_ratio is not None and float(heat_input_ratio) <= 1:
                self.warnings.append(
                    f"'{rmd.type}' model, boiler '{boiler}' has a heat input ratio of {heat_input_ratio} which implies an efficiency greater than 100%"
                )
        for domestic_water_heater in rmd.domestic_water_heater_names:
            domestic_water_heater_obj = rmd.get_obj(domestic_water_heater)
            heat_input_ratio = domestic_water_heater_obj.get_inp("HEAT-INPUT-RATIO")
            if heat_input_ratio is not None and float(heat_input_ratio) <= 1:
                self.warnings.append(
                    f"'{rmd.type}' model, domestic water heater '{domestic_water_heater}' has a heat input ratio of {heat_input_ratio} which implies an efficiency greater than 100%"
                )
        for system in rmd.system_names:
            system_obj = rmd.get_obj(system)
            heat_input_ratio = system_obj.get_inp("FURNACE-HIR")
            if heat_input_ratio is not None and float(heat_input_ratio) <= 1:
                self.warnings.append(
                    f"'{rmd.type}' model, HVAC system '{system}' has a heat input ratio of {heat_input_ratio} which implies an efficiency greater than 100%"
                )

    def check_space_and_zone_data(self, rmd):
        """
        Perform various checks for valid/supported data in the Space and Zone objects.
        """

        for space_name in rmd.space_map:
            space_obj = rmd.get_obj(space_name)
            zone_obj = rmd.space_map.get(space_name)

            # Verify that ZONE-TYPE keyword is not PLENUM for all spaces
            if (
                space_obj.get_inp(BDL_SpaceKeywords.ZONE_TYPE)
                == BDL_ZoneTypeOptions.PLENUM
            ):
                self.warnings.append(
                    f"'{rmd.type}' model, space '{space_name}': Plenum is not accurately supported by 229P. You may see unexpected outcomes."
                )

            # Verify that TYPE keyword is not PLENUM for all zones
            if zone_obj.get_inp(BDL_ZoneKeywords.TYPE) == BDL_ZoneTypeOptions.PLENUM:
                self.warnings.append(
                    f"'{rmd.type}' model, zone '{zone_obj.u_name}': Plenum is not accurately supported by 229P. You may see unexpected outcomes."
                )

            # Verify that the LTG-SPEC-METHOD is POWER-DEFINITION for all spaces
            if (
                space_obj.get_inp(BDL_SpaceKeywords.LTG_SPEC_METHOD)
                != BDL_LightingSpecMethodOptions.POWER_DEFINITION
            ):
                self.errors.append(
                    f"'{rmd.type}' model, space '{space_name}': The '{space_obj.get_inp(BDL_SpaceKeywords.LTG_SPEC_METHOD)}' lighting specification method is not supported by this application."
                )

    def check_model_data(self, rmd, ref_model_surface_summary_by_zone, ref_model_type):
        # Check for DOE version 2.3 - error
        if not rmd.doe2_version.startswith("DOE-2.3"):
            self.errors.append(f"'{rmd.type}' model must use DOE-2.3")

        # Verify that Baseline (0, 90, 180, 270) and Proposed have the same number of zones
        if len(rmd.zone_names) != len(ref_model_surface_summary_by_zone):
            self.warnings.append(
                f"'{rmd.type}' model has a different number of zones than the {ref_model_type} model. This may lead to unexpected outcomes."
            )

        # Verify that the IDs of all zones match between models
        if set(rmd.zone_names) != set(
            [
                space_name_zone_name[1]
                for space_name_zone_name in ref_model_surface_summary_by_zone.keys()
            ]
        ):
            self.warnings.append(
                f"'{rmd.type}' model has different zone names than the {ref_model_type} model. This may lead to unexpected outcomes."
            )

        # Verify that the IDs of all spaces match between models
        if set(rmd.space_map.keys()) != set(
            [
                space_name_zone_name[0]
                for space_name_zone_name in ref_model_surface_summary_by_zone.keys()
            ]
        ):
            self.warnings.append(
                f"'{rmd.type}' model has different space names than the {ref_model_type} model. This may lead to unexpected outcomes."
            )

        # Verify that the surface details match between models
        baseline_surface_summary_by_zone = self.summarize_rmd_surfaces(rmd)
        for (
            space_name_zone_name_b,
            surface_summary_b,
        ) in baseline_surface_summary_by_zone.items():
            if (
                space_name_zone_name_b in ref_model_surface_summary_by_zone
                and surface_summary_b
                != ref_model_surface_summary_by_zone[space_name_zone_name_b]
            ):
                self.warnings.append(
                    f"'{rmd.type}' model, space {space_name_zone_name_b[0]} has different surface details than the {ref_model_type} model. This may lead to unexpected outcomes."
                )
                # Only provide the first warning for this issue
                break

    def run_model_checks(self):
        # Use the first model as a reference to verify the other models have the same qty and IDs for spaces, zones, and surfaces
        reference_rmd = self.rmds[0]
        reference_surface_summary_by_zone = self.summarize_rmd_surfaces(reference_rmd)
        reference_model_type = reference_rmd.type if reference_rmd else None

        self.check_space_and_zone_data(reference_rmd)
        self.check_input_ratios(reference_rmd)
        if len(self.rmds) > 1:
            for rmd in self.rmds[1:]:
                self.check_model_data(
                    rmd, reference_surface_summary_by_zone, reference_model_type
                )
                self.check_space_and_zone_data(rmd)
                self.check_input_ratios(rmd)
