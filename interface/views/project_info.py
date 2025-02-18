import customtkinter as ctk
from tkinter import filedialog

from interface.base_view import BaseView
from interface.ctk_xyframe import CTkXYFrame

STANDARD_FONT = ("Arial", 16, "bold")
SMALL_BOLD = ("Arial", 14, "bold")
SMALL_STANDARD = ("Arial", 14)
READONLY = "readonly"
W = "w"
E = "e"
LEFT = "left"
PAD20 = (0, 20)
LEFT_PADX_20 = (20, 0)
TOP_PADY_20 = (20, 0)


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
        self.subview_frame.grid(row=1, column=0, sticky="nsew", padx=20, pady=PAD20)
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
        self.main_app_data = self.project_info_view.window.main_app.data
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
            font=SMALL_BOLD,
        )
        self.climate_zone_combo = ctk.CTkComboBox(
            self.options_frame,
            values=self.main_app_data.ClimateZoneDescriptions2019ASHRAE901.get_list(),
            state=READONLY,
        )
        self.climate_zone_combo._entry.configure(justify=LEFT)
        self.lighting_zone_label = ctk.CTkLabel(
            self.options_frame,
            text="Exterior Lighting Zone:",
            anchor=E,
            font=SMALL_BOLD,
        )
        self.lighting_zone_combo = ctk.CTkComboBox(
            self.options_frame,
            values=self.main_app_data.ExteriorLightingZoneDescriptions2019ASHRAE901.get_list(),
            state=READONLY,
        )
        self.lighting_zone_combo._entry.configure(justify=LEFT)
        self.building_open_schedule_label = ctk.CTkLabel(
            self.options_frame,
            text="Building Open Schedule:",
            anchor=E,
            font=SMALL_BOLD,
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
            font=SMALL_BOLD,
        )
        self.heating_design_day_combo = ctk.CTkComboBox(
            self.options_frame,
            values=self.main_app_data.HeatingDesignDayDescriptions.get_list(),
            state=READONLY,
        )
        self.heating_design_day_combo._entry.configure(justify=LEFT)
        self.cooling_design_day_label = ctk.CTkLabel(
            self.options_frame,
            text="Cooling Design Day Criteria:",
            anchor=E,
            font=SMALL_BOLD,
        )
        self.cooling_design_day_combo = ctk.CTkComboBox(
            self.options_frame,
            values=self.main_app_data.CoolingDesignDayDescriptions.get_list(),
            state=READONLY,
        )
        self.cooling_design_day_combo._entry.configure(justify=LEFT)
        self.measured_infiltration_checkbox = ctk.CTkCheckBox(
            self.infiltration_frame,
            text="Measured Infiltration?",
            font=SMALL_BOLD,
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
            row=0, column=0, sticky="ew", padx=LEFT_PADX_20, pady=TOP_PADY_20
        )
        self.climate_zone_combo.grid(
            row=0, column=1, sticky="ew", padx=5, pady=TOP_PADY_20
        )
        self.lighting_zone_label.grid(
            row=1, column=0, sticky="ew", padx=LEFT_PADX_20, pady=5
        )
        self.lighting_zone_combo.grid(row=1, column=1, sticky="ew", padx=5, pady=5)
        self.building_open_schedule_label.grid(
            row=2, column=0, sticky="ew", padx=LEFT_PADX_20, pady=5
        )
        self.open_from_label.grid(row=3, column=0, sticky="ew", pady=5)
        self.open_from_input.grid(row=3, column=1, sticky="ew", padx=5, pady=5)
        self.open_to_label.grid(row=4, column=0, sticky="ew", pady=5)
        self.open_to_input.grid(row=4, column=1, sticky="ew", padx=5, pady=5)
        self.heating_design_day_label.grid(
            row=5, column=0, sticky="ew", padx=LEFT_PADX_20, pady=5
        )
        self.heating_design_day_combo.grid(row=5, column=1, sticky="ew", padx=5, pady=5)
        self.cooling_design_day_label.grid(
            row=6, column=0, sticky="ew", padx=LEFT_PADX_20, pady=5
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
            pady=TOP_PADY_20,
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
        self.main_app_data.configuration_data["ashrae_climate_zone"] = (
            self.climate_zone_combo.get()
        )
        self.main_app_data.configuration_data["exterior_lighting_zone"] = (
            self.lighting_zone_combo.get()
        )
        self.main_app_data.configuration_data["open_from"] = self.open_from_input.get()
        self.main_app_data.configuration_data["open_to"] = self.open_to_input.get()
        self.main_app_data.configuration_data["heating_design_day_criteria"] = (
            self.heating_design_day_combo.get()
        )
        self.main_app_data.configuration_data["cooling_design_day_criteria"] = (
            self.cooling_design_day_combo.get()
        )
        self.main_app_data.configuration_data["uses_measured_infiltration"] = bool(
            self.measured_infiltration_checkbox.get()
        )
        self.main_app_data.configuration_data["pressure_difference"] = (
            self.pressure_difference_input.get()
        )
        self.main_app_data.configuration_data["based_on_site_testing"] = bool(
            self.site_testing_checkbox.get()
        )


class ProjectConfigView(CTkXYFrame):
    def __init__(self, subview_frame):
        super().__init__(subview_frame)
        self.project_info_view = subview_frame.master
        self.main_app_data = self.project_info_view.window.main_app.data
        self.is_subview_populated = False

        self.ruleset_model_row_widgets = {}

        self.selected_ruleset = ctk.StringVar()
        self.selected_ruleset.set("ASHRAE 90.1-2019")

        # Initialize Widgets
        self.new_construction_checkbox = None
        self.new_construction_checkbox = ctk.CTkCheckBox(
            self,
            text="All new construction?",
            font=("Arial", 14),
        )
        self.rotation_exception_checkbox = ctk.CTkCheckBox(
            self,
            text="Meets 90.1-2019 Table G3.1(5) Baseline Building Performance (a) Exceptions",
            font=("Arial", 14),
            command=self.toggle_baseline_rotations,
        )
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
            font=("Arial", 14),
        )
        self.note_label = ctk.CTkLabel(
            self, text="Note: ", anchor="e", justify="left", font=("Arial", 16, "bold")
        )
        note_text = "When you select an input file, it is expected that the same directory will also include the simulation output files associated with the selected input file. \nThis application will check for the following associated file extensions:\n(*.nhk), (*.lrp), (*.srp), (*.erp)\n\n(*) can be identical to the selected *.inp file or can include the suffix ' - Baseline Design'"
        self.note = ctk.CTkLabel(
            self, text=note_text, anchor="w", justify="left", font=("Arial", 14)
        )
        # TODO: Add project name field
        self.ruleset_label = ctk.CTkLabel(
            self, text="Energy Code/Program:", font=("Arial", 14, "bold"), anchor="e"
        )
        self.ruleset_models_frame = ctk.CTkFrame(self, width=800, height=250)
        self.ruleset_dropdown = ctk.CTkOptionMenu(
            self,
            values=["ASHRAE 90.1-2019", "None"],
            command=lambda selection: self.update_ruleset_model_frame(
                self.ruleset_models_frame, selection
            ),
        )
        self.ruleset_models_label = ctk.CTkLabel(
            self,
            text="Models: ",
            anchor="e",
            justify="left",
            font=("Arial", 14, "bold"),
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
        self.directions_label.grid(row=0, column=0, sticky="ew", padx=5, pady=20)
        self.directions.grid(row=0, column=1, columnspan=6, sticky="new", pady=20)
        # Row 1
        self.note_label.grid(row=1, column=0, sticky="new", padx=5, pady=20)
        self.note.grid(
            row=1, column=1, columnspan=8, sticky="ew", padx=(5, 20), pady=20
        )
        # Row 2
        self.ruleset_label.grid(row=2, column=0, sticky="e", padx=(20, 5), pady=10)
        self.ruleset_dropdown.grid(
            row=2, column=1, columnspan=2, sticky="ew", padx=5, pady=10
        )
        self.new_construction_checkbox.grid(
            row=2, column=3, sticky="w", padx=5, pady=10
        )
        # Row 3 Placeholder for the rotation exception checkbox
        # Row 4
        self.ruleset_models_label.grid(row=4, column=0, sticky="ew", padx=5, pady=20)

        self.show_ruleset_models(self.ruleset_models_frame)
        self.ruleset_models_frame.grid(row=4, column=1, columnspan=6, sticky="nsew")

        # Populate checkboxes from configuration data
        if self.main_app_data.is_all_new_construction():
            self.new_construction_checkbox.toggle()
            self.new_construction_checkbox.select()
        if self.main_app_data.meets_baseline_exception():
            self.rotation_exception_checkbox.toggle()
            self.rotation_exception_checkbox.select()

    def update_ruleset_model_frame(self, ruleset_models_frame, selected_ruleset):
        self.main_app_data.selected_ruleset.set(selected_ruleset)
        self.rotation_exception_checkbox.grid_remove()
        self.clear_ruleset_models_frame()
        self.show_ruleset_models(ruleset_models_frame)

    def show_ruleset_models(self, parent_frame):
        # Main logic
        if self.main_app_data.selected_ruleset.get() == "ASHRAE 90.1-2019":
            self.rotation_exception_checkbox.grid(
                row=3, column=3, columnspan=4, sticky="w", padx=5, pady=10
            )
            labels = ["Design: ", "Proposed: ", "Baseline: "]
            """PH stands for Placeholder. Used to fill a UI gap when the rotation exception checkbox is checked.
            Label will not be displayed and other widgets in the row will not be created."""
            if not self.rotation_exception_checkbox.get():
                labels.extend(
                    [
                        "Baseline 90: ",
                        "Baseline 180: ",
                        "Baseline 270: ",
                        "PH Baseline 90: ",
                        "PH Baseline 180: ",
                        "PH Baseline 270: ",
                    ]
                )
        else:
            labels = ["Design: "]

        # Create and place rows based on the selected ruleset
        self.create_model_rows(parent_frame, labels)

    def create_model_rows(self, parent_frame, labels):
        """Create and place rows for ruleset model path widgets."""
        for row_num, label_text in enumerate(labels):
            label, path_entry, select_button = self.create_file_row(
                parent_frame, label_text
            )

            # Place widgets using grid
            label.grid(row=row_num, column=0, sticky="ew", padx=5, pady=5)
            path_entry.grid(
                row=row_num, column=1, columnspan=7, sticky="ew", padx=5, pady=5
            )
            select_button.grid(row=row_num, column=8, sticky="ew", padx=5, pady=5)

            # If the label is a placeholder, do not place the widgets. Only place blank label.
            if label_text in [
                "PH Baseline 90: ",
                "PH Baseline 180: ",
                "PH Baseline 270: ",
            ]:
                label.grid_remove()

            # Store created widgets for reuse
            self.ruleset_model_row_widgets[label_text.split(":")[0]] = (
                label,
                path_entry,
                select_button,
            )

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
                "",
            ]:
                if row_widgets[0].winfo_ismapped():
                    # If visible, hide them
                    for widget in row_widgets:
                        widget.grid_remove()
                else:
                    # If hidden, show them
                    for widget in row_widgets:
                        widget.grid()

    def create_file_row(self, parent_frame, label_text):
        """Create a row of widgets without placing them using grid()."""
        if self.ruleset_model_row_widgets.get(label_text.split(":")[0]):
            return self.ruleset_model_row_widgets[label_text.split(":")[0]]

        # If the label is a placeholder, do not place the widgets. Only place blank label.
        if label_text in ["PH Baseline 90: ", "PH Baseline 180: ", "PH Baseline 270: "]:
            label = ctk.CTkLabel(parent_frame, text="")
            return label, label, label

        # Create label
        label = ctk.CTkLabel(
            parent_frame,
            text=label_text,
            font=("Arial", 14),
            width=90,
            anchor="e",  # Align text to the right within the label
        )

        # Create entry, prepopulate project info if selected in project config on startup
        path_entry = ctk.CTkEntry(parent_frame, width=700, font=("Arial", 12))
        label_text = label_text.split(":")[0].replace("Design", "User")
        if self.main_app_data.configuration_data.get(label_text):
            path_entry.insert(0, self.main_app_data.configuration_data[label_text])
            self.main_app_data.ruleset_model_file_paths[label_text] = (
                self.main_app_data.configuration_data[label_text]
            )

        # File select button
        def select_file():
            file_path = filedialog.askopenfilename(
                filetypes=[("eQUEST Input Files", "*.inp")]
            )
            if file_path:
                # Extract parent directory and filename using string parsing
                parts = file_path.rsplit("/", 2)
                if len(parts) > 1:
                    parent_dir = parts[-2]
                    filename = parts[-1]
                    trimmed_path = f"{parent_dir}/{filename}"
                else:
                    trimmed_path = file_path

                # Update the entry with the trimmed path
                path_entry.delete(0, "end")
                path_entry.insert(0, trimmed_path)

                self.main_app_data.ruleset_model_file_paths[
                    label_text.split(":")[0].replace("Design", "User")
                ] = file_path

        select_button = ctk.CTkButton(
            parent_frame, text="Select", command=select_file, width=80, height=30
        )

        return label, path_entry, select_button

    # TODO: When model files are changed, show a button that allows regeneration of the RMDs
    # TODO: When options on this view are changed, show warning
    def validate_project_info(self):
        """Verify that all required file paths have been selected."""
        # Check that at least 1 file path has been selected
        if not any(self.main_app_data.ruleset_model_file_paths.values()):
            self.main_app_data.errors = [
                "At least one file must be selected to continue."
            ]
            self.project_info_view.update_warnings_errors()
            return

        # If the code reaches this point, at least one file is selected so clear any errors
        self.main_app_data.errors.clear()

        # For each file that is selected, make sure that the directory also contains the associated output files
        for (
            model_type,
            file_path,
        ) in self.main_app_data.ruleset_model_file_paths.items():
            if file_path:
                if not self.main_app_data.verify_associated_files(file_path):
                    model_type = model_type.replace("User", "Design")
                    self.main_app_data.errors.append(
                        f"Associated simulation output files not found for the selected '{model_type}' model."
                    )
                    self.project_info_view.update_warnings_errors()

        if len(self.main_app_data.errors) > 0:
            return

        # If the code reaches this point, at least one file is selected and all associated files are found so clear any errors
        self.main_app_data.errors.clear()

        # Required model types
        required_models = ["User", "Proposed", "Baseline"]
        if not self.rotation_exception_checkbox.get():
            required_models.extend(["Baseline 90", "Baseline 180", "Baseline 270"])

        # Check if all required model types have file paths selected
        for model_type in required_models:
            if (
                model_type not in self.main_app_data.ruleset_model_file_paths
                or not self.main_app_data.ruleset_model_file_paths[model_type]
            ):
                model_type = model_type.replace("User", "Design")
                self.main_app_data.warnings.append(
                    f"The '{model_type}' model is missing and is required to evaluate the ASHRAE 90.1-2019 ruleset."
                )

        self.project_info_view.update_warnings_errors()
        # If there are no errors, reload the model files and refresh the GUI data
        self.reload_model_files()

    def reload_model_files(self):
        self.main_app_data.generate_rmds()
