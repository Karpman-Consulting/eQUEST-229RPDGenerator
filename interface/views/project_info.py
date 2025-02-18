import customtkinter as ctk
from tkinter import filedialog
from pathlib import Path

from interface.base_view import BaseView
from interface.ctk_xyframe import CTkXYFrame

LABEL_FONT = ("Arial", 14, "bold")
TEXT_FONT = ("Arial", 14)
READONLY = "readonly"
W = "w"
E = "e"
FILL = "nsew"
LEFT = "left"
PAD20END = (0, 20)
PAD20START = (20, 0)


class ProjectInfoView(BaseView):
    def __init__(self, window):
        super().__init__(window)

        # All subviews will be placed inside this frame. Single row/column allows formatting of subview to be handled by the subview itself
        self.subview_frame = ctk.CTkFrame(self)
        self.current_subview = None

        self.subviews = {
            "Project Details": ProjectDetailsView(self.subview_frame),
            "Project Config.": ProjectConfigView(self.subview_frame),
        }

        self.subview_buttons = {}
        self.subview_button_frame = ctk.CTkFrame(
            self, corner_radius=0, fg_color="transparent"
        )
        self.create_subbutton_bar()

    def __repr__(self):
        return "ProjectInfoView"

    def open_view(self):
        # Overwrite behavior of the continue button
        self.window.continue_button.configure(command=self.view_continue)
        # Update the errors and warnings button formatting
        self.update_warnings_errors()

        self.toggle_active_button("Project Info")
        self.grid_propagate(False)

        # 3 rows in the main surface view structure. Subview frame (row 2, index 1) has a weight to make it fill up the empty space in the window
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Subview buttons
        self.subview_button_frame.grid(row=0, column=0, sticky=W, padx=20, pady=(20, 0))
        for index, name in enumerate(self.subview_buttons):
            # Layout the button inside the frame
            button = self.subview_buttons[name]
            button.grid(row=0, column=index, padx=(0, 4))

        # Subview frame
        self.subview_frame.grid(row=1, column=0, sticky="nsew", padx=20, pady=PAD20END)
        self.subview_frame.grid_rowconfigure(0, weight=1)
        self.subview_frame.grid_columnconfigure(0, weight=1)

        # Show the "Project Details" subview by default
        self.show_subview("Project Details")
        self.toggle_active_subbutton("Project Details")

    def create_subbutton_bar(self):
        # TODO: Check for empty subviews
        callback_methods = {
            "Project Details": lambda: self.show_subview("Project Details"),
            "Project Config.": lambda: self.show_subview("Project Config."),
        }

        for name in callback_methods:
            # Create the button to go inside this button frame
            button = ctk.CTkButton(
                self.subview_button_frame,
                text=name,
                fg_color="#FFD966",
                hover_color="#FFD966",
                text_color="black",
                font=("Arial", 12, "bold"),
                width=140,
                height=30,
                corner_radius=0,
                compound=LEFT,
                command=callback_methods[name],
            )
            self.subview_buttons[name] = button

    def show_subview(self, subview_name):
        # Clear previous subview
        if self.current_subview is not None:
            self.current_subview.grid_forget()

        # Show new subview
        subview = self.subviews.get(subview_name)
        if subview:
            self.current_subview = subview
            self.current_subview.grid(row=0, column=0, sticky="nsew")
            self.current_subview.open_subview()

    def toggle_active_subbutton(self, active_subbutton_name):
        for name, button in self.subview_buttons.items():
            if name == active_subbutton_name:
                self.subview_buttons[name].configure(
                    fg_color="#FFED67",
                    hover_color="#FFED67",
                    text_color="black",
                    font=("Arial", 12, "bold"),
                )
            else:
                self.subview_buttons[name].configure(
                    fg_color="#FFD966",
                    hover_color="#FFD966",
                    text_color="black",
                    font=("Arial", 12, "bold"),
                )

    def view_continue(self):
        if self.current_subview == self.subviews.get("Project Details"):
            self.current_subview.save_project_details()
        self.window.show_view("Buildings")


