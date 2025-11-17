import threading
from functools import partial
import os
import sys
import subprocess
import ast
import json
import re
from pathlib import Path
import customtkinter as ctk
from tkinter import filedialog, messagebox
from tksheet import Sheet

from openpyxl import Workbook, load_workbook
from openpyxl.styles import Font
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.datavalidation import DataValidation

from rpd_generator.schema.schema_enums import SchemaEnums
from rpd_generator.bdl_structure.bdl_commands.space import Space
from rpd_generator.artifacts.building_segment import BuildingSegment
from rpd_generator.doe2_file_io.model_input_reader import ModelInputReader
from rpd_generator.doe2_file_io.model_input_editor import ModelInputEditor, INPEdits
from interface.space_type_guessing import *


LightingBuildingAreaOptions = SchemaEnums.schema_enums[
    "LightingBuildingAreaOptions2019ASHRAE901T951TG38"
]


class RulesetValuesPanel(ctk.CTkFrame):
    """
    Climate Zone and Space Types editor

    Adds lots of print() statements (flush=True) to follow control flow.
    Control noisiness with environment variable STP_VERBOSE_SPACE_LIMIT (default 20).
    """

    climate_zone_values = {}
    climate_zone_options = [
        "",
        "CZ0A",
        "CZ0B",
        "CZ1A",
        "CZ1B",
        "CZ2A",
        "CZ2B",
        "CZ3A",
        "CZ3B",
        "CZ3C",
        "CZ4A",
        "CZ4B",
        "CZ4C",
        "CZ5A",
        "CZ5B",
        "CZ5C",
        "CZ6A",
        "CZ6B",
        "CZ7",
        "CZ8",
    ]
    cz_letter_map = {1: "A", 2: "B", 3: "C"}
    cz_letter_rev = {v: k for k, v in cz_letter_map.items()}

    # ------------------------------
    # Debug helpers & knobs
    # ------------------------------
    DEBUG = False
    DEBUG_CZ = False
    VERBOSE_SPACE_LIMIT = int(os.environ.get("STP_VERBOSE_SPACE_LIMIT", "20"))

    def _dbg(self, *args):
        if self.DEBUG:
            print("[SpaceTypesPanel]", *args, flush=True)

    def _czdbg(self, *args):
        if self.DEBUG_CZ:
            print("[CZ]", *args, flush=True)

    @staticmethod
    def _resolve_occupancy_type(raw):
        def to_int_or_none(x):
            try:
                return int(float(x))
            except (TypeError, ValueError):
                return ""

        if isinstance(raw, list):
            cleaned = list(raw)
            while cleaned:
                last = to_int_or_none(cleaned[-1])
                if last == 0:
                    cleaned.pop()
                else:
                    break
            if not cleaned:
                return ""
            raw = cleaned[0]
        occ_int = to_int_or_none(raw)
        if occ_int is None:
            return ""
        return Space.lighting_space_map.get(occ_int)

    @staticmethod
    def _resolve_building_type(raw):
        """
        Convert raw BLDG-TYPE numeric values into dropdown display names.
        Uses BuildingSegment.lighting_building_area_map
        """

        def to_int_or_none(x):
            try:
                return int(float(x))
            except (TypeError, ValueError):
                return ""

        if isinstance(raw, list):
            cleaned = list(raw)
            while cleaned:
                last = to_int_or_none(cleaned[-1])
                if last == 0:
                    cleaned.pop()
                else:
                    break
            if not cleaned:
                return ""
            raw = cleaned[0]
        bldg_int = to_int_or_none(raw)
        if bldg_int is None:
            return ""
        return (
            BuildingSegment.lighting_building_area_map.get(bldg_int)
            .replace("_", " ")
            .title()
        )

    @staticmethod
    def _levenshtein(a, b):
        if a == b:
            return 0
        if abs(len(a) - len(b)) > 2:
            return 3
        dp = range(len(b) + 1)
        for i, ca in enumerate(a, 1):
            ndp = [i]
            for j, cb in enumerate(b, 1):
                ndp.append(min(dp[j] + 1, ndp[j - 1] + 1, dp[j - 1] + (ca != cb)))
            dp = ndp
        return dp[-1]

    def __init__(self, parent, main_app):
        super().__init__(parent)
        self.main_app = main_app
        self._dbg("__init__ starting…")

        # --- Data structures ---
        self.model_files = []
        self.model_labels = []
        self.file_by_label = {}
        self.original_matrix = {}
        self.unsaved_climate_zone = False
        self.site_uid_map = {}
        self.cz_values_runtime = {}
        self.unsaved_spaces = set()
        self._disabled_cells = set()
        self.confidence_visible = False

        # Climate zone UI
        self.cz_widgets = {}  # file_path -> dropdown widget
        self.cz_label = None  # label "Climate Zone"

        # --- UI (single column) ---
        self.grid_columnconfigure(0, weight=1)
        # Sheet is on row=2, so make that the stretchable row
        self.grid_rowconfigure(2, weight=1)

        # Top controls row
        top = ctk.CTkFrame(self)
        top.grid(row=0, column=0, sticky="ew", padx=8, pady=(8, 6))
        top.grid_columnconfigure(0, weight=1)

        self.guess_button = ctk.CTkButton(
            top,
            text="Guess From Names",
            command=self.guess_all_from_names,
            state="disabled",
        )
        self.guess_button.grid(row=0, column=0, sticky="w")

        self.export_button = ctk.CTkButton(
            top,
            text="Export",
            width=90,
            command=self.export_to_excel,
            state="disabled",
        )
        self.export_button.grid(row=0, column=1, padx=(8, 0))
        self.import_button = ctk.CTkButton(
            top,
            text="Import",
            width=90,
            command=self.import_from_excel,
            state="disabled",
        )
        self.import_button.grid(row=0, column=2, padx=(8, 0))

        self.status_var = ctk.StringVar(value="Idle")
        ctk.CTkLabel(top, textvariable=self.status_var).grid(
            row=0, column=3, sticky="e", padx=(8, 0)
        )

        # Climate zone frame (now owns all CZ widgets)
        cz_frame = ctk.CTkFrame(self)
        cz_frame.grid(row=1, column=0, sticky="ew", padx=8, pady=(0, 6))
        cz_frame.grid_columnconfigure(0, weight=0)
        self.cz_frame = cz_frame
        self.grid_rowconfigure(1, weight=0)
        self.cz_frame.grid_propagate(False)
        self.cz_frame.configure(height=30)

        # Sheet area (space types only)
        sheet_frame = ctk.CTkFrame(self)
        sheet_frame.grid(row=2, column=0, sticky="nsew", padx=8, pady=(0, 8))

        self.sheet = Sheet(
            sheet_frame,
            data=[],
            headers=["Space Name", "Building Type", "Space Type"],
            show_top_left=True,
        )
        self.sheet.pack(fill="both", expand=True)

        self.sheet.bind("<<SheetModified>>", self._on_sheet_modified)
        self.sheet.bind("<Delete>", self._clear_selected_cells)
        self.sheet.bind("<BackSpace>", self._clear_selected_cells)

        self.sheet.enable_bindings(
            (
                "single_select",
                "row_select",
                "column_select",
                "arrowkeys",
                "rc_delete_row",
                "rc_popup_menu",
                "edit_cell",
                "copy",
                "paste",
                "delete",
                "undo",
                "redo",
                "drag_select",
                "row_height_resize",
                "column_width_resize",
                "filter_rows",
                "sort_rows",
            )
        )

        # Bottom row
        bottom = ctk.CTkFrame(self)
        bottom.grid(row=3, column=0, sticky="ew", padx=8, pady=(0, 8))
        bottom.grid_columnconfigure(0, weight=1)
        self.save_button = ctk.CTkButton(
            bottom, text="Save Assignments", command=self.save_data, state="disabled"
        )
        self.save_button.grid(row=0, column=0, sticky="e")

        # Dropdown option lists
        self.space_type_options = [""] + [
            v.replace("_", " ").title()
            for k, v in Space.lighting_space_map.items()
            if k != 0
        ]
        self.space_type_display_to_key = {
            v.replace("_", " ").title(): k
            for k, v in Space.lighting_space_map.items()
            if k != 0
        }
        self.building_type_options = [""] + [
            option.replace("_", " ").title()
            for option in LightingBuildingAreaOptions.get_list()
        ]
        self.building_area_display_to_key = {
            v.replace("_", " ").title(): k
            for k, v in BuildingSegment.lighting_building_area_map.items()
            if k != 0
        }

        self._dbg("space_type_options count:", len(self.space_type_options))

        self.color_unsaved_bg = "#fff3cd"
        self.color_unsaved_fg = "#333333"
        self.color_dim_bg = "#dddddd"
        self.color_dim_fg = "#666666"

        # Autoload once the panel is shown
        self.after(50, self.refresh_from_selection)
        self._dbg("__init__ done.")

    # ------------------------------
    # Model collection (from RIGHT panel)
    # ------------------------------
    def _collect_selected_models(self):
        ruleset = self.main_app.data.selected_ruleset.get()
        selected = self.main_app.data.ruleset_model_file_paths.get(ruleset, {})
        pairs = [(label, path) for label, path in selected.items() if path]
        self._dbg("_collect_selected_models: ruleset=", ruleset, "pairs=", pairs)
        return pairs[:6]

    # ------------------------------
    # Climate zone frame helpers (merged)
    # ------------------------------
    def _clear_climate_zone_frame(self):
        """Remove all widgets from the CZ frame and reset state."""
        for w in self.cz_frame.winfo_children():
            w.destroy()
        self.cz_widgets.clear()
        self.cz_label = None
        self.unsaved_climate_zone = False

    def _resolve_merged_climate_zone(self):
        """
        Returns (merged_value, status) for climate zone:

            ok                 all models have CZ, and they agree
            conflict           all models have CZ but values disagree
            missing            CZ missing in some models, but agreement among existing
            missing_conflict   CZ missing in some models AND disagreement among existing
        """
        if not self.model_files:
            return "", "ok"

        per_file = {
            fp: (self.climate_zone_values.get(fp, "") or "") for fp in self.model_files
        }

        existing = {fp: v for fp, v in per_file.items() if v}
        existing_values = set(existing.values())
        all_have_cz = all(per_file.values())

        if existing_values:
            merged = next(iter(existing_values)) if len(existing_values) == 1 else ""
        else:
            merged = ""

        if all_have_cz:
            if merged:
                status = "ok"
            else:
                status = "conflict"
        else:
            if merged:
                status = "missing"
            else:
                # Some models missing, and either no CZ anywhere or disagreement
                status = "missing_conflict"

        return merged, status

    def _style_cz_label_for_status(self, status):
        """Apply base style for CZ label based on merged status (no unsaved overlay)."""
        if not self.cz_label:
            return

        if status == "ok":
            self.cz_label.configure(fg_color="transparent")
        elif status == "conflict":
            # differing values, but present in all models
            self.cz_label.configure(fg_color="#fff3cd", text_color="#000000")  # yellow
        elif status == "missing":
            # some models missing CZ, but those that have it agree
            self.cz_label.configure(fg_color="#dddddd", text_color="#000000")  # gray
        elif status == "missing_conflict":
            # some missing, some disagree → purple
            self.cz_label.configure(fg_color="#d8b4fe", text_color="#000000")  # purple
        else:
            self.cz_label.configure(fg_color="transparent")

    def _populate_climate_zone_frame(self):
        """
        Single merged CZ dropdown:

            Climate Zone [  CZx  ]

        Status styling:
            ok                 → no highlight
            conflict           → yellow
            missing            → gray
            missing_conflict   → purple
        """
        self._clear_climate_zone_frame()

        if not self.model_files:
            return

        # Label
        self.cz_label = ctk.CTkLabel(self.cz_frame, text="Climate Zone")
        self.cz_label.grid(row=0, column=0, padx=(0, 10), sticky="w")

        # Determine merged CZ + status from current per-file values
        merged_cz, status = self._resolve_merged_climate_zone()
        self._czdbg("Merged CZ =", merged_cz, "status =", status)
        self.merged_cz_runtime = merged_cz

        var = ctk.StringVar(value=merged_cz or "")

        def on_change(val):
            val = (val or "").strip()
            self._czdbg("CZ dropdown changed to:", repr(val))

            self.merged_cz_runtime = val
            # Consider unsaved if changed vs original merged value
            any_unsaved = val != merged_cz
            self.unsaved_climate_zone = any_unsaved

            if any_unsaved:
                # Unsaved overlay color
                self.cz_label.configure(
                    fg_color=self.color_unsaved_bg,
                    text_color=self.color_unsaved_fg,
                )
                self._set_idle("Climate zone modified")
            else:
                # Back to status-based style
                self._style_cz_label_for_status(status)
                self._set_idle("Climate zone restored")

        dd = ctk.CTkOptionMenu(
            self.cz_frame,
            variable=var,
            values=self.climate_zone_options,
            command=on_change,
        )
        dd.grid(row=0, column=1, padx=5, pady=(0, 2), sticky="w")

        self.cz_widgets["merged"] = dd
        # Initial style
        self._style_cz_label_for_status(status)

    # ------------------------------
    # Refresh from selection
    # ------------------------------
    def refresh_from_selection(self, from_cache=False):
        """
        Load / reload the sheet based on selected model files.
        If from_cache=True, we reuse pre-parsed data stored in main_app.data.loaded_models.
        """

        self._dbg("refresh_from_selection(from_cache=%s)" % from_cache)

        pairs = self._collect_selected_models()
        self.model_labels = [label for label, _ in pairs]
        self.model_files = [path for _, path in pairs]
        self.file_by_label = {label: path for label, path in pairs}

        if not self.model_files:
            self._clear_climate_zone_frame()
            self._reset_sheet()
            self._set_idle("No models selected.")
            return

        # Always re-build using cached parsed data
        try:
            ruleset = self.main_app.data.selected_ruleset.get()
            model_data_list = []

            for label, path in pairs:
                key = (ruleset, label)
                parsed = self.main_app.data.loaded_models.get(key)

                if parsed is None:
                    # Fallback safety — but should be rare now
                    parsed = ModelInputReader.read_inp_files([path])[0]
                    self.main_app.data.loaded_models[key] = parsed

                model_data_list.append((path, parsed))

        except Exception as e:
            self._clear_climate_zone_frame()
            self._reset_sheet()
            self._set_idle(f"Failed to load cached model data: {e}")
            return

        # Build merged matrix + CZ values from cached dicts
        self._build_matrix_from_cached(model_data_list)

        # Populate CZ UI and sheet UI from matrix (no file IO)
        self._populate_climate_zone_frame()
        self._populate_sheet_from_matrix()

        self._set_idle("Loaded from cache.")

    # ------------------------------
    # Matrix building (merged)
    # ------------------------------
    def _recompute_space_status(self, space):
        """
        Recompute merged info for a given space.
        Supports both:
            - space occupancy type (C-901-OCC-TYPE)
            - building type (C-901-BLDG-TYPE)
        """

        per_file = self.original_matrix.get(space, {})
        exists_in = sorted(per_file.keys())

        # Extract values separately
        occ_values = []
        bldg_values = []
        for fp in exists_in:
            entry = per_file.get(fp, {})
            occ_values.append(entry.get("occ", ""))
            bldg_values.append(entry.get("bldg", ""))

        occ_unique = set(occ_values)
        bldg_unique = set(bldg_values)

        # ------ OCCUPANCY TYPE MERGE ------
        if len(occ_unique) == 1:
            occ_resolved = occ_values[0]
            occ_status = "ok"
        else:
            if len(exists_in) < len(self.model_files) and len(occ_unique) == 1:
                occ_resolved = occ_values[0]
                occ_status = "missing"
            else:
                occ_resolved = ""
                occ_status = (
                    "conflict"
                    if len(exists_in) == len(self.model_files)
                    else "missing_conflict"
                )

        # ------ BUILDING TYPE MERGE ------
        if len(bldg_unique) == 1:
            bldg_resolved = bldg_values[0]
            bldg_status = "uniform"
        else:
            if len(exists_in) < len(self.model_files) and len(bldg_unique) == 1:
                bldg_resolved = bldg_values[0]
                bldg_status = "missing"
            else:
                bldg_resolved = ""
                bldg_status = (
                    "conflict"
                    if len(exists_in) == len(self.model_files)
                    else "missing_conflict"
                )

        self.merged_spaces[space] = {
            "exists_in": exists_in,
            "values": {fp: per_file[fp]["occ"] for fp in exists_in},
            "resolved": occ_resolved,
            "status": occ_status,
            "original_resolved": occ_resolved,
            # NEW FIELDS:
            "bldgtype_values": {fp: per_file[fp]["bldg"] for fp in exists_in},
            "bldgtype_resolved": bldg_resolved,
            "bldgtype_original": bldg_resolved,
            "bldgtype_status": bldg_status,
        }

    def _build_matrix_from_cached(self, model_data_list):
        """
        Build original_matrix and merged space info using cached parsed INP data.
            self.original_matrix[space][file_path] = display_value
            self.merged_spaces[space] = {...}
            self.climate_zone_values[file_path] = "CZx" or ""
        """
        self._dbg("_build_matrix_from_cached()")
        self.original_matrix.clear()
        self.merged_spaces = {}

        # ---- SPACE OCCUPANCY ----
        for file_path, parsed_dict in model_data_list:
            file_cmds = parsed_dict.get("file_commands", {})
            space_cmds = file_cmds.get("SPACE", {})

            for space, cmd in space_cmds.items():
                # skip plenums
                if cmd.get("ZONE-TYPE", "").upper() == "PLENUM":
                    continue

                occ_raw = cmd.get("C-901-OCC-TYPE")
                disp_key = self._resolve_occupancy_type(occ_raw)
                disp = (disp_key or "").replace("_", " ").title()
                if disp not in self.space_type_options:
                    disp = ""
                # --- BUILDING TYPE ---
                bldg_raw = cmd.get("C-901-BLDG-TYPE")
                bldg_disp = self._resolve_building_type(bldg_raw)

                self.original_matrix.setdefault(space, {})
                self.original_matrix[space][file_path] = {
                    "occ": disp,
                    "bldg": bldg_disp,
                }

            # ---- CLIMATE ZONE EXTRACTION ----
            site_cmds = file_cmds.get("SITE-PARAMETERS", {})
            site_uid, site_cmd = next(iter(site_cmds.items()), (None, {}))
            self.site_uid_map[file_path] = site_uid

            def _to_int(raw):
                try:
                    return int(float(raw))
                except Exception:
                    return None

            num = _to_int(site_cmd.get("C-901-CZ-NUMBER"))
            letter_index = _to_int(site_cmd.get("C-901-CZ-LETTER"))

            cz = ""
            if num is not None:
                if num in (7, 8):
                    cz = f"CZ{num}"
                else:
                    if letter_index in self.cz_letter_map:
                        cz_candidate = f"CZ{num}{self.cz_letter_map[letter_index]}"
                        if cz_candidate in self.climate_zone_options:
                            cz = cz_candidate

            self.climate_zone_values[file_path] = cz

        # ---- MERGED SPACE STATUS ----
        for space in sorted(self.original_matrix.keys(), key=str.lower):
            self._recompute_space_status(space)

    # ------------------------------
    # Sheet population (2-column sheet)
    # ------------------------------
    @staticmethod
    def _text_pixel_width(text):
        if not text:
            return 20  # minimum
        # 7 pixels per character is a good approximation for CTk default font
        return max(20, int(len(text) * 7) + 16)

    def _max_building_type_width(self):
        maxw = 0
        for opt in self.building_type_options:
            maxw = max(maxw, self._text_pixel_width(opt))
        return maxw

    def _max_space_type_width(self):
        maxw = 0
        for opt in self.space_type_options:
            maxw = max(maxw, self._text_pixel_width(opt))
        return maxw

    def _style_row_for_status(self, space, row):
        """Apply base status color (does NOT handle 'unsaved' overlay)."""
        info = self.merged_spaces.get(space, {})
        status = info.get("status", "ok")

        # We color only the Value column (index 1)
        if status == "ok":
            # Clear any prior status highlight
            self.sheet.dehighlight_cells(row=row, column=1, redraw=False)
        elif status == "conflict":
            # space exists in all models, but values differ
            self.sheet.highlight_cells(
                row=row, column=1, bg="#fff3cd", fg="#000000", redraw=False  # yellow
            )
        elif status == "missing":
            # space missing in some models, but agreement where it exists
            self.sheet.highlight_cells(
                row=row, column=1, bg="#dddddd", fg="#000000", redraw=False  # gray
            )
        elif status == "missing_conflict":
            # missing in some + disagreement where it exists
            self.sheet.highlight_cells(
                row=row, column=1, bg="#d8b4fe", fg="#000000", redraw=False  # purple
            )

    def _style_bldgtype_cell(self, space, row):
        info = self.merged_spaces[space]
        status = info["bldgtype_status"]

        if status == "uniform":
            return
        elif status == "conflict":
            self.sheet.highlight_cells(row=row, column=1, bg="#ffeb99", fg="#000000")
        elif status == "missing":
            self.sheet.highlight_cells(row=row, column=1, bg="#d9d2e9", fg="#000000")

    def _style_space_cell(self, space, row):
        info = self.merged_spaces[space]
        status = info["status"]

        if status == "ok":
            return
        elif status == "conflict":
            self.sheet.highlight_cells(row=row, column=2, bg="#ffeb99", fg="#000000")
        elif status == "missing":
            self.sheet.highlight_cells(row=row, column=2, bg="#d9d2e9", fg="#000000")
        elif status == "missing_conflict":
            self.sheet.highlight_cells(row=row, column=2, bg="#d8b4fe", fg="#000000")

    def _populate_sheet_from_matrix(self):
        rows = []
        for space, info in sorted(
            self.merged_spaces.items(), key=lambda kv: kv[0].lower()
        ):
            rows.append(
                [
                    space,
                    info["bldgtype_resolved"],  # NEW COLUMN
                    info["resolved"],  # Space type
                ]
            )

        self.sheet.headers(["Space Name", "Building Type", "Space Type"])

        self.sheet.set_sheet_data(rows)

        # Building Type dropdown
        self.sheet.dropdown_column(
            1, values=self.building_type_options, edit_data=False
        )

        # Space Type dropdown
        self.sheet.dropdown_column(2, values=self.space_type_options, edit_data=False)

        # Style each row
        for r, (space, info) in enumerate(sorted(self.merged_spaces.items())):
            # bldg type
            self._style_bldgtype_cell(space, r)
            # space type
            self._style_space_cell(space, r)

        # Enable controls now that sheet data exists
        self.guess_button.configure(state="normal")
        self.export_button.configure(state="normal")
        self.import_button.configure(state="normal")
        self.save_button.configure(state="normal")
        self.sheet.refresh()

        self._autosize_columns()
        self.after_idle(self._autosize_columns)

    # ------------------------------
    # Edit / guess handling
    # ------------------------------

    def _on_sheet_modified(self, event):
        """
        Called when the user edits the single 'Value' column.
        We update merged_spaces[space]['resolved'], mark it unsaved,
        and apply 'unsaved' overlay highlight (pink).
        """
        payload = self._extract_event_payload(event)
        self._dbg("_on_sheet_modified payload:", payload)
        if not isinstance(payload, dict):
            return
        changed_cells = payload.get("cells", {}).get("table", {})
        if not changed_cells:
            return

        for (r, c), _old in changed_cells.items():
            # Only allow editing of column 1 (Value)
            if c not in (1, 2):
                continue

            space = self.sheet.get_cell_data(r, 0)
            info = self.merged_spaces.get(space, {})
            if c == 1:
                # Building type changed
                new_val = self.sheet.get_cell_data(r, 1) or ""
                orig = info.get("bldgtype_original", "")
            elif c == 2:
                # Space type changed
                new_val = self.sheet.get_cell_data(r, 2) or ""
                orig = info.get("original_resolved", "")

            if not space:
                continue

            new_val = new_val.strip()

            # Update runtime merged value
            info["resolved"] = new_val

            # Mark unsaved or restore if unchanged
            if new_val != orig:
                self.unsaved_spaces.add((space, c))
                self.sheet.highlight_cells(
                    row=r,
                    column=0,
                    bg=self.color_unsaved_bg,
                    fg=self.color_unsaved_fg,
                    redraw=False,
                )
                self.sheet.highlight_cells(
                    row=r,
                    column=c,
                    bg=self.color_unsaved_bg,
                    fg=self.color_unsaved_fg,
                    redraw=False,
                )
            else:
                # restore original status highlight
                self.unsaved_spaces.discard((space, c))
                self.sheet.dehighlight_cells(row=r, column=0, redraw=False)
                self.sheet.dehighlight_cells(row=r, column=1, redraw=False)
                # Status-based highlight on Value column
                self._style_bldgtype_cell(space, r)
                self._style_row_for_status(space, r)

        self.sheet.refresh()
        self._set_idle(f"({len(self.unsaved_spaces)}) modified")

    def _clear_selected_cells(self, event=None):
        """
        User uses Delete key: clear Value cells.
        """
        selected = self.sheet.get_selected_cells()
        self._dbg("_clear_selected_cells selected:", selected)
        for r, c in selected:
            if c != 1:
                continue
            space = self.sheet.get_cell_data(r, 0)
            if not space:
                continue

            current_val = self.sheet.get_cell_data(r, 1)
            if current_val not in ("", None):
                self.sheet.set_cell_data(r, 1, "", redraw=False)

                info = self.merged_spaces.get(space, {})
                orig = info.get("original_resolved", "")

                info["resolved"] = ""

                if "" != orig:
                    self.unsaved_spaces.add(space)
                    self.sheet.highlight_cells(
                        row=r,
                        column=0,
                        bg=self.color_unsaved_bg,
                        fg=self.color_unsaved_fg,
                        redraw=False,
                    )
                    self.sheet.highlight_cells(
                        row=r,
                        column=1,
                        bg=self.color_unsaved_bg,
                        fg=self.color_unsaved_fg,
                        redraw=False,
                    )
                else:
                    self.unsaved_spaces.discard(space)
                    self.sheet.dehighlight_cells(row=r, column=0, redraw=False)
                    self.sheet.dehighlight_cells(row=r, column=1, redraw=False)
                    self._style_row_for_status(space, r)

        self.sheet.refresh()
        return "break"

    @staticmethod
    def _extract_event_payload(event):
        """Tkinter/tksheet helper."""
        if isinstance(event, dict):
            return event
        data = getattr(event, "data", None)
        if isinstance(data, dict):
            return data
        if isinstance(data, str):
            s = data.strip()
            if not s:
                return {}
            try:
                return json.loads(s)
            except Exception:
                try:
                    return ast.literal_eval(s)
                except Exception:
                    return {}
        return {}

    # ------------------------------
    # Guessing logic (works with merged sheet)
    # ------------------------------
    def guess_all_from_names(self):
        """
        Fill guesses into the single 'Value' column.
        Optional confidence column is added when guesses are made.
        """
        total_rows = self.sheet.get_total_rows()
        if total_rows == 0:
            return

        choice = messagebox.askquestion(
            "Guess Behavior",
            "Apply guesses to all rows?\n\n"
            "Yes = Overwrite existing value\n"
            "No = Only fill empty values",
            icon="question",
        )
        overwrite = choice == "yes"

        # Add confidence column if missing
        if not self.confidence_visible:
            # Add header
            headers = list(self.sheet.headers()) + ["Confidence"]
            self.sheet.headers(headers)

            # Expand underlying data to 4 columns
            data = self.sheet.get_sheet_data()
            new_data = []
            for row in data:
                while len(row) < 4:
                    row.append("")
                new_data.append(row)

            self.sheet.set_sheet_data(new_data, redraw=False)

            # Initialize the column
            for r in range(total_rows):
                self.sheet.set_cell_data(r, 3, "", redraw=False)

            self.confidence_visible = True
            self.sheet.refresh()
            self._autosize_columns()

        for r in range(total_rows):
            space = self.sheet.get_cell_data(r, 0)
            if not space:
                continue

            guess, conf = self._guess_space_type(space)
            if not guess:
                # No guess, zero out conf if column exists
                if self.confidence_visible:
                    self.sheet.set_cell_data(r, 3, "", redraw=False)
                continue

            current_val = self.sheet.get_cell_data(r, 2)
            if overwrite or not current_val:
                self.sheet.set_cell_data(r, 2, guess, redraw=False)
                # Mark unsaved
                info = self.merged_spaces.get(space, {})
                orig = info.get("original_resolved", "")
                info["resolved"] = guess
                if guess != orig:
                    self.unsaved_spaces.add(space)
                    self.sheet.highlight_cells(
                        row=r,
                        column=0,
                        bg=self.color_unsaved_bg,
                        fg=self.color_unsaved_fg,
                        redraw=False,
                    )
                    self.sheet.highlight_cells(
                        row=r,
                        column=2,
                        bg=self.color_unsaved_bg,
                        fg=self.color_unsaved_fg,
                        redraw=False,
                    )
                else:
                    self.unsaved_spaces.discard(space)
                    self.sheet.dehighlight_cells(row=r, column=0, redraw=False)
                    self.sheet.dehighlight_cells(row=r, column=2, redraw=False)
                    self._style_row_for_status(space, r)

            # Confidence highlight
            self._apply_confidence_color(r, 3, conf)

        self.sheet.refresh()
        self._autosize_columns()
        self._set_idle("Guesses applied")

    def _normalize_name(self, name: str) -> str:
        """
        Normalize a raw space name so it can be matched to ABBREV_MAP + fuzzy logic.
        (This is your original normalization pipeline.)
        """
        if not name:
            return ""

        s = name.lower()
        s = s.replace("_", " ").replace("-", " ")
        s = re.sub(r"\s+", " ", s).strip()

        # Apply abbreviation expansions
        for pat, repl in ABBREV_MAP.items():
            s = re.sub(pat, repl, s)

        # Fuzzy-correct each token
        tokens = s.split()
        corrected = []
        for token in tokens:
            best = token
            best_dist = 3
            for word in FUZZY_TERMS:
                dist = self._levenshtein(token, word)
                if dist < best_dist:
                    best_dist = dist
                    best = word
            corrected.append(best)

        s = " ".join(corrected)
        s = re.sub(r"\s+", " ", s).strip()

        return s

    def _normalize_target_display(self, target: str) -> str | None:
        """
        Convert target to actual dropdown display text.
        e.g. "OFFICE_OPEN" -> "Office Open"
        """
        if not target:
            return None
        if target in self.space_type_options:
            return target
        canon = target.replace("_", " ").title()
        if canon in self.space_type_options:
            return canon
        return None

    def _guess_space_type(self, space_name: str):
        """
        Full fallback + rule-based + fuzzy guesser.

        Returns:
            (best_display_name:str or None, confidence:int)
        """
        s = self._normalize_name(space_name)
        matches = []

        # --- FALLBACK_MAP keyword matches (your original logic) ---
        for kw, target in FALLBACK_MAP.items():
            if kw in s:
                matches.append((kw, target))

        if matches:
            # Specificity scoring — your original scoring rules
            def specificity_score(kw):
                length_score = len(kw)
                generic_penalty = 0
                if any(
                    g in kw
                    for g in (
                        "hotel",
                        "motel",
                        "dorm",
                        "school",
                        "hospital",
                        "building",
                        "facility",
                    )
                ):
                    generic_penalty = 5
                pos = s.find(kw)
                pos_score = max(0, len(s) - pos)
                return length_score + pos_score - generic_penalty

            best_kw, best_target = max(matches, key=lambda kv: specificity_score(kv[0]))
            final = self._normalize_target_display(best_target)
            if final:
                return final, 100

        # --- SUGGESTION_RULES (weighted hits) ---
        best = (0, -1, None)
        for rule in SUGGESTION_RULES:
            target = self._normalize_target_display(rule.get("target"))
            if not target:
                continue

            score = rule.get("weight", 0)

            # all-must-hit
            if not all(k in s for k in rule.get("all", [])):
                continue
            # exclude if any forbidden
            if any(k in s for k in rule.get("none", [])):
                continue

            # any
            any_hits = sum(1 for k in rule.get("any", []) if k in s)
            # phrases
            phrase_hits = sum(1 for ph in rule.get("phrases", []) if ph in s)

            # If no signals, skip
            if not rule.get("all") and any_hits == 0 and phrase_hits == 0:
                continue

            score += any_hits + (phrase_hits * 2)

            if score > best[0] or (score == best[0] and phrase_hits > best[1]):
                best = (score, phrase_hits, target)

        if best[2]:
            score_norm = min(100, max(50, best[0] * 7))
            return best[2], score_norm

        # --- Nothing matched ---
        return None, 0

    # ------------------------------
    # Confidence coloring
    # ------------------------------
    def _apply_confidence_color(self, row, col, conf):
        conf = int(conf or 0)
        if conf >= 85:
            bg = "#c8e6c9"  # green
        elif conf >= 60:
            bg = "#fff3cd"  # soft yellow
        elif conf >= 30:
            bg = "#ffcc80"  # orange-ish
        else:
            bg = "#ef9a9a"  # red-ish
        fg = "#000000"
        self.sheet.set_cell_data(row, col, str(conf), redraw=False)
        self.sheet.highlight_cells(row=row, column=col, bg=bg, fg=fg, redraw=False)

    # ------------------------------
    # Save / Export / Import (merged-sheet)
    # ------------------------------
    def save_data(self):
        self._dbg(
            "save_data() unsaved_spaces=",
            len(self.unsaved_spaces),
            "unsaved_climate_zone=",
            self.unsaved_climate_zone,
        )

        # Nothing to save
        if not self.unsaved_spaces and not self.unsaved_climate_zone:
            self.status_var.set("No changes to save")
            return

        # -------------------------
        # CLIMATE ZONE
        # -------------------------
        merged_cz = (self.merged_cz_runtime or "").strip()

        file_to_edits = {}

        # Store per-file CZ edits
        for fp in self.model_files:
            orig = self.climate_zone_values.get(fp, "")
            if merged_cz != orig:
                edits = []
                if merged_cz:
                    m = re.match(r"^CZ(\d)([ABC])?$", merged_cz, flags=re.I)
                    if m:
                        num = int(m.group(1))
                        letter = m.group(2)

                        # C-901-CZ-NUMBER
                        edits.append(
                            INPEdits(
                                unique_id=self.site_uid_map.get(fp),
                                change_type="modify",
                                keyword="C-901-CZ-NUMBER",
                                value=str(num),
                                command="",
                            )
                        )
                        # C-901-CZ-LETTER
                        if letter:
                            letter_num = self.cz_letter_rev[letter.upper()]
                            edits.append(
                                INPEdits(
                                    unique_id=self.site_uid_map.get(fp),
                                    change_type="modify",
                                    keyword="C-901-CZ-LETTER",
                                    value=str(letter_num),
                                    command="",
                                )
                            )
                        else:
                            edits.append(
                                INPEdits(
                                    unique_id=self.site_uid_map.get(fp),
                                    change_type="restore_default",
                                    keyword="C-901-CZ-LETTER",
                                    value="",
                                    command="",
                                )
                            )
                else:
                    # Clear to defaults
                    edits.append(
                        INPEdits(
                            unique_id=self.site_uid_map.get(fp),
                            change_type="restore_default",
                            keyword="C-901-CZ-NUMBER",
                            value="",
                            command="",
                        )
                    )
                    edits.append(
                        INPEdits(
                            unique_id=self.site_uid_map.get(fp),
                            change_type="restore_default",
                            keyword="C-901-CZ-LETTER",
                            value="",
                            command="",
                        )
                    )
                file_to_edits.setdefault(fp, []).extend(edits)

        # -------------------------
        # SPACE-TYPE ASSIGNMENTS
        # -------------------------
        data = self.sheet.get_sheet_data()
        for r, row in enumerate(data):
            if r >= len(data):
                break
            space = row[0]
            info = self.merged_spaces.get(space, {})
            orig = info.get("original_resolved", "")
            new_val = info.get("resolved", "") or ""

            new_bldg = info["bldgtype_resolved"]
            orig_bldg = info["bldgtype_original"]

            if space not in self.unsaved_spaces:
                continue

            if new_bldg != orig_bldg:
                for fp in info["exists_in"]:
                    edits = []

                    if new_bldg:
                        val = str(self.building_display_to_key[new_bldg])
                        edits.append(
                            INPEdits(
                                unique_id=space,
                                change_type="modify",
                                keyword="C-901-BLDG-TYPE",
                                value=val,
                            )
                        )
                    else:
                        edits.append(
                            INPEdits(
                                unique_id=space,
                                change_type="restore_default",
                                keyword="C-901-BLDG-TYPE",
                            )
                        )

                    file_to_edits.setdefault(fp, []).extend(edits)

            # Apply only to models where space exists
            for fp in info["exists_in"]:
                edits = []

                if new_val != "":
                    # convert back to key
                    if new_val not in self.space_type_display_to_key:
                        print(f"WARNING: Unknown space type '{new_val}'", flush=True)
                        continue
                    val = str(self.space_type_display_to_key[new_val])
                    edits.append(
                        INPEdits(
                            unique_id=space,
                            change_type="modify",
                            keyword="C-901-OCC-TYPE",
                            value=val,
                            command="",
                        )
                    )
                else:
                    edits.append(
                        INPEdits(
                            unique_id=space,
                            change_type="restore_default",
                            keyword="C-901-OCC-TYPE",
                            value="",
                            command="",
                        )
                    )

                file_to_edits.setdefault(fp, []).extend(edits)

        # -------------------------
        # Write to disk (threaded)
        # -------------------------
        self._set_busy("Saving…")
        threading.Thread(
            target=self._save_worker, args=(file_to_edits,), daemon=True
        ).start()

    def _save_worker(self, file_to_edits):
        errors = []
        for fp, edits in file_to_edits.items():
            try:
                self._dbg("_save_worker applying edits to", fp)
                ModelInputEditor.edit_inp_file(fp, edits)
            except Exception as e:
                errors.append(f"{fp}: {e}")
        self.after(0, partial(self._finish_save, errors))

    def _finish_save(self, errors):
        if errors:
            for e in errors:
                print("Save error:", e, flush=True)
            self._set_idle("Save finished with errors")
            return

        # Update original CZ
        for fp in self.model_files:
            self.climate_zone_values[fp] = self.merged_cz_runtime or ""

        # Update original per-space values
        for space, info in self.merged_spaces.items():
            new_val = info.get("resolved", "")
            info["original_resolved"] = new_val
            info["bldgtype_original"] = info["bldgtype_resolved"]

        # Clear unsaved + restore row status styles
        for r in range(self.sheet.get_total_rows()):
            space = self.sheet.get_cell_data(r, 0)
            info = self.merged_spaces.get(space, {})
            self.sheet.dehighlight_cells(row=r, column=0, redraw=False)
            self.sheet.dehighlight_cells(row=r, column=1, redraw=False)
            self._style_row_for_status(space, r)

        self.unsaved_spaces.clear()
        self.unsaved_climate_zone = False
        if self.cz_label:
            merged_cz, status = self._resolve_merged_climate_zone()
            self._style_cz_label_for_status(status)

        self.sheet.refresh()
        self._autosize_columns()
        self._set_idle("All changes saved")

    # ------------------------------
    # Export / Import (merged)
    # ------------------------------
    def export_to_excel(self):
        self._dbg("export_to_excel()")
        if not self.model_files:
            return

        default_name = "SpaceTypes.xlsx"
        fpath = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            initialfile=default_name,
            filetypes=[("Excel Files", "*.xlsx")],
        )
        if not fpath:
            return

        data = self.sheet.get_sheet_data()
        headers = self.sheet.headers()

        wb = Workbook()
        ws = wb.active
        ws.title = "Space Types"

        # Headers
        for c, header in enumerate(headers, start=1):
            cell = ws.cell(row=1, column=c, value=header)
            cell.font = Font(bold=True)

        # Data
        for r, row in enumerate(data, start=2):
            for c, cell_value in enumerate(row, start=1):
                ws.cell(row=r, column=c, value=cell_value)

        # Dropdown for Value column
        dv_list = ",".join(self.space_type_options)
        dv = DataValidation(type="list", formula1=f'"{dv_list}"', allow_blank=True)
        last_row = len(data) + 1
        dv.add(f"B2:B{last_row}")
        ws.add_data_validation(dv)

        # Autosize
        for col in range(1, ws.max_column + 1):
            max_len = 0
            col_letter = get_column_letter(col)
            for row in ws.iter_rows(
                min_row=1, max_row=ws.max_row, min_col=col, max_col=col
            ):
                v = row[0].value
                if v is not None:
                    max_len = max(max_len, len(str(v)))
            ws.column_dimensions[col_letter].width = max_len + 2

        ws.auto_filter.ref = ws.dimensions
        ws.freeze_panes = "B2"

        wb.save(fpath)

        try:
            if sys.platform.startswith("win"):
                os.startfile(fpath)
            elif sys.platform == "darwin":
                subprocess.call(["open", fpath])
            else:
                subprocess.call(["xdg-open", fpath])
        except Exception as e:
            print(f"Could not auto-open Excel file: {e}", flush=True)

        self.status_var.set(f"Exported → {Path(fpath).name}")

    def import_from_excel(self):
        self._dbg("import_from_excel()")
        if not self.model_files:
            messagebox.showerror("Error", "No space data loaded yet.")
            return

        path = filedialog.askopenfilename(filetypes=[("Excel Files", "*.xlsx")])
        if not path:
            return

        try:
            wb = load_workbook(path)
            ws = wb.active
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open Excel file:\n{e}")
            return

        sheet_headers = self.sheet.headers()
        excel_headers = [cell.value for cell in ws[1]]

        if sheet_headers != excel_headers:
            self._dbg("  header mismatch:", sheet_headers, "vs", excel_headers)
            messagebox.showwarning(
                "Header Mismatch",
                "Column headers in Excel do not match current sheet.\nImport may skip unknown columns.",
            )

        for row_idx in range(2, ws.max_row + 1):
            space = ws.cell(row=row_idx, column=1).value
            if not space:
                continue

            # Find row
            row_in_sheet = self._find_row(space)
            if row_in_sheet < 0:
                continue

            # Excel column 3 = Space Type
            new_val = ws.cell(row=row_idx, column=3).value or ""
            new_val = str(new_val).strip()

            info = self.merged_spaces.get(space, {})
            orig = info.get("original_resolved", "")

            info["resolved"] = new_val

            # Sheet column 2 = Space Type
            self.sheet.set_cell_data(row_in_sheet, 2, new_val, redraw=False)

            if new_val != orig:
                self.unsaved_spaces.add((space, 2))
                self.sheet.highlight_cells(
                    row=row_in_sheet,
                    column=0,
                    bg=self.color_unsaved_bg,
                    fg=self.color_unsaved_fg,
                    redraw=False,
                )
                self.sheet.highlight_cells(
                    row=row_in_sheet,
                    column=2,
                    bg=self.color_unsaved_bg,
                    fg=self.color_unsaved_fg,
                    redraw=False,
                )
            else:
                self.unsaved_spaces.discard((space, 2))
                self.sheet.dehighlight_cells(row=row_in_sheet, column=0, redraw=False)
                self.sheet.dehighlight_cells(row=row_in_sheet, column=2, redraw=False)
                self._style_row_for_status(space, row_in_sheet)

        self.sheet.refresh()
        self._autosize_columns()
        self.status_var.set("Import complete.")

    # ------------------------------
    # Generic helpers
    # ------------------------------
    def _find_row(self, space):
        data = self.sheet.get_sheet_data()
        for i, row in enumerate(data):
            if row and row[0] == space:
                return i
        return -1

    def _autosize_columns(self):
        """
        Stable autosize for tksheet columns.
        Must run both immediately and after idle to ensure layout is ready.
        """

        def _apply():
            try:
                headers = self.sheet.headers()
            except Exception:
                return

            total_cols = len(headers)
            data = self.sheet.get_sheet_data()

            # Compute max width per column
            max_widths = [0] * total_cols

            # Header widths
            for c, h in enumerate(headers):
                max_widths[c] = max(max_widths[c], self._text_pixel_width(h))

            # Cell widths
            for row in data:
                for c, val in enumerate(row):
                    max_widths[c] = max(max_widths[c], self._text_pixel_width(str(val)))

            # Dropdown options
            if total_cols > 1:
                max_widths[1] = max(max_widths[1], self._max_building_type_width())
            if total_cols > 2:
                max_widths[2] = max(max_widths[2], self._max_space_type_width())

            # Add padding so dropdown arrows aren't clipped
            max_widths = [w + 24 for w in max_widths]

            # Set widths with redraw=True so they commit
            for c, w in enumerate(max_widths):
                try:
                    self.sheet.column_width(column=c, width=w, redraw=True)
                except Exception:
                    pass

            self.sheet.refresh()

        # 1. Apply now
        _apply()

        # 2. Apply again once UI is fully drawn
        self.after_idle(_apply)

    def _reset_sheet(self):
        self.sheet.headers(["Space Name", "Building Type", "Space Type"])
        self.sheet.set_sheet_data([], reset_col_positions=True)
        self.sheet.refresh()
        self.guess_button.configure(state="disabled")
        self.export_button.configure(state="disabled")
        self.import_button.configure(state="disabled")
        self.save_button.configure(state="disabled")

    # ------------------------------
    # Busy/Idle state
    # ------------------------------
    def _set_busy(self, msg):
        self._dbg("BUSY:", msg)
        self.status_var.set(msg)

    def _set_idle(self, msg="Idle"):
        self._dbg("IDLE:", msg)
        self.status_var.set(msg)
