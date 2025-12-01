import atexit
import tempfile
import customtkinter as ctk
from pathlib import Path
from copy import deepcopy

from rpd_generator import main as rpd_generator
from rpd_generator.artifacts.ruleset_project_description import (
    RulesetProjectDescription,
)
from rpd_generator.doe2_file_io.model_input_reader import ModelInputReader
from rpd_generator.config import Config
from rpd_generator.schema.schema_enums import SchemaEnums
from rpd_generator.bdl_structure.bdl_enumerations.bdl_enums import BDLEnums
from rpd_generator.bdl_structure.bdl_commands.space import BDL_SpaceKeywords

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
        self.applicable_models = set()
        self.output_directory = ctk.StringVar()

        self.rmds = []
        self.model_issues = {}
        self.warnings = []
        self.errors = []

        self.loaded_models = {}
        self.active_rpd_path = None
        self.active_rct_report_path = None

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

    def generate_rmd_data(self, rpd: RulesetProjectDescription, progress_cb=None):
        """
        Build RMDs from active models. If provided, progress_cb(done:int, total:int, msg:str)
        is called after each model (including implicit Proposed clone) is created.
        """
        self.rmds = []
        active_models = {m: p for m, p in self.iter_active_models()}
        print(f"Active models: {active_models}")
        # Only count models with an actual path
        base_total = sum(1 for _, path in active_models.items() if path)
        print(f"Processing {base_total} active models.")

        # Will we create an implicit Proposed clone from User?
        will_clone_proposed = (
            self.selected_ruleset.get() != "None"
            and "User" not in active_models
            and bool(active_models.get("Proposed"))
        )
        print(f"Will clone User from Proposed: {will_clone_proposed}")

        total_to_create = base_total + (1 if will_clone_proposed else 0)
        print(f"Total RMDs to create: {total_to_create}")
        done = 0

        for model_type, file_path in active_models.items():
            print(f"Model type: {model_type}, file path: {file_path}")
            if not file_path:
                continue
            print(f"Generating RMD for {model_type} from {file_path}")
            rmd_type_enum = (
                model_type.upper() + "_0"
                if model_type == "Baseline"
                else model_type.upper().replace(" ", "_")
            )
            rmds = rpd_generator.generate_rmd_objects_from_inps(
                rpd, [file_path], self.processing_dir
            )
            rmd = rmds[0]
            rmd.populate_all_child_data_elements()
            rmd.type = rmd_type_enum
            self.rmds.append(rmd)
            rmd.populate_data_group()

            done += 1
            if progress_cb:
                progress_cb(done, total_to_create, f"Creating RMD: {rmd.type}")

            # implicit Proposed from User if needed
            if (
                self.selected_ruleset.get() != "None"
                and model_type == "Proposed"
                and "User" not in active_models
            ):
                user_rmd = deepcopy(rmd)
                user_rmd.rpd = rmd.rpd
                user_rmd.obj_id = f"{rmd.obj_id} - User"
                user_rmd.type = "USER"
                self.rmds.append(user_rmd)
                user_rmd.populate_data_group()

                done += 1
                if progress_cb:
                    progress_cb(done, total_to_create, f"Creating RMD: {rmd.type}")

    def call_write_rpd_json_from_rmds(self):
        output_path = (
            Path(self.output_directory.get()) / f"{self.project_name.get()}.rpd"
        )

        rpd_generator.write_rpd_json_from_rpd(
            self.rpd,
            self.rmds,
            str(output_path),
        )
        self.active_rpd_path = str(output_path)
        print(f"RPD generated and set as active: {output_path}")

    def get_rmd(self, rmd_type):
        for rmd in self.rmds:
            if rmd.type == rmd_type:
                return rmd
        return None

    def set_applicable_models(self, models: list[str]):
        self.applicable_models = set(models)

    def is_model_active(self, model_type: str) -> bool:
        return model_type in self.applicable_models

    def get_effective_path(self, ruleset: str, model_type: str) -> str | None:
        if model_type == "Proposed" and self.proposed_reflects_design.get():
            return self.ruleset_model_file_paths[ruleset].get("User")
        return self.ruleset_model_file_paths[ruleset].get(model_type)

    def iter_active_models(self):
        """Yield (model_type, effective_path) for currently applicable models only."""
        ruleset = self.selected_ruleset.get()
        for model_type in self.applicable_models:
            yield model_type, self.get_effective_path(ruleset, model_type)

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
            if heat_input_ratio is not None and float(heat_input_ratio.strip()) <= 1:
                self.warnings.append(
                    f"{rmd.type} model, boiler '{boiler}' has a heat input ratio of {float(heat_input_ratio.strip())} which implies an efficiency greater than 100%"
                )
        for domestic_water_heater in rmd.domestic_water_heater_names:
            domestic_water_heater_obj = rmd.get_obj(domestic_water_heater)
            heat_input_ratio = domestic_water_heater_obj.get_inp("HEAT-INPUT-RATIO")
            if heat_input_ratio is not None and float(heat_input_ratio.strip()) <= 1:
                self.warnings.append(
                    f"{rmd.type} model, domestic water heater '{domestic_water_heater}' has a heat input ratio of {float(heat_input_ratio.strip())} which implies an efficiency greater than 100%"
                )
        for system in rmd.system_names:
            system_obj = rmd.get_obj(system)
            heat_input_ratio = system_obj.get_inp("FURNACE-HIR")
            if heat_input_ratio is not None and float(heat_input_ratio.strip()) <= 1:
                self.warnings.append(
                    f"{rmd.type} model, HVAC system '{system}' has a heat input ratio of {float(heat_input_ratio.strip())} which implies an efficiency greater than 100%"
                )

    def check_space_and_zone_data(self, rmd):
        """
        Perform various checks for valid/supported data in the Space and Zone objects.
        """
        spaces_without_ltg_space_type = []
        for space_name in rmd.space_map:
            space_obj = rmd.get_obj(space_name)

            # Verify that the LTG-SPEC-METHOD is POWER-DEFINITION for all spaces
            # LUMINAIRE-COUNT and ILLUMINANCE input methods are not supported
            if (
                space_obj.get_inp(BDL_SpaceKeywords.LTG_SPEC_METHOD)
                != BDL_LightingSpecMethodOptions.POWER_DEFINITION
            ):
                self.errors.append(
                    f"{rmd.type} model, space '{space_name}': The '{space_obj.get_inp(BDL_SpaceKeywords.LTG_SPEC_METHOD)}' lighting specification method is not supported by this application."
                )

            if not space_obj.lighting_space_type:
                spaces_without_ltg_space_type.append(space_name)

        if spaces_without_ltg_space_type:
            count = len(spaces_without_ltg_space_type)
            space_spaces = "space" if count == 1 else "spaces"
            has_have = "has" if count == 1 else "have"

            self.warnings.append(
                f"{rmd.type} model: {count} {space_spaces} {has_have} no lighting space type defined. "
                "This may lead to a large number of Undetermined outcomes."
            )

    def check_model_data(self, rmd, ref_model_surface_summary_by_zone, ref_model_type):
        # Check for DOE version 2.3 - error
        if not rmd.doe2_version.startswith("DOE-2.3"):
            self.errors.append(f"{rmd.type} model must use DOE-2.3")

        # Verify that Baseline (0, 90, 180, 270) and Proposed have the same number of zones
        if len(rmd.zone_names) != len(ref_model_surface_summary_by_zone):
            self.warnings.append(
                f"{rmd.type} model has a different number of zones than the {ref_model_type} model. This may lead to unexpected outcomes."
            )

        # Verify that the IDs of all zones match between models
        if set(rmd.zone_names) != set(
            [
                space_name_zone_name[1]
                for space_name_zone_name in ref_model_surface_summary_by_zone.keys()
            ]
        ):
            self.warnings.append(
                f"{rmd.type} model has different zone names than the {ref_model_type} model. This may lead to unexpected outcomes."
            )

        # Verify that the IDs of all spaces match between models
        if set(rmd.space_map.keys()) != set(
            [
                space_name_zone_name[0]
                for space_name_zone_name in ref_model_surface_summary_by_zone.keys()
            ]
        ):
            self.warnings.append(
                f"{rmd.type} model has different space names than the {ref_model_type} model. This may lead to unexpected outcomes."
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
                    f"{rmd.type} model, space {space_name_zone_name_b[0]} has different surface details than the {ref_model_type} model. This may lead to unexpected outcomes."
                )
                # Only provide the first warning for this issue
                break

    def run_model_checks(self):
        reference_rmd = self.rmds[0]
        reference_surface_summary_by_zone = self.summarize_rmd_surfaces(reference_rmd)
        reference_model_type = reference_rmd.type if reference_rmd else None

        # Clear old check-based issues (but keep associated-file issues)
        for model in list(self.model_issues.keys()):
            # Only remove entries that came from run_model_checks
            self.model_issues[model] = [
                msg for msg in self.model_issues[model] if not msg.startswith("[CHECK]")
            ]

        def add_issue(rmd, msg, is_error=False):
            model_name = self.model_name_from_rmd_type(rmd.type)
            tag = "[ERROR]" if is_error else "[WARN]"
            entry = f"{tag} {msg}"

            if model_name not in self.model_issues:
                self.model_issues[model_name] = []

            self.model_issues[model_name].append(entry)

        # Run checks on reference model
        self.check_space_and_zone_data(reference_rmd)
        self.check_input_ratios(reference_rmd)

        # Re-route warnings/errors
        for w in self.warnings:
            add_issue(reference_rmd, w)
        for e in self.errors:
            add_issue(reference_rmd, e, is_error=True)

        self.warnings.clear()
        self.errors.clear()

        if len(self.rmds) > 1:
            for rmd in self.rmds[1:]:
                self.check_model_data(
                    rmd, reference_surface_summary_by_zone, reference_model_type
                )
                self.check_space_and_zone_data(rmd)
                self.check_input_ratios(rmd)

                for w in self.warnings:
                    add_issue(rmd, w)
                for e in self.errors:
                    add_issue(rmd, e, is_error=True)

                self.warnings.clear()
                self.errors.clear()

    def model_name_from_rmd_type(self, rmd_type: str) -> str:
        """
        Map RMD.type → the model row name used in the UI.
        """
        t = rmd_type.upper()

        # The USER model is the Design model
        if t == "USER":
            return "Design"

        if t.startswith("BASELINE"):
            return "Baseline"

        if t == "PROPOSED":
            return "Proposed"

        # Fallback-safe behavior (not normally used)
        return t.title()
