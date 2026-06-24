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


class EvaluationSummaryPanel(ctk.CTkFrame):
    """
    Summarize Evaluation View
    Generates an evaluation-only HTML report using summarize_evaluations()
    """

    def __init__(self, parent, controller, main_app):
        super().__init__(parent)
        self.controller = controller
        self.main_app = main_app

        self.grid_columnconfigure(0, weight=1)

        # --- Title ---
        ctk.CTkLabel(
            self,
            text="Summarize Evaluation",
            font=HEADER_FONT,
            anchor="w",
        ).grid(row=0, column=0, sticky="ew", padx=8, pady=(8, 4))

        # --- Description ---
        ctk.CTkLabel(
            self,
            text=(
                "This summary uses only the Detailed Evaluation Report JSON.\n"
                "Click the button below to generate an HTML evaluation summary and "
                "open it in your default web browser."
            ),
            font=TEXT_FONT,
            anchor="w",
            justify="left",
        ).grid(row=1, column=0, sticky="ew", padx=8, pady=(0, 12))

        # --- Evaluation Report Row ---
        row = ctk.CTkFrame(self)
        row.grid(row=2, column=0, sticky="ew", padx=8, pady=4)
        row.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(row, text="Evaluation Report:", font=LABEL_FONT).grid(
            row=0, column=0, padx=(0, 12)
        )

        self.eval_path_var = ctk.StringVar()
        self.eval_path_label = ctk.CTkLabel(
            row, textvariable=self.eval_path_var, font=TEXT_FONT, anchor="w"
        )
        self.eval_path_label.grid(row=0, column=1, sticky="ew")

        # --- Generate Button ---
        self.run_button = ctk.CTkButton(
            self,
            text="Generate & View Evaluation Summary",
            width=260,
            command=self._generate_clicked,
        )
        self.run_button.grid(row=3, column=0, pady=16)

        self.refresh_panel()

    # ----------------------------------------------------------------------
    def refresh_panel(self):
        path = getattr(self.main_app.data, "active_rct_report_path", "") or ""
        self.eval_path_var.set(
            self.controller._shorten_path(path) if path else "No report selected."
        )

    # ----------------------------------------------------------------------
    def _generate_clicked(self):
        eval_path = getattr(self.main_app.data, "active_rct_report_path", None)

        if not eval_path:
            ErrorWindow(self.controller, "No evaluation report JSON is selected.")
            return

        # HTML output file
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".html")
        tmp_path = Path(tmp.name)
        tmp.close()

        self.run_button.configure(state="disabled", text="Generating...")

        loading = LoadingWindow(self.controller, "Generating evaluation summary...")
        loading.set_progress(0.0)

        def worker():
            try:
                # Run evaluation summary generator
                gen = SummaryReportGenerator(
                    detailed_evaluation_report_file_path=eval_path,
                    rpd_file_paths=[],  # Not needed
                    output_file_path=str(tmp_path),
                )
                gen.summarize_evaluations()

                self.after(0, lambda: webbrowser.open(tmp_path.as_uri(), new=2))

            except Exception:
                tb = traceback.format_exc()
                self.after(
                    0, lambda: ErrorWindow(self.controller, f"Summary failed:\n\n{tb}")
                )

            finally:
                self.after(0, loading.close)
                self.after(
                    0,
                    lambda: self.run_button.configure(
                        state="normal", text="Generate & View Evaluation Summary"
                    ),
                )

        threading.Thread(target=worker, daemon=True).start()
