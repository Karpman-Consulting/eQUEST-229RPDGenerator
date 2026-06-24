import customtkinter as ctk
import threading
import tempfile
import webbrowser
import traceback
from pathlib import Path

from rctreportviewer.main import SummaryReportGenerator

from interface.error_window import ErrorWindow
from interface.loading_window import LoadingWindow
from interface.constants import HEADER_FONT, LABEL_FONT, TEXT_FONT


class ModelSummaryPanel(ctk.CTkFrame):
    """
    Summarize Model View
    Uses ONLY the loaded RPD object stored in main_app.data.rpd.
    No JSON reloading occurs here.
    """

    def __init__(self, parent, controller, main_app):
        super().__init__(parent)

        self.controller = controller
        self.main_app = main_app

        self.grid_columnconfigure(0, weight=1)

        # Title
        ctk.CTkLabel(self, text="Summarize Model", font=HEADER_FONT, anchor="w").grid(
            row=0, column=0, sticky="ew", padx=8, pady=(8, 4)
        )

        # Active RPD row
        row = ctk.CTkFrame(self)
        row.grid(row=2, column=0, sticky="ew", padx=8, pady=(4, 8))
        row.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(row, text="Active RPD:", font=LABEL_FONT).grid(
            row=0, column=0, padx=(0, 8)
        )

        self.rpd_path_var = ctk.StringVar()
        self.rpd_path_label = ctk.CTkLabel(
            row, textvariable=self.rpd_path_var, font=TEXT_FONT, anchor="w"
        )
        self.rpd_path_label.grid(row=0, column=1, sticky="ew")

        # Model Types
        types_frame = ctk.CTkFrame(self)
        types_frame.grid(row=3, column=0, sticky="nsew", padx=8, pady=8)
        types_frame.grid_columnconfigure(0, weight=1)
        types_frame.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(
            types_frame, text="Model Types in RPD:", font=LABEL_FONT, anchor="w"
        ).grid(row=0, column=0, sticky="ew")

        self.types_text = ctk.CTkTextbox(types_frame, font=TEXT_FONT, height=140)
        self.types_text.grid(row=1, column=0, sticky="nsew")

        # Generate button
        self.run_button = ctk.CTkButton(
            self, text="Generate & View Model Summary", command=self._generate_clicked
        )
        self.run_button.grid(row=4, column=0, pady=16)

        self.refresh_panel()

    # ------------------------------------------------------------------
    def refresh_panel(self):
        """Refresh RPD path text + model types from loaded RPD object."""
        path = getattr(self.main_app.data, "active_rpd_path", "") or ""
        self.rpd_path_var.set(
            self.controller._shorten_path(path) if path else "No RPD selected."
        )

        self._load_model_types()

    # ------------------------------------------------------------------
    def _load_model_types(self):
        """Use self.main_app.data.rpd to populate the model types textbox."""

        self.types_text.configure(state="normal")
        self.types_text.delete("1.0", "end")

        rpd = getattr(self.main_app.data, "rpd", None)

        if not rpd:
            self.types_text.insert("end", "No RPD loaded.")
            self.types_text.configure(state="disabled")
            return

        ds = getattr(rpd, "rpd_data_structure", None)

        if not ds or "ruleset_model_descriptions" not in ds:
            self.types_text.insert("end", "Invalid or empty RPD structure.")
            self.types_text.configure(state="disabled")
            return

        rmds = ds["ruleset_model_descriptions"]

        if not rmds:
            self.types_text.insert("end", "No model descriptions found.")
            self.types_text.configure(state="disabled")
            return

        # Extract all unique model types
        seen = set()
        for rmd in rmds:
            t = rmd.get("type")
            if t and t not in seen:
                seen.add(t)
                self.types_text.insert("end", f"• {t}\n")

        self.types_text.configure(state="disabled")

    # ------------------------------------------------------------------
    def _generate_clicked(self):
        """Run SummaryReportGenerator.summarize_models() using RPD from memory."""
        rpd_path = getattr(self.main_app.data, "active_rpd_path", None)

        if not rpd_path:
            ErrorWindow(self.controller, "No RPD selected.")
            return

        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".html")
        tmp_path = Path(tmp.name)
        tmp.close()

        self.run_button.configure(state="disabled", text="Generating...")
        loading = LoadingWindow(self.controller, "Generating model summary...")
        loading.set_progress(0.0)

        def worker():
            try:
                gen = SummaryReportGenerator(
                    detailed_evaluation_report_file_path="",
                    rpd_file_paths=[rpd_path],
                    output_file_path=str(tmp_path),
                )
                gen.summarize_models()

                self.after(0, lambda: webbrowser.open(tmp_path.as_uri(), new=2))

            except Exception:
                tb = traceback.format_exc()
                self.after(
                    0,
                    lambda: ErrorWindow(self.controller, f"Summary failed:\n\n{tb}"),
                )

            finally:
                self.after(0, loading.close)
                self.after(
                    0,
                    lambda: self.run_button.configure(
                        state="normal", text="Generate & View Model Summary"
                    ),
                )

        threading.Thread(target=worker, daemon=True).start()