class ProjectDetailsView(CTkXYFrame):
    def __init__(self, subview_frame):
        super().__init__(subview_frame)
        self.project_info_view = subview_frame.master
        self.app_data = self.project_info_view.window.main_app.data
        self.is_subview_populated = False

        # Initialize Widgets
        self.options_frame = ctk.CTkFrame(subview_frame, fg_color="transparent")
        self.infiltration_frame = ctk.CTkFrame(
            self.options_frame, fg_color="transparent"
        )
        self.climate_zone_label = ctk.CTkLabel(
            self.options_frame,
            text="ASHRAE Climate Zone:",
            anchor=E,
            font=LABEL_FONT,
        )
        self.climate_zone_combo = ctk.CTkComboBox(
            self.options_frame,
            values=self.app_data.ClimateZoneDescriptions2019ASHRAE901,
            state=READONLY,
        )
        self.climate_zone_combo._entry.configure(justify=LEFT)
        self.lighting_zone_label = ctk.CTkLabel(
            self.options_frame,
            text="Exterior Lighting Zone:",
            anchor=E,
            font=LABEL_FONT,
        )
        self.lighting_zone_combo = ctk.CTkComboBox(
            self.options_frame,
            values=self.app_data.ExteriorLightingZoneDescriptions2019ASHRAE901,
            state=READONLY,
        )
        self.lighting_zone_combo._entry.configure(justify=LEFT)
        self.building_open_schedule_label = ctk.CTkLabel(
            self.options_frame,
            text="Building Open Schedule:",
            anchor=E,
            font=LABEL_FONT,
        )
        self.open_from_label = ctk.CTkLabel(
            self.options_frame,
            text="From:",
            anchor=E,
            font=("Arial", 14),
        )
        self.open_from_input = ctk.CTkEntry(self.options_frame)
        self.open_to_label = ctk.CTkLabel(
            self.options_frame,
            text="From:",
            anchor=E,
            font=("Arial", 14),
        )
        self.open_to_input = ctk.CTkEntry(self.options_frame)
        self.heating_design_day_label = ctk.CTkLabel(
            self.options_frame,
            text="Heating Design Day Criteria:",
            anchor=E,
            font=LABEL_FONT,
        )
        self.heating_design_day_combo = ctk.CTkComboBox(
            self.options_frame,
            values=self.app_data.HeatingDesignDayDescriptions,
            state=READONLY,
        )
        self.heating_design_day_combo._entry.configure(justify=LEFT)
        self.cooling_design_day_label = ctk.CTkLabel(
            self.options_frame,
            text="Cooling Design Day Criteria:",
            anchor=E,
            font=LABEL_FONT,
        )
        self.cooling_design_day_combo = ctk.CTkComboBox(
            self.options_frame,
            values=self.app_data.CoolingDesignDayDescriptions,
            state=READONLY,
        )
        self.cooling_design_day_combo._entry.configure(justify=LEFT)
        self.measured_infiltration_checkbox = ctk.CTkCheckBox(
            self.infiltration_frame,
            text="Measured Infiltration?",
            font=LABEL_FONT,
            command=self.toggle_measured_infiltration,
        )
        self.pressure_difference_label = ctk.CTkLabel(
            self.infiltration_frame,
            text="Pressure Difference:",
            anchor=E,
            font=("Arial", 14),
        )
        self.pressure_difference_input = ctk.CTkEntry(self.infiltration_frame)
        self.site_testing_checkbox = ctk.CTkCheckBox(
            self.infiltration_frame,
            text="Based on Site Selection?",
            font=("Arial", 14),
        )

        self.populate_subview()

    def __repr__(self):
        return "ProjectDetailsView"

    def open_subview(self):
        self.project_info_view.toggle_active_subbutton("Project Details")
        self.populate_subview() if not self.is_subview_populated else None

    def populate_subview(self):
        # Place widgets
        self.climate_zone_label.grid(
            row=0, column=0, sticky="ew", padx=PAD20START, pady=PAD20START
        )
        self.climate_zone_combo.grid(
            row=0, column=1, sticky="ew", padx=5, pady=PAD20START
        )
        self.lighting_zone_label.grid(
            row=1, column=0, sticky="ew", padx=PAD20START, pady=5
        )
        self.lighting_zone_combo.grid(row=1, column=1, sticky="ew", padx=5, pady=5)
        self.building_open_schedule_label.grid(
            row=2, column=0, sticky="ew", padx=PAD20START, pady=5
        )
        self.open_from_label.grid(row=3, column=0, sticky="ew", pady=5)
        self.open_from_input.grid(row=3, column=1, sticky="ew", padx=5, pady=5)
        self.open_to_label.grid(row=4, column=0, sticky="ew", pady=5)
        self.open_to_input.grid(row=4, column=1, sticky="ew", padx=5, pady=5)
        self.heating_design_day_label.grid(
            row=5, column=0, sticky="ew", padx=PAD20START, pady=5
        )
        self.heating_design_day_combo.grid(row=5, column=1, sticky="ew", padx=5, pady=5)
        self.cooling_design_day_label.grid(
            row=6, column=0, sticky="ew", padx=PAD20START, pady=5
        )
        self.cooling_design_day_combo.grid(row=6, column=1, sticky="ew", padx=5, pady=5)

        self.options_frame.grid(row=0, column=0, sticky="nsew")

        self.infiltration_frame.grid(
            row=0,
            column=2,
            rowspan=3,
            columnspan=2,
            sticky="nsew",
            padx=200,
            pady=PAD20START,
        )
        self.measured_infiltration_checkbox.grid(row=0, column=0, sticky="ew", padx=5)
        self.measured_infiltration_checkbox.select()
        self.pressure_difference_label.grid(row=1, column=0, sticky="ew", padx=5)
        self.pressure_difference_input.grid(row=1, column=1, sticky="ew", padx=5)
        self.site_testing_checkbox.grid(
            row=2, column=0, columnspan=2, sticky="ew", padx=50
        )

    def toggle_measured_infiltration(self):
        if self.measured_infiltration_checkbox.get():
            self.pressure_difference_label.grid()
            self.pressure_difference_input.grid()
            self.site_testing_checkbox.grid()
        else:
            self.pressure_difference_label.grid_remove()
            self.pressure_difference_input.grid_remove()
            self.site_testing_checkbox.grid_remove()

    # TODO: not necessarily "configuration data". Maybe change to "project data" or have 2 data structures
    def save_project_details(self):
        self.app_data.configuration_data["ashrae_climate_zone"] = (
            self.climate_zone_combo.get()
        )
        self.app_data.configuration_data["exterior_lighting_zone"] = (
            self.lighting_zone_combo.get()
        )
        self.app_data.configuration_data["open_from"] = self.open_from_input.get()
        self.app_data.configuration_data["open_to"] = self.open_to_input.get()
        self.app_data.configuration_data["heating_design_day_criteria"] = (
            self.heating_design_day_combo.get()
        )
        self.app_data.configuration_data["cooling_design_day_criteria"] = (
            self.cooling_design_day_combo.get()
        )
        self.app_data.configuration_data["uses_measured_infiltration"] = bool(
            self.measured_infiltration_checkbox.get()
        )
        self.app_data.configuration_data["pressure_difference"] = (
            self.pressure_difference_input.get()
        )
        self.app_data.configuration_data["based_on_site_testing"] = bool(
            self.site_testing_checkbox.get()
        )


