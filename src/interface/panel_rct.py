import customtkinter as ctk
import re
import io
import traceback
import threading
from contextlib import redirect_stdout
from tkinter import filedialog
from pathlib import Path
from rct229.web_application import run_project_evaluation
from rct229.utils.file import deserialize_rpd_file

from interface.error_window import ErrorWindow
from interface.loading_window import LoadingWindow
from interface.constants import HEADER_FONT, LABEL_FONT, TEXT_FONT


class StdoutInterceptor(io.StringIO):
    def __init__(self, on_line):
        super().__init__()
        self.on_line = on_line
        self._buffer = ""

    def write(self, s):
        self._buffer += s
        while "\n" in self._buffer:
            line, self._buffer = self._buffer.split("\n", 1)
            self.on_line(line.rstrip())
        return len(s)


class RCTPanel(ctk.CTkFrame):
    """
    RCT Panel:
    • Uses RPD selected in the RIGHT panel.
    • Provides its own Output Directory field (independent of Generate tab).
    """

    def __init__(self, parent, controller, main_app):
        """
        controller = MainAppWindow instance
        main_app   = MainAppData instance
        """
        super().__init__(parent)
        self.controller = controller  # <-- window / UI controller
        self.main_app = main_app  # <-- shared data

        self.grid_columnconfigure(0, weight=1)

        # Title + description
        ctk.CTkLabel(
            self, text="Run Ruleset Checking Tool (RCT)", font=HEADER_FONT, anchor="w"
        ).grid(row=0, column=0, sticky="ew", padx=8, pady=(8, 4))

        ctk.CTkLabel(
            self,
            text="Uses the selected RPD from the right panel.\n"
            "Select or change the Output Directory below, then run RCT.",
            font=TEXT_FONT,
            anchor="w",
            justify="left",
        ).grid(row=1, column=0, sticky="ew", padx=8, pady=(0, 12))

        # Output Directory Select
        out_row = ctk.CTkFrame(self)
        out_row.grid(row=2, column=0, sticky="ew", padx=8, pady=(4, 12))
        out_row.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(out_row, text="Output Directory:", font=LABEL_FONT).grid(
            row=0, column=0, padx=(0, 8)
        )

        self.output_entry = ctk.CTkEntry(
            out_row,
            textvariable=self.main_app.data.output_directory,
            font=TEXT_FONT,
        )
        self.output_entry.grid(row=0, column=1, sticky="ew")

        ctk.CTkButton(
            out_row, text="Browse", width=90, command=self._choose_output_dir
        ).grid(row=0, column=2, padx=(8, 0))

        # Run Button
        self.run_button = ctk.CTkButton(
            self,
            text="Run RCT Evaluation",
            width=200,
            command=self._run_rct_clicked,
        )
        self.run_button.grid(row=3, column=0, pady=16)

    # ------------------------------------------------------------------
    # UI ACTIONS
    # ------------------------------------------------------------------
    def _choose_output_dir(self):
        directory = filedialog.askdirectory(
            parent=self, title="Select Output Directory"
        )
        if directory:
            self.main_app.data.output_directory.set(directory)

    def _run_rct_clicked(self):
        data = self.main_app.data

        if not getattr(data, "active_rpd_path", None):
            ErrorWindow(
                self.controller,
                "No RPD selected.\n\nUse the right panel to choose or generate an RPD.",
            )
            return

        out_dir = data.output_directory.get().strip()
        if not out_dir:
            ErrorWindow(self.controller, "Please select an Output Directory first.")
            return

        # Disable button
        self.run_button.configure(state="disabled", text="Running RCT...")

        loading = LoadingWindow(self.controller, "Starting RCT evaluation...")
        loading.set_progress(0.0)
        loading.update_idletasks()

        def worker():
            try:
                # Load the RPD file
                rpd = deserialize_rpd_file(data.active_rpd_path)

                def handle_line(line: str):
                    # forward text to loading window
                    self.after(0, lambda l=line: loading.set_message(l))

                    # parse progress if present
                    m = re.search(r"progress:\s*(\d+)%", line, re.I)
                    if m:
                        pct = int(m.group(1))
                        self.after(0, lambda p=pct: loading.set_progress(p / 100.0))

                interceptor = StdoutInterceptor(handle_line)

                with redirect_stdout(interceptor):
                    run_project_evaluation(
                        [rpd],
                        "ashrae9012019",
                        ["ASHRAE9012019DetailReport"],
                        saving_dir=out_dir,
                    )

                # Update UI on success
                self.after(0, lambda: loading.set_progress(1.0))

                report_path = Path(out_dir) / "ASHRAE9012019DetailReport.json"
                self.main_app.data.active_rct_report_path = str(report_path)

                self.after(
                    0,
                    lambda: self.controller.on_evaluation_complete(
                        True, f"Results saved to:\n{out_dir}"
                    ),
                )

            except Exception:
                tb = traceback.format_exc()
                msg = "RCT failed with an exception:\n\n" f"{tb}"

                self.after(
                    0,
                    lambda m=msg: ErrorWindow(self.controller, m),
                )

            finally:
                self.after(0, loading.close)
                self.after(
                    0,
                    lambda: self.run_button.configure(
                        state="normal", text="Run RCT Evaluation"
                    ),
                )

        threading.Thread(target=worker, daemon=True).start()
