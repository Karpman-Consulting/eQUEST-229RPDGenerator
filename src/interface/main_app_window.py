import customtkinter as ctk
import threading
from tkinter import filedialog
from pathlib import Path
from rct229.utils.file import deserialize_rpd_file

from rpd_generator.artifacts.ruleset_project_description import (
    RulesetProjectDescription,
)
from rpd_generator.doe2_file_io.model_input_reader import ModelInputReader
from interface.panel_assignments import RulesetValuesPanel
from interface.panel_generate_rpd import GenerateRPDPanel
from interface.panel_systems import BaselineSystemTypesPanel
from interface.panel_rct import RCTPanel
from interface.panel_evaluation_summary import EvaluationSummaryPanel
from interface.panel_model_summary import ModelSummaryPanel
from interface.CTkToolTip import CTkToolTip
from interface.error_window import ErrorWindow
from interface.constants import *


RULESET_MODEL_MATRIX = {
    "ASHRAE 90.1-2019 PRM": [
        # Optional Design model
        "Design",
        # Required
        "Proposed",
        "Baseline",
        # Optional rotated baselines
        "Baseline 90",
        "Baseline 180",
        "Baseline 270",
    ],
    "None": ["Design"],  # single INP selection
}

STATUS_MISSING = "missing"
STATUS_OK = "ok"
STATUS_ISSUES = "issues"  # warnings/errors associated
STATUS_OPTIONAL = "optional"

NAV_ACTIVE_FG = "#E8E8E8"
NAV_ACTIVE_TEXT = "#1A1A1A"
NAV_ACTIVE_FONT = (NAV_FONT[0], NAV_FONT[1], "bold")

STATUS_ICON = {
    STATUS_MISSING: "⛔",
    STATUS_OPTIONAL: "⚪",
    STATUS_OK: "✅",
    STATUS_ISSUES: "⚠️",
}

STATUS_COLOR = {
    STATUS_MISSING: "#d9534f",  # red
    STATUS_OPTIONAL: "#808080",  # default/gray
    STATUS_OK: "#5cb85c",  # green
    STATUS_ISSUES: "#f0ad4e",  # yellow
}

RIGHT_PANEL_WIDTH = 320