class ProjectConfigView(CTkXYFrame):
    def __init__(self, subview_frame):
        super().__init__(subview_frame)
        self.project_info_view = subview_frame.master
        self.app_data = self.project_info_view.window.main_app.data
        self.is_subview_populated = False

        self.ruleset_model_row_widgets = {}

        # Initialize Widgets
        self.new_construction_checkbox = ctk.CTkCheckBox(
            self,
            text="All new construction?",
            font=("Arial", 14),
        )
        self.directions_label = ctk.CTkLabel(
            self,
            text="Directions: ",
            anchor=E,
            justify=LEFT,
            font=LABEL_FONT,
        )

        directions_text = "Select the Energy Code or Above-Code Program for your project, then browse and select the eQUEST model input files (*.inp) associated with each of the \napplicable models expected by the ruleset."
        self.directions = ctk.CTkLabel(
            self,
            text=directions_text,
            anchor=W,
            justify=LEFT,
            font=LABEL_FONT,
        )
        self.note_label = ctk.CTkLabel(
            self, text="Note: ", anchor=E, justify=LEFT, font=LABEL_FONT
        )
        note_text = "When you select an input file, it is expected that the same directory will also include the simulation output files associated with the selected input file. \nThis application will check for the following associated file extensions:\n(*.nhk), (*.lrp), (*.srp), (*.erp)\n\n(*) can be identical to the selected *.inp file or can include the suffix ' - Baseline Design'"
        self.note = ctk.CTkLabel(
            self, text=note_text, anchor=W, justify=LEFT, font=TEXT_FONT
        )
        self.project_name_label = ctk.CTkLabel(
            self, text="Project Name: ", font=LABEL_FONT, anchor=E
        )
        self.project_name_entry = ctk.CTkEntry(
            self,
            font=TEXT_FONT,
            textvariable=self.app_data.project_name,
            state=READONLY,
        )
        self.ruleset_label = ctk.CTkLabel(
            self, text="Energy Code/Program:", font=LABEL_FONT, anchor=E
        )
        self.ruleset_models_frame = ctk.CTkFrame(self, width=800, height=250)
        self.ruleset_dropdown = ctk.CTkOptionMenu(
            self,
            values=["ASHRAE 90.1-2019", "None"],
            command=lambda selection: self.update_ruleset_model_frame(selection),
        )
        self.ruleset_dropdown.set(self.app_data.selected_ruleset.get())
        self.rotation_exception_checkbox = ctk.CTkCheckBox(
            self,
            text="Baseline Rotation Exempt? (90.1-2019 Table G3.1(5) Baseline Building Performance (a))",
            font=TEXT_FONT,
            variable=self.app_data.has_rotation_exception,
            command=self.toggle_baseline_rotations,
        )
        self.ruleset_models_label = ctk.CTkLabel(
            self,
            text="Models: ",
            anchor=E,
            justify=LEFT,
            font=LABEL_FONT,
        )
        self.output_dir_label = ctk.CTkLabel(
            self, text="Output Directory:", font=LABEL_FONT, anchor=E
        )
        self.output_dir_entry = ctk.CTkEntry(
            self,
            font=TEXT_FONT,
            width=500,
            textvariable=self.app_data.output_directory,
        )
        self.output_dir_button = ctk.CTkButton(
            self,
            text="Select",
            command=self.select_output_directory,
            width=80,
        )

        self.continue_button = ctk.CTkButton(
            self,
            text="Continue",
            width=100,
            corner_radius=12,
            # TODO: come back to this, goes with regenerate rmds button
            # command=self.validate_project_info,
        )
        self.populate_subview()

    def __repr__(self):
        return "ProjectConfigView"

    def open_subview(self):
        self.project_info_view.toggle_active_subbutton("Project Config.")
        self.populate_subview() if not self.is_subview_populated else None

    def populate_subview(self):
        # Place widgets
        # Row 0
        self.directions_label.grid(row=0, column=0, sticky=E + W, padx=5, pady=(20, 5))
        self.directions.grid(
            row=0, column=1, columnspan=8, sticky="new", padx=5, pady=(20, 5)
        )

        # Row 1
        self.note_label.grid(row=1, column=0, sticky="new", padx=5, pady=5)
        self.note.grid(row=1, column=1, columnspan=8, sticky=E + W, padx=5, pady=5)

        # Row 2
        self.project_name_label.grid(row=2, column=0, sticky=E, padx=5, pady=(50, 10))
        self.project_name_entry.grid(
            row=2, column=1, columnspan=3, sticky=E + W, padx=5, pady=(50, 10)
        )

        # Row 3
        self.ruleset_label.grid(row=3, column=0, sticky=E, padx=5, pady=5)
        self.ruleset_dropdown.grid(
            row=3, column=1, columnspan=2, sticky=E + W, padx=5, pady=5
        )

        # Row 4 Placeholder for the rotation exception checkbox

        # Row 5
        self.ruleset_models_label.grid(row=5, column=0, sticky=E + W, padx=5, pady=5)

        self.show_ruleset_models()
        self.ruleset_models_frame.grid(row=5, column=1, columnspan=8, sticky=FILL)

        # Row 6
        self.output_dir_label.grid(
            row=6, column=0, sticky=E, padx=(20, 5), pady=(15, 5)
        )
        self.output_dir_entry.grid(
            row=6, column=1, columnspan=5, sticky=E + W, padx=5, pady=(15, 5)
        )
        self.output_dir_button.grid(row=6, column=6, sticky=E + W, padx=5, pady=(15, 5))

    def update_ruleset_model_frame(self, selected_ruleset):
        self.app_data.selected_ruleset.set(selected_ruleset)
        self.rotation_exception_checkbox.grid_remove()
        self.clear_ruleset_models_frame()
        self.show_ruleset_models()

    def show_ruleset_models(self):
        # Main logic
        if self.app_data.selected_ruleset.get() == "ASHRAE 90.1-2019":
            self.rotation_exception_checkbox.grid(
                row=4, column=1, columnspan=4, sticky=W, padx=5, pady=(15, 5)
            )
            labels = ["Design: ", "Proposed: ", "Baseline: "]
            if not self.rotation_exception_checkbox.get():
                labels.extend(["Baseline 90: ", "Baseline 180: ", "Baseline 270: "])
        else:
            labels = ["Design: "]

        # Create and place rows based on the selected ruleset
        self.create_model_rows(labels)

    def create_model_rows(self, labels):
        """Create and place rows for ruleset model path widgets."""
        for row_num, label_text in enumerate(labels):
            label, path_entry, select_button = self.create_file_row(label_text)

            # Place widgets using grid
            label.grid(row=row_num, column=0, sticky=E + W, padx=5, pady=5)
            path_entry.grid(
                row=row_num, column=1, columnspan=7, sticky=E + W, padx=5, pady=5
            )
            select_button.grid(row=row_num, column=8, sticky=E + W, padx=5, pady=5)

            if len(labels) == 1:
                self.ruleset_models_frame.grid_rowconfigure(
                    0, weight=1
                )  # Center first row
            else:
                for i in range(len(labels)):
                    self.ruleset_models_frame.grid_rowconfigure(i, weight=0)

    def clear_ruleset_models_frame(self):
        for row_widgets in self.ruleset_model_row_widgets.values():
            for widget in row_widgets:
                widget.grid_remove()

    def toggle_baseline_rotations(self):
        """Add or remove Baseline rotation rows based on checkbox state."""
        for row_widgets in self.ruleset_model_row_widgets.values():
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

    def create_file_row(self, label_text):
        """Create a row of widgets without placing them using grid()."""
        model_text = label_text.split(":")[0]

        if model_text in self.ruleset_model_row_widgets:
            return self.ruleset_model_row_widgets[model_text]

        # Create label
        label = ctk.CTkLabel(
            self.ruleset_models_frame,
            text=label_text,
            font=TEXT_FONT,
            width=90,
            anchor=E,  # Align text to the right within the label
        )

        # Create entry, prepopulate project info if selected in project config on startup
        path_entry = ctk.CTkEntry(
            self.ruleset_models_frame, width=700, font=("Arial", 12)
        )
        model_type = model_text.replace("Design", "User")

        # Model Type may not exist in the dictionary if the user did not select a file for it or the user changed the ruleset after selecting files
        file_path = self.app_data.ruleset_model_file_paths.get(model_type, "")
        if file_path:
            path_entry.insert(0, self._get_trimmed_path(file_path))

        # File select button
        def select_file():
            selected_path = filedialog.askopenfilename(
                filetypes=[("eQUEST Input Files", "*.inp")]
            )
            if selected_path:
                path_entry.delete(0, "end")
                path_entry.insert(0, self._get_trimmed_path(selected_path))
                self.app_data.ruleset_model_file_paths[model_type] = selected_path

        select_button = ctk.CTkButton(
            self.ruleset_models_frame,
            text="Select",
            command=select_file,
            width=80,
            height=30,
        )

        # Store created widgets for reuse
        self.ruleset_model_row_widgets[model_text] = (
            label,
            path_entry,
            select_button,
        )

        return label, path_entry, select_button

    # TODO: When model files are changed, show a button that allows regeneration of the RMDs
    # TODO: When options on this view are changed, show warning
    def validate_project_info(self):
        """Verify that all required file paths have been selected."""
        # Check that at least 1 file path has been selected
        if not any(self.app_data.ruleset_model_file_paths.values()):
            self.app_data.errors = ["At least one file must be selected to continue."]
            self.project_info_view.update_warnings_errors()
            return

        # If the code reaches this point, at least one file is selected so clear any errors
        self.app_data.errors.clear()

        # For each file that is selected, make sure that the directory also contains the associated output files
        for (
            model_type,
            file_path,
        ) in self.app_data.ruleset_model_file_paths.items():
            if file_path:
                if not self.app_data.verify_associated_files(file_path):
                    model_type = model_type.replace("User", "Design")
                    self.app_data.errors.append(
                        f"Associated simulation output files not found for the selected '{model_type}' model."
                    )
                    self.project_info_view.update_warnings_errors()

        if len(self.app_data.errors) > 0:
            return

        # If the code reaches this point, at least one file is selected and all associated files are found so clear any errors
        self.app_data.errors.clear()

        # Required model types
        required_models = ["User", "Proposed", "Baseline"]
        if not self.rotation_exception_checkbox.get():
            required_models.extend(["Baseline 90", "Baseline 180", "Baseline 270"])

        # Check if all required model types have file paths selected
        for model_type in required_models:
            if (
                model_type not in self.app_data.ruleset_model_file_paths
                or not self.app_data.ruleset_model_file_paths[model_type]
            ):
                model_type = model_type.replace("User", "Design")
                self.app_data.warnings.append(
                    f"The '{model_type}' model is missing and is required to evaluate the ASHRAE 90.1-2019 ruleset."
                )

        self.project_info_view.update_warnings_errors()
        # If there are no errors, reload the model files and refresh the GUI data
        # self.reload_model_files()

    # def reload_model_files(self):
    #     self.app_data.generate_rmds()

    def view_continue(self):
        self.project_info_view.window.show_view("Buildings")

    def select_output_directory(self):
        """Opens a directory selection dialog and updates the entry field."""
        directory = filedialog.askdirectory()
        if directory:
            self.output_dir_entry.delete(0, "end")
            self.output_dir_entry.insert(0, directory)
            self.app_data.output_directory.set(directory)

    @staticmethod
    def _get_trimmed_path(file_path: str) -> str:
        """Helper function to extract parent directory and filename from a file path using pathlib."""
        path = Path(file_path)
        if path.parent:
            return f"{path.parent.name}/{path.name}"
        return path.name
