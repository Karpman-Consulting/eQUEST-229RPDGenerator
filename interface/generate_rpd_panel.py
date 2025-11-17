import customtkinter as ctk
import threading
import traceback
from tkinter import filedialog

from interface.error_window import ErrorWindow
from interface.loading_window import LoadingWindow
from interface.constants import HEADER_FONT, LABEL_FONT, TEXT_FONT

from rpd_generator.artifacts.ruleset_project_description import (
    RulesetProjectDescription,
)


class GenerateRPDPanel(ctk.CTkFrame):
    """
    Generate RPD Panel:
    • Uses INPs selected in the RIGHT panel.
    • Provides Project Name + Output Directory fields.
    • Runs the RPD generation process with progress window.
    """

    def __init__(self, parent, controller, main_app):
        super().__init__(parent)
        self.controller = controller
        self.main_app = main_app

        self.grid_columnconfigure(0, weight=1)

        # ------------------------------------------------------------------
        # Title + description
        # ------------------------------------------------------------------
        ctk.CTkLabel(
            self,
            text="Generate Ruleset Project Description (RPD)",
            font=HEADER_FONT,
            anchor="w",
        ).grid(row=0, column=0, sticky="ew", padx=8, pady=(8, 4))

        ctk.CTkLabel(
            self,
            text=(
                "Uses the Proposed/Baseline INP files selected in the right panel.\n"
                "Specify a Project Name and Output Directory, then click Generate."
            ),
            font=TEXT_FONT,
            anchor="w",
            justify="left",
        ).grid(row=1, column=0, sticky="ew", padx=8, pady=(0, 12))

        # ------------------------------------------------------------------
        # Project Name
        # ------------------------------------------------------------------
        name_row = ctk.CTkFrame(self)
        name_row.grid(row=2, column=0, sticky="ew", padx=8, pady=(4, 12))
        name_row.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(name_row, text="Project Name:", font=LABEL_FONT).grid(
            row=0, column=0, padx=(0, 8)
        )

        self.project_name_entry = ctk.CTkEntry(
            name_row,
            textvariable=self.main_app.data.project_name,
            font=TEXT_FONT,
        )
        self.project_name_entry.grid(row=0, column=1, sticky="ew")

        # ------------------------------------------------------------------
        # Output Directory
        # ------------------------------------------------------------------
        out_row = ctk.CTkFrame(self)
        out_row.grid(row=3, column=0, sticky="ew", padx=8, pady=(4, 12))
        out_row.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(out_row, text="Output Directory:", font=LABEL_FONT).grid(
            row=0, column=0, padx=(0, 8)
        )

        self.out_entry = ctk.CTkEntry(
            out_row,
            textvariable=self.main_app.data.output_directory,
            font=TEXT_FONT,
        )
        self.out_entry.grid(row=0, column=1, sticky="ew")

        ctk.CTkButton(
            out_row,
            text="Browse",
            width=90,
            command=self._choose_output_dir,
        ).grid(row=0, column=2, padx=(8, 0))

        # ------------------------------------------------------------------
        # Generate Button
        # ------------------------------------------------------------------
        self.generate_button = ctk.CTkButton(
            self,
            text="Generate RPD",
            width=200,
            command=self._generate_clicked,
            state="disabled",  # main app will enable when INPs ready
        )
        self.generate_button.grid(row=4, column=0, pady=16)

    # ======================================================================
    # EXTERNAL CONTROL (from MainAppWindow)
    # ======================================================================
    def set_enabled(self, enabled: bool):
        """Called by MainAppWindow to enable/disable Generate button."""
        self.generate_button.configure(state="normal" if enabled else "disabled")

    # ======================================================================
    # UI ACTIONS
    # ======================================================================
    def _choose_output_dir(self):
        d = filedialog.askdirectory(parent=self, title="Select Output Directory")
        if d:
            self.main_app.data.output_directory.set(d)

    def _generate_clicked(self):
        """Validate + run RPD generation thread."""
        data = self.main_app.data

        # Validate project name
        if not data.project_name.get().strip():
            ErrorWindow(self.controller, "Please specify a Project Name.")
            return

        # Validate output directory
        out_dir = data.output_directory.get().strip()
        if not out_dir:
            ErrorWindow(self.controller, "Please select an Output Directory.")
            return

        # Delegate INP validation to existing method
        validator = getattr(self.controller, "validate_and_generate", None)
        if validator:
            validator()
            if data.errors:
                return

        # Disable UI while running
        self.generate_button.configure(state="disabled", text="Generating...")

        # Loading window
        loading = LoadingWindow(self.controller, "Starting RPD Generation...")
        loading.set_progress(0.0)

        # Start background thread
        threading.Thread(
            target=lambda: self._generation_worker(loading),
            daemon=True,
        ).start()

    # ======================================================================
    # WORKER THREAD
    # ======================================================================
    def _generation_worker(self, loading):
        try:
            data = self.main_app.data

            # --------------------------------------------------------------
            # Create the RPD object
            # --------------------------------------------------------------
            data.rpd = RulesetProjectDescription(data.project_name.get())
            data.rpd.populate_data_elements()

            # --------------------------------------------------------------
            # Progress Callback (identical to old report_progress)
            # --------------------------------------------------------------
            def report_progress(done: int, total: int, msg: str):
                frac = 0.75 * (done / total) if total else 0.0
                self.after(
                    0,
                    lambda f=frac, m=msg, d=done, t=total: self._update_loading(
                        loading, f"{m}  ({d}/{t})", f
                    ),
                )

            # --------------------------------------------------------------
            # STEP 1 — Reading models
            # --------------------------------------------------------------
            self._update_loading(loading, "Reading models...", 0.00)
            data.generate_rmd_data(data.rpd, progress_cb=report_progress)

            # --------------------------------------------------------------
            # STEP 2 — Run model checks
            # --------------------------------------------------------------
            self._update_loading(loading, "Running checks...", 0.75)
            data.run_model_checks()

            # --------------------------------------------------------------
            # STEP 3 — Evaluate errors/warnings and write output
            # --------------------------------------------------------------
            if len(data.errors) == 0:
                # If warnings exist → show them (old behavior)
                if len(data.warnings) > 0:
                    warning_msg = (
                        "Warnings were generated during RPD generation:\n\n"
                        + "\n".join(data.warnings)
                    )
                    self.after(0, lambda: ErrorWindow(self.controller, warning_msg))

                # Progress update before writing output
                self._update_loading(loading, "Writing output...", 0.76)

                data.call_write_rpd_json_from_rmds()

                # ----------------------------------------------------------
                # Save generated RPD path
                # ----------------------------------------------------------
                if getattr(data, "last_written_rpd_path", None):
                    data.active_rpd_path = data.last_written_rpd_path
                elif hasattr(data, "get_last_written_rpd_path"):
                    try:
                        data.active_rpd_path = data.get_last_written_rpd_path()
                    except Exception:
                        pass

                self.after(0, self.controller.refresh_rpd_panel_after_generation)

                # ----------------------------------------------------------
                # Complete
                # ----------------------------------------------------------
                self.after(
                    0,
                    lambda: self.controller.on_generation_complete(
                        True, "RPD successfully generated."
                    ),
                )
            else:
                # Generation FAILED
                msg = "\n".join(data.errors)
                self.after(
                    0, lambda: self.controller.on_generation_complete(False, msg)
                )

        except Exception:
            tb = traceback.format_exc()
            self.after(0, lambda: self.controller.on_generation_complete(False, tb))
        finally:
            # Restore UI
            self.after(
                0,
                lambda: (
                    loading.close(),
                    self.generate_button.configure(state="normal", text="Generate RPD"),
                ),
            )

    # ======================================================================
    # HELPERS
    # ======================================================================
    def _update_loading(self, loading, msg, frac):
        def _do_update():
            if not loading.winfo_exists():  # <--- critical safety check
                return
            loading.set_message(msg)
            loading.set_progress(max(0, min(1, frac)))

        self.after(0, _do_update)

    def _fail(self, loading, msg):
        self.after(0, loading.close)
        self.after(
            0, lambda: ErrorWindow(self.controller, f"RPD Generation Failed:\n\n{msg}")
        )
        self.after(
            0,
            lambda: self.generate_button.configure(state="normal", text="Generate RPD"),
        )