class MainAppWindow(ctk.CTkToplevel):
    """
    Redesign highlights
    -------------------
    • Two panels: LEFT = tools/work area, RIGHT = file manager.
    • Ruleset dropdown lives ABOVE the right panel.
    • File paths are NOT shown in the main area. Instead, each model row in
      the right panel shows a status icon+color and a button:
        - If no file selected → "Select INP" (opens file dialog)
        - If selected → "View/Change" (opens a small details dialog that shows
          the full path and lets user change it)
    • Proposed & Baseline are REQUIRED for ASHRAE 90.1-2019 PRM. Design and
      Baseline rotations are optional. For "None" only one Design INP appears.
    • Top of LEFT panel: sticky row of buttons (acts like tabs):
        [Generate RPD] [Assign Space Types] [Assign Climate Zone]
      Clicking switches the content below; the right panel does not change.
    • The right panel also manages RPD file selection and displays the current
      RPD path; RPD can be generated (left) or selected (right).
    • Rotation exception and "Proposed=Design" checkboxes are removed.
    • The window defaults to a slimmer width.
    """

    def __init__(self, main_app):
        super().__init__()
        self.main_app = main_app
        self.title("Karpman Consulting Ruleset Compliance Toolkit")
        self.geometry("1520x920")
        self.minsize(1120, 720)

        # State
        self.current_view = None
        self.main_app.data.ruleset_model_file_paths = {
            ruleset: {} for ruleset in RULESET_MODEL_MATRIX
        }
        self._model_status = {ruleset: {} for ruleset in RULESET_MODEL_MATRIX}

        # Selected ruleset StringVar already lives on main_app.data.selected_ruleset
        if not self.main_app.data.selected_ruleset.get():
            self.main_app.data.selected_ruleset.set("ASHRAE 90.1-2019 PRM")

        # Error/Loading windows
        self.progress_window = None
        self.error_window = None

        # Layout: 2 main columns → LEFT work area and RIGHT file manager
        self.grid_columnconfigure(0, weight=1)  # left side grows
        self.grid_columnconfigure(1, weight=0)  # separator column (no stretch)
        self.grid_columnconfigure(
            2, weight=0, minsize=RIGHT_PANEL_WIDTH
        )  # right side fixed width
        self.grid_rowconfigure(2, weight=1)

        # Layout: LEFT | SEPARATOR | RIGHT
        self.grid_columnconfigure(0, weight=1)  # left grows
        self.grid_columnconfigure(1, weight=0)  # separator
        self.grid_columnconfigure(
            2, weight=0, minsize=RIGHT_PANEL_WIDTH
        )  # right panel fixed

        # Row structure
        self.grid_rowconfigure(2, weight=1)  # content row grows

        # --- TOP NAV BAR ---
        self._build_nav()

        # --- HORIZONTAL SEPARATOR BELOW NAV ---
        self.horz_separator = ctk.CTkFrame(self, height=2, fg_color="#8A8A8A")
        self.horz_separator.grid(
            row=1, column=0, columnspan=3, sticky="ew", padx=0, pady=0
        )

        # --- VERTICAL SEPARATOR (between columns 0 and 2) ---
        self.vert_separator = ctk.CTkFrame(self, width=2, fg_color="#8A8A8A")
        self.vert_separator.grid(row=2, column=1, sticky="ns", padx=0, pady=0)

        # --- LEFT PANEL ---
        self.left_panel = ctk.CTkFrame(self)
        self.left_panel.grid(row=2, column=0, sticky="nsew", padx=4, pady=4)
        self.left_panel.grid_columnconfigure(0, weight=1)
        self.left_panel.grid_rowconfigure(1, weight=1)
        self._build_left_views()

        # --- RIGHT PANEL ---
        self.right_panel = ctk.CTkFrame(self)
        self.right_panel.grid(row=2, column=2, sticky="nsew", padx=4, pady=4)
        self.right_panel.grid_columnconfigure(0, weight=1)
        self._build_right_panel()

        # Initialize applicability for tools that rely on model list
        self._refresh_applicability()
        self._refresh_nav_button_states()

    def _build_nav(self):
        nav = ctk.CTkFrame(self)
        nav.grid(row=0, column=0, sticky="ew", padx=4, pady=(0, 4), columnspan=3)
        nav.grid_columnconfigure((0, 1, 2), weight=1, uniform="nav")

        # Distinct normal colors
        self.NAV_NORMAL_COLORS = {
            "assignments": "#2F7F77",  # deep emerald
            "systems": "#D1A14A",  # golden ochre
            "generate": "#D66A5D",  # warm coral
            "rct": "#4F6FB5",  # royal blue
            "eval_summary": "#8B5FA7",  # mulberry purple
            "model_summary": "#738C94",  # slate graphite
        }

        self.NAV_HOVER_COLORS = {
            "assignments": "#25645E",  # darker emerald
            "systems": "#B7873E",  # darker ochre
            "generate": "#B1554C",  # darker coral
            "rct": "#3E5B99",  # darker royal blue
            "eval_summary": "#6F4D84",  # darker mulberry
            "model_summary": "#5D7178",  # darker slate graphite
        }

        # Construct buttons
        self.nav_buttons = {
            "assignments": ctk.CTkButton(
                nav,
                text="Assign Ruleset Values",
                command=lambda: self._show_view("assignments"),
                fg_color=self.NAV_NORMAL_COLORS["assignments"],
                hover_color=self.NAV_HOVER_COLORS["assignments"],
            ),
            "generate": ctk.CTkButton(
                nav,
                text="Generate RPD",
                command=lambda: self._show_view("generate"),
                fg_color=self.NAV_NORMAL_COLORS["generate"],
                hover_color=self.NAV_HOVER_COLORS["generate"],
            ),
            "systems": ctk.CTkButton(
                nav,
                text="Check 90.1 Baseline Systems",
                command=lambda: self._show_view("systems"),
                fg_color=self.NAV_NORMAL_COLORS["systems"],
                hover_color=self.NAV_HOVER_COLORS["systems"],
                state="disabled",
            ),
            "rct": ctk.CTkButton(
                nav,
                text="Run RCT",
                command=lambda: self._show_view("rct"),
                fg_color=self.NAV_NORMAL_COLORS["rct"],
                hover_color=self.NAV_HOVER_COLORS["rct"],
                state="disabled",
            ),
            "eval_summary": ctk.CTkButton(
                nav,
                text="Summarize Evaluation",
                command=lambda: self._show_view("eval_summary"),
                fg_color=self.NAV_NORMAL_COLORS["eval_summary"],
                hover_color=self.NAV_HOVER_COLORS["eval_summary"],
                state="disabled",
            ),
            "model_summary": ctk.CTkButton(
                nav,
                text="Summarize Model",
                command=lambda: self._show_view("model_summary"),
                fg_color=self.NAV_NORMAL_COLORS["model_summary"],
                hover_color=self.NAV_HOVER_COLORS["model_summary"],
                state="disabled",
            ),
        }

        # Layout (2×3 grid)
        self.nav_buttons["assignments"].grid(
            row=0, column=0, padx=8, pady=8, sticky="ew"
        )
        self.nav_buttons["generate"].grid(row=0, column=1, padx=8, pady=8, sticky="ew")
        self.nav_buttons["model_summary"].grid(
            row=0, column=2, padx=8, pady=8, sticky="ew"
        )

        self.nav_buttons["systems"].grid(row=1, column=0, padx=8, pady=8, sticky="ew")
        self.nav_buttons["rct"].grid(row=1, column=1, padx=8, pady=8, sticky="ew")
        self.nav_buttons["eval_summary"].grid(
            row=1, column=2, padx=8, pady=8, sticky="ew"
        )

    def _set_active_nav(self, active_key: str):
        """Update nav button styles to reflect active section."""
        for key, btn in self.nav_buttons.items():
            if key == active_key:
                btn.configure(
                    fg_color=self.NAV_HOVER_COLORS[key],
                    border_width=3,
                    border_color="#000000",  # thick black border
                    font=(NAV_FONT[0], NAV_FONT[1], "bold"),
                )
            else:
                btn.configure(
                    fg_color=self.NAV_NORMAL_COLORS[key],
                    border_width=0,
                    font=(NAV_FONT[0], NAV_FONT[1]),
                )

    # ------------------------------------------------------------------
    # LEFT SIDE
    # ------------------------------------------------------------------

    def _build_left_views(self):
        # Stacked frames for views
        self.views_container = ctk.CTkFrame(self.left_panel)
        self.views_container.grid(row=1, column=0, sticky="nsew", padx=4, pady=(2, 8))
        self.views_container.grid_columnconfigure(0, weight=1)
        self.views_container.grid_rowconfigure(0, weight=1)

        # --- Instructions View (shown until required INPs are selected) ---
        self.view_instructions = ctk.CTkFrame(self.views_container)
        self.view_instructions.grid_columnconfigure(0, weight=1)
        self.view_instructions.grid_rowconfigure(0, weight=1)

        instructions = (
            "Welcome to the Ruleset Compliance Toolkit.\n\n"
            "Before using any tools, you must select the required files in the right panel:\n"
            "  • Assign Ruleset Values - Proposed and Baseline INP are required.\n"
            "  • Generate RPD - Proposed and Baseline INP are required.\n"
            "  • Summarize Model - RPD is required.\n"
            "  • Check 90.1 Baseline Systems - RPD is required.\n"
            "  • Run RCT - RPD is required.\n"
            "  • Summarize Evaluation - Detailed Evaluation Report is required.\n\n"
            "Once the required files are selected, tools and\n"
            "navigation options will automatically unlock."
        )

        ctk.CTkLabel(
            self.view_instructions,
            text=instructions,
            font=TEXT_FONT,
            justify="left",
        ).pack(padx=20, pady=20, anchor="nw")

        # --- Generate RPD view ---
        self.view_generate = GenerateRPDPanel(
            self.views_container, controller=self, main_app=self.main_app
        )

        # Embed the Space Types panel
        self.view_assignments = ctk.CTkFrame(self.views_container)
        self.view_assignments.grid_columnconfigure(0, weight=1)
        self.view_assignments.grid_rowconfigure(0, weight=1)

        # The actual content panel inside it
        self.space_panel = RulesetValuesPanel(self.view_assignments, self.main_app)
        self.space_panel.grid(row=0, column=0, sticky="nsew")

        # --- Systems Check View ---
        self.view_systems = BaselineSystemTypesPanel(
            self.views_container, self.main_app
        )

        # --- Run RCT ---
        self.view_rct = RCTPanel(
            self.views_container, controller=self, main_app=self.main_app
        )

        # --- Evaluation Summary View ---
        self.view_eval = EvaluationSummaryPanel(
            self.views_container, controller=self, main_app=self.main_app
        )

        # --- Model Summary View ---
        self.view_model = ModelSummaryPanel(
            self.views_container, controller=self, main_app=self.main_app
        )

        # Hide all frames initially — only _show_view() should display one
        for view in (
            self.view_generate,
            self.view_assignments,
            self.view_systems,
            self.view_rct,
            self.view_eval,
            self.view_model,
        ):
            view.grid_forget()

        # Start default
        self._show_view("instructions")

    def _show_view(self, which: str):

        self._set_active_nav(which)

        # Hide all view frames
        for child in (
            self.view_generate,
            self.view_assignments,
            self.view_systems,
            self.view_rct,
            self.view_eval,
            self.view_model,
            self.view_instructions,
        ):
            child.grid_forget()

        # Map views
        views = {
            "instructions": self.view_instructions,
            "generate": self.view_generate,
            "assignments": self.view_assignments,
            "systems": self.view_systems,
            "rct": self.view_rct,
            "eval_summary": self.view_eval,
            "model_summary": self.view_model,
        }

        # Show the correct view
        views[which].grid(row=0, column=0, sticky="nsew")

        # Refresh space panel when needed
        if which == "assignments" and hasattr(self, "space_panel"):
            self.space_panel.refresh_from_selection()

        self.current_view = which

    # ------------------------------------------------------------------
    # RIGHT SIDE
    # ------------------------------------------------------------------
    def _build_right_panel(self):
        # Ruleset selector at the very top (above the model manager)
        hdr = ctk.CTkFrame(self.right_panel)
        hdr.grid(row=0, column=0, sticky="ew", padx=4, pady=(8, 0))
        hdr.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(hdr, text="Ruleset:", font=LABEL_FONT, width=80, anchor=E).grid(
            row=0, column=0, padx=(0, 8), pady=4, sticky="ew"
        )
        self.ruleset_dropdown = ctk.CTkOptionMenu(
            hdr,
            values=list(RULESET_MODEL_MATRIX.keys()),
            variable=self.main_app.data.selected_ruleset,
            command=self._on_ruleset_change,
        )
        self.ruleset_dropdown.grid(row=0, column=1, sticky="ew")

        # Model selection/status panel
        self.model_panel = ctk.CTkFrame(self.right_panel)
        self.model_panel.grid(row=1, column=0, sticky="nsew", padx=8, pady=8)
        self.model_panel.grid_columnconfigure(0, weight=1)

        # Initial build of model rows
        self._rebuild_model_rows()

        # RPD manager below Models section of the right panel
        self.rpd_panel = ctk.CTkFrame(self.right_panel)
        self.rpd_panel.grid(row=2, column=0, sticky="ew", padx=8, pady=(0, 8))
        self._compose_rpd_panel()

        # RCT panel at the very bottom of the right panel
        self.rct_panel = ctk.CTkFrame(self.right_panel)
        self.rct_panel.grid(row=3, column=0, sticky="ew", padx=8, pady=(0, 12))
        self._compose_rct_panel()

    def _compose_rpd_panel(self):
        MODELS_BG = "#CFCFCF"

        for w in self.rpd_panel.winfo_children():
            w.destroy()

        # Section Label
        ctk.CTkLabel(self.rpd_panel, text="RPD File:", font=LABEL_FONT, anchor=W).pack(
            fill="x", pady=(6, 2)
        )

        # Row Frame
        row = ctk.CTkFrame(self.rpd_panel, fg_color=MODELS_BG)
        row.pack(fill="x", padx=4, pady=(0, 6))

        self.rpd_path_var = ctk.StringVar(
            value=getattr(self.main_app.data, "active_rpd_path", "")
        )

        # Status Label
        lbl = ctk.CTkLabel(
            row,
            text=self._shorten_path(self.rpd_path_var.get()) or "No RPD",
            anchor=W,
            text_color=(
                STATUS_COLOR[STATUS_OK]
                if self.rpd_path_var.get()
                else STATUS_COLOR[STATUS_OPTIONAL]
            ),
            fg_color=MODELS_BG,
        )
        lbl.pack(side="left", fill="x", expand=True, padx=(6, 8))

        # Select Button
        ctk.CTkButton(row, text="Select RPD", width=110, command=self._select_rpd).pack(
            side="left", padx=6
        )

        # Tooltip if exists
        if self.rpd_path_var.get():
            CTkToolTip(lbl, message=self.rpd_path_var.get())

    def _compose_rct_panel(self):
        MODELS_BG = "#CFCFCF"

        for w in self.rct_panel.winfo_children():
            w.destroy()

        ctk.CTkLabel(
            self.rct_panel, text="RCT Evaluation Report:", font=LABEL_FONT, anchor=W
        ).pack(fill="x", pady=(6, 2))

        row = ctk.CTkFrame(self.rct_panel, fg_color=MODELS_BG)
        row.pack(fill="x", padx=4, pady=(0, 6))

        self.rct_path_var = ctk.StringVar(
            value=getattr(self.main_app.data, "active_rct_report_path", "")
        )

        lbl = ctk.CTkLabel(
            row,
            text=self._shorten_path(self.rct_path_var.get()) or "No Report",
            anchor=W,
            text_color=(
                STATUS_COLOR[STATUS_OK]
                if self.rct_path_var.get()
                else STATUS_COLOR[STATUS_OPTIONAL]
            ),
            fg_color=MODELS_BG,
        )
        lbl.pack(side="left", fill="x", expand=True, padx=(6, 8))

        ctk.CTkButton(
            row, text="Select Report", width=110, command=self._select_rct_report
        ).pack(side="left", padx=6)

        if self.rct_path_var.get():
            CTkToolTip(lbl, message=self.rct_path_var.get())

    def _select_rct_report(self):
        path = filedialog.askopenfilename(
            parent=self, filetypes=[("RCT Evaluation Report", "*.json")]
        )
        if path:
            self.rct_path_var.set(path)
            if hasattr(self.view_rct, "refresh_panel"):
                self.view_rct.refresh_panel()
            self.main_app.data.active_rct_report_path = path
            self._compose_rct_panel()
            self._refresh_nav_button_states()

            if hasattr(self, "view_eval"):
                self.view_eval.refresh_panel()

    def _on_ruleset_change(self, _):
        """Handle when user changes selected ruleset from dropdown."""
        self._rebuild_model_rows()
        self._refresh_applicability()
        self._refresh_nav_button_states()

        # Update Assignments Panel to match new model set
        if hasattr(self, "space_panel"):
            self.space_panel.refresh_from_selection()

    def _refresh_nav_button_states(self):
        """Enable/disable nav buttons based on current state and add tooltips."""

        data = self.main_app.data

        has_rpd = hasattr(data, "active_rpd_path") and bool(data.active_rpd_path)
        has_eval_report = bool(data.active_rct_report_path)
        inp_ready = self._required_models_selected()
        self.view_generate.set_enabled(
            inp_ready and not self._any_model_has_critical_issues()
        )

        # --- Systems Button ---
        if has_rpd:
            self.nav_buttons["systems"].configure(state="normal")
            self._set_disabled_button_tooltip(self.nav_buttons["systems"], None)
        else:
            self.nav_buttons["systems"].configure(state="disabled")
            self._set_disabled_button_tooltip(
                self.nav_buttons["systems"],
                "Requires an RPD.\nGenerate or select an RPD first.",
            )

        # --- Run RCT Button ---
        if has_rpd:
            self.nav_buttons["rct"].configure(state="normal")
            self._set_disabled_button_tooltip(self.nav_buttons["rct"], None)
        else:
            self.nav_buttons["rct"].configure(state="disabled")
            self._set_disabled_button_tooltip(
                self.nav_buttons["rct"],
                "Requires an RPD.\nGenerate or select an RPD first.",
            )

        # --- Summarize Model ---
        if has_rpd:
            self.nav_buttons["model_summary"].configure(state="normal")
            self._set_disabled_button_tooltip(self.nav_buttons["model_summary"], None)
        else:
            self.nav_buttons["model_summary"].configure(state="disabled")
            self._set_disabled_button_tooltip(
                self.nav_buttons["model_summary"],
                "Requires an RPD.\nGenerate or select an RPD first.",
            )

        # --- Summarize Evaluation ---
        if has_eval_report:
            self.nav_buttons["eval_summary"].configure(state="normal")
            self._set_disabled_button_tooltip(self.nav_buttons["eval_summary"], None)
        else:
            self.nav_buttons["eval_summary"].configure(state="disabled")
            self._set_disabled_button_tooltip(
                self.nav_buttons["eval_summary"],
                "Requires a Detailed Evaluation Report from the RCT. Select or run RCT first.",
            )

        # --- Generate RPD Button ---
        # Must have required INPs AND no model issues
        if inp_ready and not self._any_model_has_critical_issues():
            self.nav_buttons["generate"].configure(state="normal")
            self._set_disabled_button_tooltip(self.nav_buttons["generate"], None)
            self.nav_buttons["assignments"].configure(state="normal")
            self._set_disabled_button_tooltip(self.nav_buttons["assignments"], None)
        else:
            self.nav_buttons["generate"].configure(state="disabled")
            self.nav_buttons["assignments"].configure(state="disabled")

            # Identify correct tooltip
            if not inp_ready:
                msg = (
                    "Required INP models not selected.\n"
                    "Proposed and Baseline are required."
                    if self.main_app.data.selected_ruleset.get()
                    == "ASHRAE 90.1-2019 PRM"
                    else "Select the Design INP file to enable RPD generation."
                )
            elif self._any_model_has_critical_issues():
                msg = "Cannot generate RPD until file issues are resolved.\nClick the ⚠ button beside the model for details."
            else:
                msg = None

            self._set_disabled_button_tooltip(self.nav_buttons["generate"], msg)
            self._set_disabled_button_tooltip(self.nav_buttons["assignments"], msg)

    @staticmethod
    def _set_disabled_button_tooltip(button, message: str | None):
        """Attach or remove tooltip for a button."""
        # Remove existing tooltip if present
        if hasattr(button, "_tooltip") and button._tooltip:
            button._tooltip.hide()
            button._tooltip = None

        if message:
            button._tooltip = CTkToolTip(button, message=message)

    def _rebuild_model_rows(self):
        for w in self.model_panel.winfo_children():
            w.destroy()

        ruleset = self.main_app.data.selected_ruleset.get()
        ctk.CTkLabel(self.model_panel, text="Models", font=HEADER_FONT, anchor=W).pack(
            fill="x", pady=(6, 4)
        )

        models = RULESET_MODEL_MATRIX.get(ruleset, ["Design"])
        for m in models:
            self._add_model_row(m)

    def _add_model_row(self, model_name: str):
        MODELS_BG = "#CFCFCF"  # <- your panel color
        ruleset = self.main_app.data.selected_ruleset.get()

        row = ctk.CTkFrame(self.model_panel, fg_color=MODELS_BG)
        row.pack(fill="x", pady=4)

        # label + status icon
        left = ctk.CTkFrame(row, fg_color=MODELS_BG)
        left.pack(side="left", fill="x", expand=True)

        icon, color = self._compute_model_status(model_name)
        lbl = ctk.CTkLabel(
            left,
            text=f"{icon}  {model_name}",
            text_color=color,
            font=TEXT_FONT,
            anchor=W,
            fg_color=MODELS_BG,
            bg_color=MODELS_BG,  # <- REQUIRED so label matches background
        )
        lbl.pack(side="left")

        # Select / View-Change button
        has_file = bool(
            self.main_app.data.ruleset_model_file_paths[ruleset].get(model_name)
        )
        btn_text = "View/Change" if has_file else "Select INP"

        ctk.CTkButton(
            row,
            text=btn_text,
            width=110,
            command=lambda m=model_name: self._open_model_file_dialog(m),
        ).pack(side="left", padx=6)

        # Issues button (disabled unless there are warnings/errors)
        issues = self.main_app.data.model_issues.get(model_name, [])

        issues_btn = ctk.CTkButton(
            row,
            text="⚠",
            width=28,
            height=28,
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color="#FFD400",
            hover=False,
            command=lambda: self._show_model_issues(model_name),
            state="normal" if issues else "disabled",
        )
        issues_btn.pack(side="left", padx=(4, 0))

        if issues:
            CTkToolTip(issues_btn, message="\n".join(issues))

        # Tooltip for file path when available
        path = self.main_app.data.ruleset_model_file_paths[ruleset].get(model_name, "")
        if path:
            CTkToolTip(lbl, message=path)

    # ------------------------------------------------------------------
    # FILE & PATH HELPERS
    # ------------------------------------------------------------------
    def _open_model_file_dialog(self, model_name: str):
        ruleset = self.main_app.data.selected_ruleset.get()
        current = self.main_app.data.ruleset_model_file_paths[ruleset].get(model_name)

        if not current:
            # Simple selection flow
            selected_path = filedialog.askopenfilename(
                parent=self, filetypes=[("eQUEST Input Files", "*.inp")]
            )
            if selected_path:
                self._set_model_path(model_name, selected_path)
        else:
            # Open a tiny details dialog (path + Change)
            dialog = ctk.CTkToplevel(self)
            dialog.title(f"{model_name} model")
            dialog.geometry("640x160")
            dialog.grab_set()

            ctk.CTkLabel(
                dialog,
                text=f"Selected file for {model_name}:",
                font=LABEL_FONT,
                anchor=W,
            ).pack(fill="x", padx=10, pady=(10, 4))
            ctk.CTkLabel(
                dialog, text=current, anchor=W, font=TEXT_FONT, wraplength=600
            ).pack(fill="x", padx=10)

            btn_row = ctk.CTkFrame(dialog)
            btn_row.pack(fill="x", padx=10, pady=10)

            def change():
                new_path = filedialog.askopenfilename(
                    parent=dialog, filetypes=[("eQUEST Input Files", "*.inp")]
                )
                if new_path:
                    self._set_model_path(model_name, new_path)
                    dialog.destroy()

            ctk.CTkButton(btn_row, text="Change", command=change).pack(side="left")
            ctk.CTkButton(btn_row, text="Close", command=dialog.destroy).pack(
                side="right"
            )

    def _set_model_path(self, model_name: str, file_path: str):
        """Load and verify the selected INP file in a background thread."""
        ruleset = self.main_app.data.selected_ruleset.get()

        def worker():
            key = (ruleset, model_name)
            try:
                # Load model (can take time)
                parsed = ModelInputReader.read_inp_files([file_path])[0]
                self.main_app.data.loaded_models[key] = parsed

                # Verify associated output files
                ok, missing = self.verify_associated_files(file_path)
                if ok:
                    self.main_app.data.model_issues.pop(model_name, None)
                else:
                    self.main_app.data.model_issues[model_name] = [
                        f"Missing simulation outputs: {', '.join(missing)}. "
                        "Recommend re-running the simulation."
                    ]

                # Cache path
                self.main_app.data.ruleset_model_file_paths[ruleset][
                    model_name
                ] = file_path

                # Schedule UI updates back on main thread
                self.after(0, self._on_model_load_success, model_name)

            except Exception as e:
                self.main_app.data.model_issues[model_name] = [f"[ERROR] {e}"]
                self.after(
                    0,
                    lambda e=e: self._on_model_load_failure(
                        model_name, f"Failed to load model:\n\n{e}"
                    ),
                )

        # Disable UI feedback quickly while loading
        self._rebuild_model_rows()
        self._refresh_nav_button_states()

        threading.Thread(target=worker, daemon=True).start()

    def _on_model_load_success(self, model_name: str):
        """Called from main thread when model loads successfully."""
        self._rebuild_model_rows()
        if hasattr(self, "space_panel"):
            self.space_panel.refresh_from_selection(from_cache=True)
        self._refresh_nav_button_states()

    def _on_model_load_failure(self, model_name: str, message: str):
        """Called from main thread when model fails to load."""
        self._rebuild_model_rows()
        self._refresh_nav_button_states()
        ErrorWindow(self, error_message=message)

    def _select_rpd(self):
        path = filedialog.askopenfilename(
            parent=self, filetypes=[("RPD JSON", "*.rpd")]
        )
        if not path:
            return

        try:
            # --- Load and assign RPD object ---
            print(f"Loading RPD from: {path}")
            rpd_obj = deserialize_rpd_file(path)

            # Ensure it’s a RulesetProjectDescription object
            if isinstance(rpd_obj, dict):
                # If deserialize_rpd_file returns raw JSON dict, wrap it manually
                rpd = RulesetProjectDescription("Loaded RPD")
                rpd.rpd_data_structure = rpd_obj
            else:
                rpd = rpd_obj
                if not getattr(rpd, "rpd_data_structure", None):
                    # Defensive: if deserializer didn't fill it
                    rpd.rpd_data_structure = getattr(rpd, "data", {})

            # --- Assign to main app data ---
            self.main_app.data.rpd = rpd
            self.main_app.data.active_rpd_path = path

            # Log summary info
            rmds = rpd.rpd_data_structure.get("ruleset_model_descriptions", [])
            print(f"RPD loaded successfully: {len(rmds)} RMDs found.")
            for rmd in rmds:
                print("   -", rmd.get("type", "(unknown)"))

            # --- Update UI ---
            self.rpd_path_var.set(path)
            self._compose_rpd_panel()
            self._refresh_nav_button_states()

            if hasattr(self, "view_model"):
                self.view_model.refresh_panel()

        except Exception as e:
            import traceback

            tb = traceback.format_exc()
            self.raise_error_window(f"❌ Failed to load RPD:\n{e}\n\n{tb}")

    @staticmethod
    def _shorten_path(path: str, max_parts: int = 3) -> str:
        if not path:
            return ""
        p = Path(path)
        parts = list(p.parts)
        if len(parts) <= max_parts:
            return str(p)
        return str(Path(*parts[:1]) / "..." / Path(*parts[-(max_parts - 1) :]))

    def _show_model_issues(self, model_name: str):
        issues = self.main_app.data.model_issues.get(model_name, [])
        if not issues:
            return

        dialog = ctk.CTkToplevel(self)
        dialog.title(f"Issues for {model_name}")
        dialog.geometry("500x240")
        dialog.grab_set()

        ctk.CTkLabel(dialog, text=f"{model_name} Issues:", font=HEADER_FONT).pack(
            pady=(10, 5)
        )
        text = "\n".join(issues)
        ctk.CTkTextbox(dialog, height=140, font=TEXT_FONT).pack(
            fill="both", expand=True, padx=10
        )
        dialog.children[list(dialog.children.keys())[-1]].insert("0.0", text)

        ctk.CTkButton(dialog, text="Close", command=dialog.destroy).pack(pady=10)

    def _any_model_has_critical_issues(self) -> bool:
        """
        Return True only if a model has ERROR-level issues.
        Warnings do not block generation.
        """
        for msgs in self.main_app.data.model_issues.values():
            if any(msg.startswith("[ERROR]") for msg in msgs):
                return True
        return False

    # ------------------------------------------------------------------
    # GENERATION & VALIDATION
    # ------------------------------------------------------------------
    def validate_and_generate(self):
        self.main_app.data.errors = []

        ruleset = self.main_app.data.selected_ruleset.get()
        paths = self.main_app.data.ruleset_model_file_paths[ruleset]

        # Requirements per spec
        if ruleset == "ASHRAE 90.1-2019 PRM":
            required = ["Proposed", "Baseline"]
            for req in required:
                if not paths.get(req):
                    self.main_app.data.errors.append(
                        f"'{req}' model is required for ASHRAE 90.1-2019."
                    )
        else:
            # None → must have one Design
            if not paths.get("Design"):
                self.main_app.data.errors.append(
                    "'Design' model is required for this ruleset."
                )

        # Validate associated files for any selected models
        for model_name, fpath in paths.items():
            if not fpath:
                continue
            if not self.verify_associated_files(fpath):
                self.main_app.data.errors.append(
                    f"Associated simulation output files not found for '{model_name}'."
                )

        # Output directory presence
        if not self.main_app.data.output_directory.get():
            self.main_app.data.errors.append("Please select an output directory.")

        if self.main_app.data.errors:
            self.raise_error_window("\n".join(self.main_app.data.errors))
            return

    def refresh_rpd_panel_after_generation(self):
        # Reflect a newly generated RPD on the right panel
        if self.main_app.data.active_rpd_path:
            self.rpd_path_var.set(self.main_app.data.active_rpd_path)
            self._compose_rpd_panel()
            self._refresh_nav_button_states()

            if hasattr(self, "view_model"):
                self.view_model.refresh_panel()

    def refresh_rct_panel_after_evaluation(self):
        # Reflect a new RCT evaluation on the right panel
        if self.main_app.data.active_rct_report_path:
            self.rct_path_var.set(self.main_app.data.active_rct_report_path)
            self._compose_rct_panel()
            self._refresh_nav_button_states()

            if hasattr(self, "view_eval"):
                self.view_eval.refresh_panel()

    def on_generation_complete(self, success: bool, msg: str = ""):
        self._rebuild_model_rows()
        self._refresh_nav_button_states()
        if success:
            self.main_app.data.errors.clear()
            self.raise_error_window("RPD successfully generated!")
        else:
            self.raise_error_window(msg)

    def on_evaluation_complete(self, success: bool, message: str = ""):
        if success:
            # Update right-side UI with the new report
            self.refresh_rct_panel_after_evaluation()

        self._refresh_nav_button_states()

        if success:
            self.raise_error_window(
                "RCT evaluation completed successfully.\nThe evaluation report has been loaded."
            )
        else:
            self.raise_error_window(f"RCT Evaluation Failed:\n\n{message}")

    def _progress_update(self, msg: str, frac: float):
        if self.progress_window and self.progress_window.winfo_exists():
            self.progress_window.set_message(msg)
            self.progress_window.set_progress(max(0.0, min(1.0, float(frac))))

    def _compute_model_status(self, model_name: str) -> tuple[str, str]:
        """
        Returns (icon, color) for the model status under the selected ruleset.
        """
        ruleset = self.main_app.data.selected_ruleset.get()
        paths = self.main_app.data.ruleset_model_file_paths[ruleset]
        issues = self.main_app.data.model_issues.get(model_name, [])

        required = (
            ruleset == "ASHRAE 90.1-2019 PRM" and model_name in ("Proposed", "Baseline")
        ) or (ruleset == "None" and model_name == "Design")

        file_selected = bool(paths.get(model_name))

        # Priority 1: If we have issue messages
        if issues:
            return "⚠", STATUS_COLOR["issues"]

        # Priority 2: If required but missing
        if required and not file_selected:
            return "🔴", STATUS_COLOR["missing"]

        # Priority 3: If optional and missing
        if not required and not file_selected:
            return "⚪", STATUS_COLOR["optional"]

        # Priority 4: If file selected and no issues
        return "✅", STATUS_COLOR["ok"]

    # ------------------------------------------------------------------
    # APPLICABILITY / MODELS
    # ------------------------------------------------------------------
    def _active_model_types(self) -> list[str]:
        ruleset = self.main_app.data.selected_ruleset.get()
        models = list(RULESET_MODEL_MATRIX.get(ruleset, ["Design"]))
        if ruleset == "None":
            return ["Design"]
        # ASHRAE → keep all; required vs optional enforced elsewhere
        return models

    def _refresh_applicability(self):
        self.main_app.data.set_applicable_models(self._active_model_types())

    def _required_models_selected(self) -> bool:
        """Return True if the minimum required INP models are selected."""
        ruleset = self.main_app.data.selected_ruleset.get()
        paths = self.main_app.data.ruleset_model_file_paths.get(ruleset, {})

        if ruleset == "ASHRAE 90.1-2019 PRM":
            # Both required
            return bool(paths.get("Proposed")) and bool(paths.get("Baseline"))

        elif ruleset == "None":
            # Only one INP needed
            return bool(paths.get("Design"))

        # Fallback safety — should not normally reach here
        return False

    # ------------------------------------------------------------------
    # Utils
    # ------------------------------------------------------------------
    @staticmethod
    def verify_associated_files(file_path: str) -> tuple[bool, list[str]]:
        """
        Returns (ok, missing_files_list)
        """
        file_extensions = [".erp", ".srp", ".lrp", ".nhk"]
        p = Path(file_path)
        base = p.stem
        directory = p.parent
        missing = []

        for ext in file_extensions:
            normal_file = directory / f"{base}{ext}"
            baseline_file = directory / f"{base} - Baseline Design{ext}"
            if not normal_file.is_file() and not baseline_file.is_file():
                missing.append(ext)

        return len(missing) == 0, missing

    def select_output_directory(self):
        directory = filedialog.askdirectory(
            parent=self, title="Select Output Directory"
        )
        if directory:
            self.main_app.data.output_directory.set(directory)

    def raise_error_window(self, error_text: str):
        if not error_text:
            return
        if self.error_window is None or not self.error_window.winfo_exists():
            self.error_window = ErrorWindow(self, error_text)
            self.error_window.after(100, self.error_window.lift, None)
        else:
            self.error_window.focus()
