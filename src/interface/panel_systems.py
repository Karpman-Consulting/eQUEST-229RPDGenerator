import time
import threading
import traceback
import customtkinter as ctk
from jsonpath_ng.ext import parse

from interface.constants import HEADER_FONT, TEXT_FONT
from interface.error_window import ErrorWindow
from rpd_generator.schema.schema_utils import quantify_rmd
from rpd_generator.utilities.ashrae9012019.get_baseline_system_types import (
    get_baseline_system_types,
)
from rpd_generator.utilities.ashrae9012019.get_zone_target_baseline_system import (
    get_zone_target_baseline_system,
)


class BaselineSystemTypesPanel(ctk.CTkFrame):
    def __init__(self, parent, main_app):
        super().__init__(parent)
        self.main_app = main_app

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(5, weight=1)

        # -----------------------------------------------------
        # Title
        # -----------------------------------------------------
        ctk.CTkLabel(
            self,
            text="Check ASHRAE 90.1 Baseline HVAC Systems",
            font=HEADER_FONT,
            anchor="w",
        ).grid(row=0, column=0, sticky="ew", padx=8, pady=(8, 4))

        ctk.CTkLabel(
            self,
            text=(
                "Evaluates each RMD and compares each zone’s modeled baseline HVAC system\n"
                "against the expected baseline system type based on 90.1-2019 rules."
            ),
            font=TEXT_FONT,
            anchor="w",
            justify="left",
        ).grid(row=1, column=0, sticky="ew", padx=8, pady=(0, 12))

        # -----------------------------------------------------
        # Run button
        # -----------------------------------------------------
        self.run_button = ctk.CTkButton(
            self,
            text="Run Baseline System Check",
            width=220,
            command=self._run_check_clicked,
        )
        self.run_button.grid(row=2, column=0, sticky="w", padx=8, pady=(0, 12))

        # -----------------------------------------------------
        # Warning banner
        # -----------------------------------------------------
        self.warning_frame = ctk.CTkFrame(self, fg_color="#FFF3CD", corner_radius=6)
        self.warning_frame.grid(row=3, column=0, sticky="ew", padx=8, pady=(0, 6))
        self.warning_frame.grid_remove()

        # -----------------------------------------------------
        # Header row (fixed)
        # -----------------------------------------------------
        self.header_frame = ctk.CTkFrame(self, fg_color="#E4E7EB")
        self.header_frame.grid(row=4, column=0, sticky="ew", padx=8)

        # 6 columns including Details
        self.col_min_widths = [120, 120, 140, 100, 240, 80]

        for i, width in enumerate(self.col_min_widths):
            self.header_frame.grid_columnconfigure(i, weight=1, minsize=width)

        headers = ["Zone", "Expected", "Modeled", "Result", "HVAC IDs", "Details"]
        for col, text in enumerate(headers):
            ctk.CTkLabel(
                self.header_frame,
                text=text,
                font=TEXT_FONT,
                text_color="#1F2937",
                anchor="w",
                padx=10,
                pady=6,
            ).grid(row=0, column=col, sticky="nsew")

        # -----------------------------------------------------
        # Scrollable results table
        # -----------------------------------------------------
        self.table_frame = ctk.CTkScrollableFrame(self, fg_color="#FFFFFF")
        self.table_frame.grid(row=5, column=0, sticky="nsew", padx=8, pady=(0, 12))

        # Must match header: 6 columns
        for i, width in enumerate(self.col_min_widths):
            self.table_frame.grid_columnconfigure(i, weight=1, minsize=width)

    # ------------------------------------------------------------------
    # Baseline System Logic
    # ------------------------------------------------------------------
    def check_baseline_systems(self):
        """
        Returns structure:
            results[rmd_type] = [
                {
                    "zone_id": ...,
                    "expected": ...,
                    "modeled": ...,
                    "result": ...,
                    "hvac_ids": [...],
                    "debug": { ... all diagnostics ... }
                }
            ]
        """
        t_start = time.perf_counter()

        rpd = self.main_app.data.rpd.rpd_data_structure

        t0 = time.perf_counter()
        rpd = quantify_rmd(rpd)
        print("quantify_rmd:", time.perf_counter() - t0)

        t1 = time.perf_counter()
        rmd_p = next(
            rmd
            for rmd in rpd.get("ruleset_model_descriptions", [])
            if rmd.get("type", "").upper() == "PROPOSED"
        )
        print("find proposed:", time.perf_counter() - t1)

        for rmd_b in rpd.get("ruleset_model_descriptions", []):
            if not rmd_b.get("type", "").upper().startswith("BASELINE"):
                continue

            t2 = time.perf_counter()
            zones_b = [
                m.value
                for m in parse("$.buildings[*].building_segments[*].zones[*]").find(
                    rmd_b
                )
            ]
            print("zones jsonpath:", time.perf_counter() - t2)

            t3 = time.perf_counter()
            zone_target_baseline_systems = get_zone_target_baseline_system(
                rmd_b, rmd_p, rmd_b.get("weather", {}).get("climate_zone", "")
            )
            print("baseline system calc:", time.perf_counter() - t3)

        print("TOTAL:", time.perf_counter() - t_start)
        try:
            rpd = self.main_app.data.rpd.rpd_data_structure
        except Exception:
            return {"error": "RPD structure unavailable."}

        rpd = quantify_rmd(rpd)
        results = {}

        # -----------------------------
        # Find Proposed RMD
        # -----------------------------
        rmd_p = next(
            (
                rmd
                for rmd in rpd.get("ruleset_model_descriptions", [])
                if rmd.get("type", "").upper() == "PROPOSED"
            ),
            None,
        )
        if not rmd_p:
            return {"error": "Proposed RMD not found"}

        # -----------------------------
        # Process each Baseline RMD
        # -----------------------------
        for rmd_b in rpd.get("ruleset_model_descriptions", []):
            rmd_type = rmd_b.get("type", "")
            if not rmd_type.upper().startswith("BASELINE"):
                continue

            # ---- Zones ----
            zones_b = [
                m.value
                for m in parse("$.buildings[*].building_segments[*].zones[*]").find(
                    rmd_b
                )
            ]

            # ---- HVAC IDs per zone ----
            hvacs_serving_zones = {}
            for zone in zones_b:
                hvacs_serving_zones[zone["id"]] = list(
                    {
                        m.value
                        for m in parse(
                            "$.terminals[*].served_by_heating_ventilating_air_conditioning_system"
                        ).find(zone)
                    }
                )

            # ---- Modeled baseline types ----
            baseline_system_types = get_baseline_system_types(rmd_b)
            baseline_type_by_hvac_id = {
                hvac_id: sys_type
                for sys_type, hvac_list in baseline_system_types.items()
                for hvac_id in hvac_list
            }

            # ---- Expected baseline types & debug ----
            climate_zone = rmd_b.get("weather", {}).get("climate_zone", "")
            zone_target_baseline_systems = get_zone_target_baseline_system(
                rmd_b, rmd_p, climate_zone
            )

            rmd_results = []

            # ---- Compare zone-by-zone ----
            for zone in zones_b:
                zone_id = zone["id"]

                expected_data = zone_target_baseline_systems.get(zone_id, {})
                expected_system = expected_data.get("expected_system_type", "Unmatched")
                debug_data = expected_data.get("debug", {})

                hvac_ids = hvacs_serving_zones.get(zone_id, [])
                modeled_types = {
                    baseline_type_by_hvac_id.get(hvac_id, "Unmatched")
                    for hvac_id in hvac_ids
                }

                if len(modeled_types) == 1:
                    modeled_system = modeled_types.pop()
                elif len(modeled_types) > 1:
                    modeled_system = "Multiple Systems"
                else:
                    modeled_system = "Unmatched"

                result = "PASS" if modeled_system == expected_system else "FAIL"

                rmd_results.append(
                    {
                        "zone_id": zone_id,
                        "expected": expected_system,
                        "modeled": modeled_system,
                        "result": result,
                        "hvac_ids": hvac_ids,
                        "debug": debug_data,
                    }
                )

            results[rmd_type] = rmd_results

        return results

    # ------------------------------------------------------------------
    # Run button
    # ------------------------------------------------------------------
    def _run_check_clicked(self):
        if not hasattr(self.main_app.data, "rpd"):
            err = ErrorWindow(self, error_message="No RPD loaded.")
            err.grab_set()
            return

        self.run_button.configure(state="disabled", text="Running...")

        thread = threading.Thread(target=self._run_system_check_thread, daemon=True)
        thread.start()

    def _run_system_check_thread(self):
        try:
            results = self.check_baseline_systems()
        except Exception:
            tb = traceback.format_exc()
            self.after(0, lambda: self._thread_finish_with_error(tb))
            return

        self.after(0, lambda: self._populate_results_table(results))

    def _populate_results_table(self, results):
        try:
            self._populate_results_table_impl(results)
        except Exception:
            tb = traceback.format_exc()
            self._thread_finish_with_error(tb)

    def _populate_results_table_impl(self, results):
        if isinstance(results, dict) and "error" in results:
            self._thread_finish_with_error(results["error"])
            return

        self.run_button.configure(state="normal", text="Run Baseline System Check")

        # Clear UI
        for child in self.table_frame.winfo_children():
            child.destroy()
        for child in self.warning_frame.winfo_children():
            child.destroy()
        self.warning_frame.grid_remove()

        # -----------------------------------------------------
        # Build warnings
        # -----------------------------------------------------
        warnings = []

        for rmd_type, items in results.items():
            fail_count = sum(1 for entry in items if entry["result"] != "PASS")
            if fail_count:
                warnings.append(
                    f"{rmd_type}: {fail_count} zone(s) failed the baseline system type check."
                )
            for entry in items:
                if entry["modeled"] == "Multiple Systems":
                    warnings.append(
                        f"{rmd_type}: Zone {entry['zone_id']} has multiple HVAC systems"
                    )

        if warnings:
            self.warning_frame.grid()
            for w in warnings:
                ctk.CTkLabel(
                    self.warning_frame,
                    text=f"⚠️ {w}",
                    font=TEXT_FONT,
                    text_color="#856404",
                    anchor="w",
                    pady=3,
                ).pack(anchor="w", padx=10)

        # -----------------------------------------------------
        # Fill table
        # -----------------------------------------------------
        row_i = 0

        for rmd_type, items in results.items():

            # --- Section header ---
            ctk.CTkLabel(
                self.table_frame,
                text=f"--- {rmd_type} ---",
                font=TEXT_FONT,
                text_color="#6B7280",
                fg_color="#F0F0F0",
                anchor="w",
                padx=10,
                pady=6,
            ).grid(row=row_i, column=0, columnspan=6, sticky="ew")
            row_i += 1

            sorted_items = sorted(
                items,
                key=lambda r: {"FAIL": 0, "WARN": 1, "PASS": 2}.get(r["result"], 3),
            )

            for entry in sorted_items:
                zone = entry["zone_id"]
                exp = entry["expected"]
                modeled = entry["modeled"]
                hvac_str = ", ".join(entry["hvac_ids"]) or "—"
                result = entry["result"]

                # Color coding
                if result == "PASS":
                    color = "#2E8540"
                    icon = "✅"
                elif modeled == "Multiple Systems":
                    color = "#C47F16"
                    icon = "⚠️"
                elif modeled == "Unmatched":
                    color = "#6B7280"
                    icon = "⚪"
                else:
                    color = "#C62828"
                    icon = "❌"

                values = [zone, exp, modeled, f"{icon} {result}", hvac_str]
                row_bg = "#FFFFFF" if (row_i % 2 == 0) else "#F7F9FA"

                # Columns 0–4
                for col, val in enumerate(values):
                    ctk.CTkLabel(
                        self.table_frame,
                        text=val,
                        text_color=("#374151" if col != 3 else color),
                        fg_color=row_bg,
                        anchor="w",
                        padx=10,
                        pady=5,
                    ).grid(row=row_i, column=col, sticky="nsew")

                # ------- Details button -------
                details_btn = ctk.CTkButton(
                    self.table_frame,
                    text="Details",
                    width=70,
                    command=lambda zid=zone, debug=entry[
                        "debug"
                    ], rmd=rmd_type: self._open_zone_debug_window(zid, debug, rmd),
                )
                details_btn.grid(row=row_i, column=5, padx=6, pady=5, sticky="w")

                row_i += 1

    # ------------------------------------------------------------------
    # DEBUG DETAILS WINDOW
    # ------------------------------------------------------------------
    key_str_map = {
        "expected_system_type_from_table": "Table G3.1.1 Expected System Type",
        "system_origin_from_table": "Look-up Criteria Origin",
        "building_area_type": "Building Area Type",
        "num_floors": "Number of Floors",
        "floor_area": "Total Building Type Floor Area",
        "applied": "Applicable",
        "does_zone_meet_g3_1_1c": "Meets G3.1.1c Exception",
        "zone_internal_load_per_area": "Zone Internal Load per Floor Area",
        "avg_internal_load_area": "Average Internal Load per Floor Area",
        "zone_elfh": "Zone EFLH",
        "avg_eflh": "Average EFLH",
        "load_diff": "Internal Load Difference",
        "eflh_diff": "EFLH Difference",
        "does_zone_meet_g3_1_1d": "Meets G3.1.1d Exception",
        "building_total_lab_exhaust": "Building Total Lab Exhaust",
        "zone_is_lab_zone": "Is Lab Zone",
        "does_zone_meet_g3_1_1e": "Meets G3.1.1e Exception",
        "all_spaces_exception_E": "All Heated-Only Lighting Space Types",
        "is_zone_likely_a_vestibule": "Is Zone Likely a Vestibule",
        "is_zone_mechanically_heated_and_not_cooled": "Mechanically Heated and Not Cooled",
        "does_zone_meet_g3_1_1f": "Meets G3.1.1f Exception",
        "is_zone_mechanically_oooled": "Mechanically Cooled",
        "is_system_type_9_or_10": "Is Table G3.1.1 Lookup System Type 9 or 10",
        "does_zone_meet_g3_1_1g": "Meets G3.1.1g Exception",
        "total_computer_zones_peak_cooling_load_b": "Total Computer Zones Peak Cooling Load",
        "zone_is_computer_room_zone": "Is Computer Room Zone",
    }
    conversion_keys = {
        "floor_area": "ft2",
        "zone_internal_load_per_area": "Btu/hr/ft2",
        "avg_internal_load_area": "Btu/hr/ft2",
        "load_diff": "Btu/hr/ft2",
        "building_total_lab_exhaust": "cfm",
        "total_computer_zones_peak_cooling_load_b": "Btu/hr",
    }

    def _open_zone_debug_window(self, zone_id, debug, rmd_type):
        if not debug:
            ErrorWindow(self, error_message="No debug info available for this zone.")
            return

        win = ctk.CTkToplevel(self)
        win.title(f"Debug Details – Zone {zone_id} ({rmd_type})")
        win.geometry("650x750")
        win.grab_set()

        scroll = ctk.CTkScrollableFrame(win, fg_color="#F9FAFB")
        scroll.pack(fill="both", expand=True, padx=10, pady=10)

        def add_section(title, data):
            frame = ctk.CTkFrame(scroll, fg_color="#FFFFFF", corner_radius=6)
            frame.pack(fill="x", pady=10, padx=4)

            ctk.CTkLabel(frame, text=title, font=HEADER_FONT, anchor="w").pack(
                anchor="w", padx=10, pady=6
            )

            def _convert_val(val):
                try:
                    unit = self.conversion_keys.get(key)
                    quantity = val.to(unit)
                    return f"{quantity.magnitude:.2f} {unit}"
                except Exception:
                    return str(val)

            for key, value in data.items():
                if key in self.conversion_keys:
                    value = _convert_val(value)
                ctk.CTkLabel(
                    frame,
                    text=f"{self.key_str_map.get(key, key)}: {value}",
                    font=TEXT_FONT,
                    anchor="w",
                    wraplength=550,
                ).pack(anchor="w", padx=16, pady=2)

        # ---- Zone conditioning ----
        add_section(
            "Zone Conditioning Category",
            {
                "Zone Conditioning Category": debug.get("zone_conditioning_category")
                .replace("_", " ")
                .title()
            },
        )

        # ---- Table G3.1.1 ----
        add_section(
            "Table G3.1.1 (Base System Assignment)", debug.get("table_g3_1_1", {})
        )

        # ---- Exceptions ----
        exceptions = debug.get("exceptions", {})
        for exc_name in [
            "g3_1_1b",
            "g3_1_1c",
            "g3_1_1d",
            "g3_1_1e",
            "g3_1_1f",
            "g3_1_1g",
        ]:
            if exc_name in exceptions:
                add_section(exc_name.upper(), exceptions[exc_name])

        # ---- Final assignment ----
        add_section(
            "Final Baseline System",
            {
                "Expected System": debug.get("final_expected_system_type"),
                "System Origin": debug.get("final_system_origin"),
            },
        )

        ctk.CTkButton(win, text="Close", command=win.destroy).pack(pady=10)

    # ------------------------------------------------------------------
    # Errors
    # ------------------------------------------------------------------
    def _thread_finish_with_error(self, tb):
        self.run_button.configure(state="normal", text="Run Baseline System Check")

        try:
            err = ErrorWindow(self, error_message=str(tb))
            err.grab_set()
        except Exception as e:
            print("Error displaying ErrorWindow:", e)
            print(tb)
