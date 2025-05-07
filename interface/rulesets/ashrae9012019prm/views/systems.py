import customtkinter as ctk

import interface.custom_widgets as cw
from interface.ctk_xyframe import CTkXYFrame
from interface.base_view import BaseView
from interface.main_app_data import ASHRAE9012019ModelOptions
from interface.constants import *


class SystemsView(BaseView):
    button_name = "Systems"
    icon = "systems.png"

    def __init__(self, window):
        super().__init__(window)
        self.main_window = window

        # All subviews will be placed inside this frame. Single row/column allows formatting of subview to be handled by the subview itself
        self.subview_frame = ctk.CTkFrame(self)
        self.current_subview = None
        self.current_subview_name = None

        self.subviews = {
            "Baseline HVACSystemSubview": HVACSystemSubview(self.subview_frame),
            "Proposed HVACSystemSubview": HVACSystemSubview(self.subview_frame),
            "Baseline HeatRejectionSubview": HeatRejectionSubview(self.subview_frame),
            "Proposed HeatRejectionSubview": HeatRejectionSubview(self.subview_frame),
        }
        self.subviews["Baseline HVACSystemSubview"].json_representation = (
            "baseline_hvac_systems"
        )
        self.subviews["Proposed HVACSystemSubview"].json_representation = (
            "proposed_hvac_systems"
        )
        self.subviews["Baseline HeatRejectionSubview"].json_representation = (
            "baseline_heat_rejections"
        )
        self.subviews["Proposed HeatRejectionSubview"].json_representation = (
            "proposed_heat_rejections"
        )

        # Directions frame holds all directions info and will get 'gridded' within the surfaces view grid
        self.directions_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.directions_label = ctk.CTkLabel(
            self.directions_frame,
            text="Directions: ",
            font=LABEL_FONT,
        )
        self.directions_widget = ctk.CTkLabel(
            self.directions_frame,
            text="Assign the various data parameters for each system.",
            font=LABEL_FONT,
        )

        self.subview_buttons = {}
        self.border_line = ctk.CTkFrame(self, height=2, fg_color=BLACK)
        self.subview_button_frame = ctk.CTkFrame(
            self, corner_radius=0, fg_color="transparent"
        )
        self.create_subbutton_bar()

    def __repr__(self):
        return "SystemsView"

    def open_view(self):
        self.toggle_active_button("Systems")
        self.grid_propagate(False)
        self.main_window.show_baseline_proposed_toggle(True)

        # 3 rows in the main surface view structure. Subview frame (row 4, index 3) has a weight to make it fill up the empty space in the window
        self.grid_rowconfigure(3, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Directions
        self.directions_frame.grid(row=0, column=0, sticky=FILL, padx=50, pady=20)
        self.directions_label.grid(row=0, column=0)
        self.directions_widget.grid(row=0, column=1)

        # Subview buttons
        self.subview_button_frame.grid(row=1, column=0, sticky=W, padx=20)
        for index, name in enumerate(self.subview_buttons):
            # Layout the button inside the frame
            button = self.subview_buttons[name]
            button.grid(row=0, column=index, padx=(0, 4))

        self.border_line.grid(row=2, column=0, columnspan=5, sticky=E + W, padx=20)

        # Subview frame
        self.subview_frame.grid(row=3, column=0, sticky=FILL, padx=20, pady=PAD20END)
        self.subview_frame.grid_rowconfigure(0, weight=1)
        self.subview_frame.grid_columnconfigure(0, weight=1)

        self.current_subview_name = (
            f"{self.app_data.baseline_or_proposed.get()} HVACSystemSubview"
        )
        self.show_subview(
            f"{self.app_data.baseline_or_proposed.get()} HVACSystemSubview"
        )

    def create_subbutton_bar(self):
        callback_methods = {}
        if len(self.app_data.rmds[0].heat_rejection_names) > 0:
            callback_methods["Heat Rejection"] = lambda: self.show_subview(
                f"{self.app_data.baseline_or_proposed.get()} Heat Rejection"
            )
        if len(self.app_data.rmds[0].system_names) > 0:
            callback_methods["HVAC Systems"] = lambda: self.show_subview(
                f"{self.app_data.baseline_or_proposed.get()} HVAC Systems"
            )

        for name in callback_methods:
            # Create the button to go inside this button frame
            button = ctk.CTkButton(
                self.subview_button_frame,
                text=name,
                fg_color=SUBVIEW_BUTTON_COLOR,
                hover_color=SUBVIEW_BUTTON_COLOR,
                text_color=BLACK,
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

        subview = self.subviews.get(subview_name)
        if subview:
            self.current_subview_name = subview_name
            self.current_subview = subview
        else:
            current_state = self.app_data.baseline_or_proposed.get()
            filtered_subviews = [
                value for key, value in self.subviews.items() if current_state in key
            ]

            # Set current_subview to the first matching subview, if found
            if filtered_subviews:
                self.current_subview = filtered_subviews[0]
                self.current_subview_name = (
                    self.app_data.baseline_or_proposed.get()
                    + " "
                    + self.current_subview.__repr__()
                )

        self.current_subview.grid(row=0, column=0, sticky=FILL)
        self.current_subview.focus_set()
        self.current_subview.open_subview()

    def toggle_active_subbutton(self, active_subbutton_name):
        for name, button in self.subview_buttons.items():
            if name == active_subbutton_name:
                self.subview_buttons[name].configure(
                    fg_color=ACTIVE_SUBVIEW_BUTTON_COLOR,
                    hover_color=ACTIVE_SUBVIEW_BUTTON_COLOR,
                    text_color=BLACK,
                    font=("Arial", 11, "bold"),
                )
            else:
                self.subview_buttons[name].configure(
                    fg_color=SUBVIEW_BUTTON_COLOR,
                    hover_color=SUBVIEW_BUTTON_COLOR,
                    text_color=BLACK,
                    font=("Arial", 11, "bold"),
                )

    def get_view_data(self):
        view_data = {}
        for subview in self.subviews.values():
            view_data[subview.json_representation] = subview.get_subview_data()
        return view_data


class HeatRejectionSubview(CTkXYFrame):
    # Set right after subviews are created in the SystemsView
    json_representation = None

    def __init__(self, subview_frame):
        super().__init__(subview_frame)
        self.systems_view = subview_frame.master
        self.app_data = self.systems_view.window.main_app.data
        self.is_subview_populated = False
        self.widget_rows = []

    def __repr__(self):
        return "HeatRejectionSubview"

    def open_subview(self):
        self.systems_view.main_window.next_button.configure(command=self.view_next)
        self.systems_view.main_window.back_button.configure(command=self.view_back)
        self.systems_view.main_window.show_back_next_buttons_toggle()
        self.systems_view.toggle_active_subbutton("Heat Rejection")
        self.populate_subview() if not self.is_subview_populated else None

    def view_next(self):
        if len(self.app_data.rmds[0].system_names) > 0:
            self.systems_view.show_subview("HVACSystemSubview")
        else:
            self.systems_view.main_window.show_view("MiscellaneousView")

    def view_back(self):
        if "SurfacesView" in self.systems_view.main_window.views:
            self.systems_view.main_window.show_view("SurfacesView")
        else:
            self.systems_view.main_window.show_view("SpacesView")

    def populate_subview(self):
        self.add_column_headers()

        #  Get heat rejections from relevant rmd. Throw error if none found
        heat_rejection_names = []
        if self.app_data.baseline_or_proposed.get() == "Proposed":
            heat_rejection_names = self.app_data.get_rmd(
                ASHRAE9012019ModelOptions.PROPOSED
            ).heat_rejection_names
        elif self.app_data.baseline_or_proposed.get() == "Baseline":
            heat_rejection_names = self.app_data.get_rmd(
                ASHRAE9012019ModelOptions.BASELINE_0
            ).heat_rejection_names

        for i, heat_rejection_name in enumerate(heat_rejection_names):
            self.add_row(i, heat_rejection_name)

        self.is_subview_populated = True

        # Populate with any loaded data if it exists
        self.set_subview_data()

    def add_column_headers(self):
        name_label = ctk.CTkLabel(self, text="Name", font=LABEL_FONT)
        name_label.grid(row=0, column=0, padx=PAD20END, pady=5)
        fan_type_label = ctk.CTkLabel(self, text="Fan Type", font=LABEL_FONT)
        fan_type_label.grid(row=0, column=1, padx=PAD20END, pady=5)

    def add_row(self, i, heat_rejection_name):
        heat_rejection_label = ctk.CTkLabel(self, text=f"{heat_rejection_name}")
        heat_rejection_label.grid(
            row=(i + 1), column=0, padx=PAD20END, pady=PAD20END, sticky=W
        )
        fan_type_combo = ctk.CTkComboBox(
            self, values=self.app_data.HeatRejectionFanDescriptions, state=READONLY
        )
        fan_type_combo._entry.configure(justify=LEFT)
        fan_type_combo.grid(row=(i + 1), column=1, padx=PAD20END, pady=PAD20END)

        self.widget_rows.append(
            [
                heat_rejection_label,
                fan_type_combo,
            ]
        )

    def get_subview_data(self):
        subview_data = []
        for heat_rejection_label, fan_type_combo in self.widget_rows:
            subview_data.append(
                {
                    "Heat Rejection Name": heat_rejection_label.cget("text"),
                    "Fan Type": fan_type_combo.get(),
                }
            )
        return subview_data

    def set_subview_data(self):
        for heat_rejection_label, fan_type_combo in self.widget_rows:
            fan_type = self.get_fan_type_from_hr_name(heat_rejection_label.cget("text"))
            if fan_type:
                # Set the combo box from the saved data. Else keep as default
                fan_type_combo.set(fan_type)

    def get_fan_type_from_hr_name(self, heat_rejection_name):
        heat_rejection_data = self.app_data.all_project_data.get(
            self.json_representation, []
        )
        for heat_rejection in heat_rejection_data:
            if heat_rejection.get("Heat Rejection Name") == heat_rejection_name:
                return heat_rejection.get("Fan Type", None)
        return None


class HVACSystemSubview(CTkXYFrame):
    # Set right after subviews are created in the SystemsView
    json_representation = None

    def __init__(self, subview_frame):
        super().__init__(subview_frame)
        self.systems_view = subview_frame.master
        self.app_data = self.systems_view.window.main_app.data
        self.is_subview_populated = False
        self.widget_rows = []

    def __repr__(self):
        return "HVACSystemSubview"

    def open_subview(self):
        self.systems_view.main_window.next_button.configure(command=self.view_next)
        self.systems_view.main_window.back_button.configure(command=self.view_back)
        self.systems_view.main_window.show_back_next_buttons_toggle()
        self.systems_view.toggle_active_subbutton("HVAC Systems")
        self.populate_subview() if not self.is_subview_populated else None

    def view_next(self):
        self.systems_view.main_window.show_view("MiscellaneousView")

    def view_back(self):
        if len(self.app_data.rmds[0].heat_rejection_names) > 0:
            self.systems_view.show_subview("HeatRejectionSubview")
        elif "SurfacesView" in self.systems_view.main_window.views:
            self.systems_view.main_window.show_view("SurfacesView")
        else:
            self.systems_view.main_window.show_view("SpacesView")

    def populate_subview(self):
        self.add_column_headers()

        #  Get hvac systems from relevant rmd. Throw error if none found
        hvac_system_names = []
        if self.app_data.baseline_or_proposed.get() == "Proposed":
            hvac_system_names = self.app_data.get_rmd(
                ASHRAE9012019ModelOptions.PROPOSED
            ).system_names
        elif self.app_data.baseline_or_proposed.get() == "Baseline":
            hvac_system_names = self.app_data.get_rmd(
                ASHRAE9012019ModelOptions.BASELINE_0
            ).system_names

        for i, hvac_system_name in enumerate(hvac_system_names):
            self.add_row(i, hvac_system_name)

        self.is_subview_populated = True

        # Populate with any loaded data if it exists
        self.set_subview_data()

    def add_column_headers(self):
        name_label = ctk.CTkLabel(self, text="Name", font=LABEL_FONT)
        name_label.grid(row=0, column=0, padx=PAD20END, pady=5)
        dehumidification_type_label = ctk.CTkLabel(
            self, text="Dehumidification Type", font=LABEL_FONT
        )
        dehumidification_type_label.grid(row=0, column=2, padx=PAD20END, pady=5)
        ducted_supply_label = ctk.CTkLabel(self, text="Ducted Supply?", font=LABEL_FONT)
        ducted_supply_label.grid(row=0, column=3, padx=PAD20END, pady=5)
        air_filter_merv_rating_label = ctk.CTkLabel(
            self, text="Air Filter MERV Rating", font=LABEL_FONT
        )
        air_filter_merv_rating_label.grid(row=0, column=4, padx=PAD20END, pady=5)

    def add_row(self, i, hvac_system_name):
        system_label = ctk.CTkLabel(self, text=f"{hvac_system_name}")
        system_label.grid(row=(i + 1), column=0, padx=PAD20END, pady=PAD20END, sticky=W)
        dehumidification_type_combo = ctk.CTkComboBox(
            self,
            values=self.app_data.DehumidificationDescriptions,
            state=READONLY,
        )
        dehumidification_type_combo._entry.configure(justify=LEFT)
        dehumidification_type_combo.grid(
            row=(i + 1), column=2, padx=PAD20END, pady=PAD20END
        )
        ducted_supply_checkbox = ctk.CTkCheckBox(self, text="", width=30)
        ducted_supply_checkbox.grid(row=(i + 1), column=3, padx=PAD20END, pady=PAD20END)
        air_filter_merv_rating_spinbox = cw.IntSpinbox(
            self, width=125, minimum_value=1, maximum_value=16, default_value=8
        )
        air_filter_merv_rating_spinbox.grid(
            row=(i + 1), column=4, padx=PAD20END, pady=PAD20END
        )

        self.widget_rows.append(
            [
                system_label,
                dehumidification_type_combo,
                ducted_supply_checkbox,
                air_filter_merv_rating_spinbox,
            ]
        )

    def get_subview_data(self):
        subview_data = []
        for row in self.widget_rows:
            (
                system_label,
                dehumidification_type_combo,
                ducted_supply_checkbox,
                air_filter_merv_rating_spinbox,
            ) = row
            subview_data.append(
                {
                    "HVAC System Name": system_label.cget("text"),
                    "Dehumidification Type": dehumidification_type_combo.get(),
                    "Ducted Supply": ducted_supply_checkbox.get(),
                    "Air Filter MERV Rating": air_filter_merv_rating_spinbox.get(),
                }
            )
        return subview_data

    def set_subview_data(self):
        for row in self.widget_rows:
            (
                system_label,
                dehumidification_type_combo,
                ducted_supply_checkbox,
                air_filter_merv_rating_spinbox,
            ) = row
            hvac_row_data = self.get_hvac_data(system_label.cget("text"))
            if not hvac_row_data:
                # If no data found for this hvac system, skip it
                continue
            dehumidification_type_combo.set(
                hvac_row_data.get("Dehumidification Type", "")
            )
            ducted_supply = hvac_row_data.get("Ducted Supply", False)
            (
                ducted_supply_checkbox.select()
                if ducted_supply
                else ducted_supply_checkbox.deselect()
            )
            air_filter_merv_rating_spinbox.set(
                hvac_row_data.get("Air Filter MERV Rating", 8)
            )

    def get_hvac_data(self, hvac_system_name):
        """Helper method to get HVAC data from the app_data for a specific HVAC System"""
        hvac_system_data = self.app_data.all_project_data.get(
            self.json_representation, []
        )
        for hvac_system in hvac_system_data:
            if hvac_system.get("HVAC System Name") == hvac_system_name:
                return hvac_system
        return None
