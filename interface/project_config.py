import customtkinter as ctk
import threading
from tkinter import Menu, filedialog
from pathlib import Path

from interface.CTkToolTip import CTkToolTip
from interface.disclaimer_window import DisclaimerWindow
from interface.loading_window import LoadingWindow
from interface.error_window import ErrorWindow
from interface.constants import *
from rpd_generator.artifacts.ruleset_project_description import (
    RulesetProjectDescription,
)


class ProjectConfigWindow(ctk.CTkToplevel):
    def __init__(self, main_app):
        super().__init__()
        self.main_app = main_app

        self.title("Project Configuration")
        self.license_window = None
        self.disclaimer_window = None
        self.progress_window = None
        self.error_window = None

        self.main_app.data.ruleset_model_file_paths = {
            ruleset: {} for ruleset in RULESETS
        }
        self.ruleset_model_row_widgets = {ruleset: {} for ruleset in RULESETS}

        # Initialize Widgets
        self.directions_label = ctk.CTkLabel(
            self,
            text="Directions: ",
            anchor="e",
            justify="left",
            font=("Arial", 16, "bold"),
        )
        directions_text = "Select the Energy Code or Above-Code Program for your project, then browse and select the eQUEST model input files (*.inp) \nassociated with each of the applicable models expected by the ruleset."
        self.directions = ctk.CTkLabel(
            self,
            text=directions_text,
            anchor="w",
            justify="left",
            font=("Arial", 14, "bold"),
        )
        self.note_label = ctk.CTkLabel(
            self, text="Note: ", anchor="e", justify="left", font=("Arial", 16, "bold")
        )
        note_text = "When you select an input file, it is expected that the same directory will also include the simulation output files associated with the selected input file. \nThis application will check for the following associated file extensions:\n(*.nhk), (*.lrp), (*.srp), (*.erp)\n\n(*) can be identical to the selected *.inp file or can include the suffix ' - Baseline Design'"
        self.note = ctk.CTkLabel(
            self, text=note_text, anchor="w", justify="left", font=("Arial", 14)
        )
        self.project_name_label = ctk.CTkLabel(
            self, text="Project Name: ", font=("Arial", 14, "bold"), anchor="e"
        )
        self.project_name_entry = ctk.CTkEntry(
            self, font=("Arial", 14), textvariable=self.main_app.data.project_name
        )
        project_entry_tooltip = CTkToolTip(
            self.project_name_entry, message="Name of the project"
        )
        self.ruleset_label = ctk.CTkLabel(
            self, text="Energy Code/Program:", font=("Arial", 14, "bold"), anchor="e"
        )

        self.proposed_reflects_design_checkbox = ctk.CTkCheckBox(
            self,
            text="Proposed Design model reflects design documents?",
            font=("Arial", 14),
            variable=self.main_app.data.proposed_reflects_design,
            command=self.toggle_design,
            onvalue=True,
            offvalue=False,
        )
        self.rotation_exception_checkbox = ctk.CTkCheckBox(
            self,
            text="Was it demonstrated to the satisfaction of the rating authority that the building orientation is dictated by site considerations?",
            font=("Arial", 14),
            variable=self.main_app.data.has_rotation_exception,
            command=self.toggle_baseline_rotations,
            onvalue=True,
            offvalue=False,
        )
        rotation_exception_checkbox_tooltip = CTkToolTip(
            self.rotation_exception_checkbox,
            message="Check this box if the building is exempt from the Baseline Rotation requirement.",
        )
        self.ruleset_models_frame = ctk.CTkFrame(self, width=800)
        self.ruleset_dropdown = ctk.CTkOptionMenu(
            self,
            values=RULESETS,
            variable=self.main_app.data.selected_ruleset,
            command=self.update_ruleset_model_frame,
        )
        self.ruleset_models_label = ctk.CTkLabel(
            self,
            text="Models: ",
            anchor="e",
            justify="left",
            font=("Arial", 14, "bold"),
        )
        self.output_dir_label = ctk.CTkLabel(
            self, text="Output Directory:", font=("Arial", 14, "bold"), anchor="e"
        )
        self.output_dir_entry = ctk.CTkEntry(
            self,
            font=("Arial", 14),
            width=500,
            textvariable=self.main_app.data.output_directory,
        )
        output_dir_entry_tooltip = CTkToolTip(
            self.output_dir_entry,
            message="Directory where the RPD output files are stored after generation",
        )
        self.output_dir_button = ctk.CTkButton(
            self,
            text="Select",
            command=self.select_output_directory,
            width=80,
        )
        self.generate_button = ctk.CTkButton(
            self,
            text="Generate RPD",
            width=100,
            corner_radius=12,
            command=self.validate_project_info,
        )

        self.menubar = self.create_menu_bar()
        self.place_widgets()
        self.create_nav_bar()
        self._refresh_applicability()

    def __repr__(self):
        return "ProjectConfigWindow"

    def create_nav_bar(self):
        # Create the button to continue to the Buildings page
        self.generate_button.grid(row=8, column=0, columnspan=9, pady=15)

    def create_menu_bar(self):
        menubar = Menu(self)
        file_menu = Menu(menubar, tearoff=0)
        file_menu.add_command(label="New", command="donothing")
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.quit)
        menubar.add_cascade(label="File", menu=file_menu)

        help_menu = Menu(menubar, tearoff=0)
        help_menu.add_command(label="Instructions", command="donothing")
        help_menu.add_command(label="Background", command="donothing")
        help_menu.add_separator()
        help_menu.add_command(label="License", command="donothing")
        help_menu.add_command(label="Disclaimer", command=self.raise_disclaimer_window)
        menubar.add_cascade(label="About", menu=help_menu)

        self.config(menu=menubar)
        return menubar

    def raise_disclaimer_window(self):
        if self.disclaimer_window is None or not self.disclaimer_window.winfo_exists():
            self.disclaimer_window = DisclaimerWindow(self)
            self.disclaimer_window.after(100, self.disclaimer_window.lift, None)
        else:
            self.disclaimer_window.focus()  # if window exists, focus it

    def raise_error_window(self, error_text):
        if not error_text:
            return
        if self.error_window is None or not self.error_window.winfo_exists():
            self.error_window = ErrorWindow(self, error_text)
            self.error_window.after(100, self.error_window.lift, None)
        else:
            self.error_window.focus()  # if window exists, focus it

    def open_progress(self, message="Generating RPD..."):
        # Close any existing one first (defensive)
        if self.progress_window and self.progress_window.winfo_exists():
            self.progress_window.close()

        self.progress_window = LoadingWindow(self, message)
        self.after(100, self.progress_window.lift)

    def close_progress(self):
        if self.progress_window and self.progress_window.winfo_exists():
            self.progress_window.close()
        self.progress_window = None

    def place_widgets(self):
        # Place widgets
        # Row 0
        self.directions_label.grid(row=0, column=0, sticky="ew", padx=5, pady=(20, 5))
        self.directions.grid(
            row=0, column=1, columnspan=6, sticky="new", padx=5, pady=(20, 5)
        )

        # Row 1
        self.note_label.grid(row=1, column=0, sticky="new", padx=5, pady=5)
        self.note.grid(row=1, column=1, columnspan=8, sticky="ew", padx=(5, 20), pady=5)

        # Row 2
        self.project_name_label.grid(row=2, column=0, sticky="e", padx=5, pady=(30, 5))
        self.project_name_entry.grid(
            row=2, column=1, columnspan=3, sticky="ew", padx=5, pady=(30, 5)
        )

        # Row 3
        self.output_dir_label.grid(row=3, column=0, sticky="e", padx=(20, 5), pady=5)
        self.output_dir_entry.grid(
            row=3, column=1, columnspan=4, sticky="ew", padx=5, pady=5
        )
        self.output_dir_button.grid(row=3, column=5, sticky="w", padx=5, pady=5)

        # Row 4
        self.ruleset_label.grid(row=4, column=0, sticky="e", padx=(20, 5), pady=5)
        self.ruleset_dropdown.grid(
            row=4, column=1, columnspan=2, sticky="ew", padx=5, pady=5
        )

        # Row 5 Placeholder for proposed reflects design checkbox

        # Row 6 Placeholder for the rotation exception checkbox

        # Row 7
        self.ruleset_models_label.grid(row=7, column=0, sticky="ew", padx=5, pady=5)

        self.show_ruleset_models()
        self.ruleset_models_frame.grid(
            row=7, column=1, columnspan=6, sticky="nsew", padx=5
        )

    def update_ruleset_model_frame(self):
        self.proposed_reflects_design_checkbox.grid_remove()
        self.rotation_exception_checkbox.grid_remove()
        self.clear_ruleset_models_frame()
        self.show_ruleset_models()
        self._refresh_applicability()

    def show_ruleset_models(self):
        # Main logic
        if self.main_app.data.selected_ruleset.get() == "ASHRAE 90.1-2019 PRM":
            self.proposed_reflects_design_checkbox.grid(
                row=5, column=1, columnspan=4, sticky="w", padx=5, pady=5
            )
            self.rotation_exception_checkbox.grid(
                row=6, column=1, columnspan=4, sticky="w", padx=5, pady=(5, 10)
            )
            if not self.proposed_reflects_design_checkbox.get():
                labels = ["Design: ", "Proposed: ", "Baseline: "]
            else:
                labels = ["Design: ", "Baseline: "]
            if not self.rotation_exception_checkbox.get():
                labels.extend(["Baseline 90: ", "Baseline 180: ", "Baseline 270: "])
        else:
            labels = [""]

        # Create and place rows based on the selected ruleset
        self.create_model_rows(labels)

    def create_model_rows(self, labels):
        """Create and place rows for ruleset model path widgets."""
        for row_num, label_text in enumerate(labels):
            label, path_entry, select_button = self.create_file_row(label_text)

            # Place widgets using grid
            label.grid(row=row_num, column=0, sticky="ew", padx=5, pady=5)
            path_entry.grid(
                row=row_num, column=1, columnspan=7, sticky="ew", padx=5, pady=5
            )
            select_button.grid(row=row_num, column=8, sticky="ew", padx=5, pady=5)

            if len(labels) == 1:
                self.ruleset_models_frame.grid_rowconfigure(
                    0, weight=1
                )  # Center first row
            else:
                for i in range(len(labels)):
                    self.ruleset_models_frame.grid_rowconfigure(i, weight=0)

    def clear_ruleset_models_frame(self):
        for widget in self.ruleset_models_frame.winfo_children():
            widget.grid_remove()

    def toggle_design(self):
        """Add or remove Design based on checkbox state."""
        active_ruleset = self.main_app.data.selected_ruleset.get()
        for row_widgets in self.ruleset_model_row_widgets[active_ruleset].values():
            if row_widgets[0].cget("text") == "Proposed: ":
                if row_widgets[0].winfo_ismapped():
                    # If visible, hide them
                    for widget in row_widgets:
                        widget.grid_remove()
                else:
                    # If hidden, show them
                    for widget in row_widgets:
                        widget.grid()
        self._refresh_applicability()

    def toggle_baseline_rotations(self):
        """Add or remove Baseline rotation rows based on checkbox state."""
        active_ruleset = self.main_app.data.selected_ruleset.get()
        for row_widgets in self.ruleset_model_row_widgets[active_ruleset].values():
            if row_widgets[0].cget("text") in [
                "Baseline 90: ",
                "Baseline 180: ",
                "Baseline 270: ",
            ]:
                if row_widgets[0].winfo_ismapped():
                    # If visible, hide them
                    for widget in row_widgets:
                        widget.grid_remove()
                else:
                    # If hidden, show them
                    for widget in row_widgets:
                        widget.grid()
        self._refresh_applicability()

    def create_file_row(self, label_text):
        """Create a row of widgets without placing them using grid()."""
        model_text = label_text.split(":")[0]
        active_ruleset = self.main_app.data.selected_ruleset.get()
        # Avoid recreating widgets if they already exist
        if model_text in self.ruleset_model_row_widgets[active_ruleset]:
            return self.ruleset_model_row_widgets[active_ruleset][model_text]

        # Create label
        label = ctk.CTkLabel(
            self.ruleset_models_frame,
            text=label_text,
            font=("Arial", 14),
            width=90,
            anchor="e",  # Align text to the right within the label
        )

        # Create entry
        path_entry = ctk.CTkEntry(
            self.ruleset_models_frame, width=700, font=("Arial", 12)
        )

        model_type = model_text.replace("Design", "User")

        # File select button
        def select_file():
            selected_path = filedialog.askopenfilename(
                parent=self,
                filetypes=[("eQUEST Input Files", "*.inp")],
            )
            if selected_path:
                path_entry.delete(0, "end")
                path_entry.insert(0, self._get_trimmed_path(selected_path))
                self.main_app.data.ruleset_model_file_paths[active_ruleset][
                    model_type
                ] = selected_path

        select_button = ctk.CTkButton(
            self.ruleset_models_frame,
            text="Select",
            command=select_file,
            width=80,
            height=30,
        )

        # Store created widgets for reuse
        self.ruleset_model_row_widgets[active_ruleset][model_text] = (
            label,
            path_entry,
            select_button,
        )

        return label, path_entry, select_button

    def validate_project_info(self):
        """Verify that all required file paths have been selected, and generate the RPD file."""
        # Check that at least 1 file path has been selected
        active_ruleset = self.main_app.data.selected_ruleset.get()
        if not any(
            self.main_app.data.ruleset_model_file_paths[active_ruleset].values()
        ):
            self.main_app.data.errors = [
                "At least one file must be selected to continue."
            ]
            self.raise_error_window("\n".join(self.main_app.data.errors))
            return

        # If the code reaches this point, at least one file is selected so clear any errors
        self.main_app.data.errors.clear()
        # For each file that is selected, make sure that the directory also contains the associated output files
        for (
            model_type,
            file_path,
        ) in self.main_app.data.ruleset_model_file_paths[active_ruleset].items():
            if file_path:
                if not self.verify_associated_files(file_path):
                    model_type = model_type.replace("User", "Design")
                    self.main_app.data.errors.append(
                        f"Associated simulation output files not found for the selected '{model_type}' model."
                    )

        if len(self.main_app.data.errors) > 0:
            self.raise_error_window("\n".join(self.main_app.data.errors))
            return

        # If the code reaches this point, at least one file is selected and all associated files are found so clear any errors
        self.main_app.data.errors.clear()

        if self.main_app.data.selected_ruleset.get() == "ASHRAE 90.1-2019 PRM":
            # Required model types
            required_models = ["User", "Proposed", "Baseline"]
            if not self.rotation_exception_checkbox.get():
                required_models.extend(["Baseline 90", "Baseline 180", "Baseline 270"])
            if self.proposed_reflects_design_checkbox.get():
                self.main_app.data.ruleset_model_file_paths[active_ruleset][
                    "Proposed"
                ] = self.main_app.data.ruleset_model_file_paths[active_ruleset].get(
                    "User"
                )

            # Check if all required model types have file paths selected
            for model_type in required_models:
                if (
                    model_type
                    not in self.main_app.data.ruleset_model_file_paths[active_ruleset]
                    or not self.main_app.data.ruleset_model_file_paths[active_ruleset][
                        model_type
                    ]
                ):
                    model_type = model_type.replace("User", "Design")
                    self.main_app.data.errors.append(
                        f"The '{model_type}' model is missing and is required to evaluate the ASHRAE 90.1-2019 ruleset."
                    )

        # If there are no errors, generate RMDs
        if len(self.main_app.data.errors) == 0:
            self.generate_button.configure(state="disabled", text="Generating...")
            self.open_progress("Generating RPD...")
            worker = threading.Thread(target=self._generate_rpd_thread, daemon=True)
            worker.start()

        # If there are errors, raise the error window
        else:
            self.raise_error_window("\n".join(self.main_app.data.errors))

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

    def select_output_directory(self):
        """Opens a directory selection dialog and updates the entry field."""
        directory = filedialog.askdirectory(
            parent=self, title="Select Output Directory"
        )
        if directory:
            self.output_dir_entry.delete(0, "end")
            self.output_dir_entry.insert(0, directory)
            self.main_app.data.output_directory.set(directory)

    @staticmethod
    def _get_trimmed_path(file_path: str) -> str:
        """Helper function to extract parent directory and filename from a file path using pathlib."""
        path = Path(file_path)
        if path.parent:
            return f"{path.parent.name}/{path.name}"
        return path.name

    def _active_model_types(self) -> list[str]:
        # Build the *current* applicable set
        active = []
        if self.main_app.data.selected_ruleset.get() == "ASHRAE 90.1-2019 PRM":
            active.append("User")  # "Design" label maps to "User" key
            if not self.proposed_reflects_design_checkbox.get():
                active.append("Proposed")
            active.append("Baseline")
            if not self.rotation_exception_checkbox.get():
                active.extend(["Baseline 90", "Baseline 180", "Baseline 270"])
        return active

    def _refresh_applicability(self):
        self.main_app.data.set_applicable_models(self._active_model_types())

    def _generate_rpd_thread(self):
        try:
            data = self.main_app.data
            data.rpd = RulesetProjectDescription(data.project_name.get())
            data.rpd.populate_data_elements()

            def report_progress(done: int, total: int, m: str):
                frac = 0.75 * (done / total) if total else 0.0
                self.after(
                    0, lambda: self._progress_update(f"{m}  ({done}/{total})", frac)
                )

            # update message before starting
            self.after(0, lambda: self._progress_update("Reading models...", 0.0))

            data.generate_rmd_data(data.rpd, progress_cb=report_progress)

            self.after(0, lambda: self._progress_update("Running checks...", 0.75))
            data.run_model_checks()

            if len(data.errors) == 0:
                self.after(0, lambda: self._progress_update("Writing output...", 0.76))
                data.call_write_rpd_json_from_rmds()
                self.after(
                    0,
                    lambda: self._on_generation_complete(
                        True, "RPD successfully generated."
                    ),
                )
            else:
                msg = "\n".join(data.errors)
                self.after(0, lambda: self._on_generation_complete(False, msg))
        except Exception as e:
            self.after(0, lambda: self._on_generation_complete(False, str(e)))

    def _on_generation_complete(self, success: bool, msg: str = ""):
        self.close_progress()
        # Restore button
        self.generate_button.configure(state="normal", text="Generate RPD")

        if success:
            self.main_app.data.errors.clear()
            self.raise_error_window("RPD successfully generated!")
        else:
            self.raise_error_window(msg)

    def _progress_update(self, msg: str, frac: float):
        if self.progress_window and self.progress_window.winfo_exists():
            self.progress_window.set_message(msg)
            # clamp for safety
            self.progress_window.set_progress(max(0.0, min(1.0, float(frac))))
