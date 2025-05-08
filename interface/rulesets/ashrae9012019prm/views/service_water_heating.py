import customtkinter as ctk

from interface.base_view import BaseView
from interface.constants import *
from interface.ctk_xyframe import CTkXYFrame
from interface.main_app_data import ASHRAE9012019ModelOptions


class ServiceWaterHeatingView(BaseView):
    button_name = "Service Water\nHeating"
    icon = "misc.png"

    def __init__(self, window):
        super().__init__(window)
        self.main_window = window

        # Header frame for subviews
        self.subview_header_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.current_subview_header = None

        self.view_frame = ctk.CTkFrame(self)
        self.current_subview = None
        self.current_subview_name = None

        # Directions frame holds all directions info and will get 'gridded' within the surfaces view grid
        self.directions_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.directions_label = ctk.CTkLabel(
            self.directions_frame,
            text="Directions: ",
            font=LABEL_FONT,
        )
        # TODO: Don't forget to update directions text
        self.directions_widget = ctk.CTkLabel(
            self.directions_frame,
            text="ASSIGN DIRECTIONS",
            font=LABEL_FONT,
        )
        self.subviews = {
            "Baseline SWHSubview": ServiceWaterHeatingSubview(self.view_frame),
            "Proposed SWHSubview": ServiceWaterHeatingSubview(self.view_frame),
        }
        self.subviews["Baseline SWHSubview"].json_representation = (
            "baseline_service_water_heating"
        )
        self.subviews["Proposed SWHSubview"].json_representation = (
            "proposed_service_water_heating"
        )

    def __repr__(self):
        return "ServiceWaterHeatingView"

    def open_view(self):
        self.toggle_active_button("Service Water\nHeating")
        self.grid_propagate(False)
        self.main_window.show_baseline_proposed_toggle(True)

        self.grid_rowconfigure(2, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Directions
        self.directions_frame.grid(row=0, column=0, sticky=FILL, padx=50, pady=20)
        self.directions_label.grid(row=0, column=0)
        self.directions_widget.grid(row=0, column=1)

        # Subview header row
        self.subview_header_frame.grid(row=1, column=0, sticky=FILL, padx=20)

        # Subview frame
        self.view_frame.grid(row=2, column=0, sticky=FILL, padx=20, pady=PAD20END)
        self.view_frame.grid_rowconfigure(0, weight=1)
        self.view_frame.grid_columnconfigure(0, weight=1)

        current_state = self.app_data.baseline_or_proposed.get()
        self.current_subview_name = current_state + " SWHSubview"
        self.show_subview(current_state + " SWHSubview")

    def show_subview(self, subview_name):
        # Clear previous subview
        if self.current_subview is not None:
            self.current_subview.grid_forget()

        if self.current_subview_header is not None:
            self.current_subview_header.grid_forget()

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

        self.current_subview_header = self.current_subview.header_frame
        self.current_subview_header.grid(row=0, column=0, sticky=FILL)
        self.current_subview.grid(row=0, column=0, sticky=FILL)
        self.current_subview.focus_set()
        self.current_subview.open_subview()

    def get_view_data(self):
        view_data = {}
        for subview in self.subviews.values():
            view_data[subview.json_representation] = subview.get_subview_data()
        return view_data


# TODO: If no service water heating components, hide tab like Surfaces View tab
class ServiceWaterHeatingSubview(CTkXYFrame):
    # Set right after subview is created
    json_representation = None

    def __init__(self, view_frame):
        super().__init__(view_frame)
        self.swh_view = view_frame.master
        self.app_data = self.swh_view.window.main_app.data
        self.header_frame = ctk.CTkFrame(self.swh_view.subview_header_frame)
        if self.app_data.is_all_new_construction.get():
            self.column_widths = [300, 240, 300, 240]
        else:
            self.column_widths = [300, 240, 240, 300, 240]
        self.is_view_populated = False
        self.widget_rows = []

    def __repr__(self):
        return "ServiceWaterHeatingSubview"

    def open_subview(self):
        self.populate_subview() if not self.is_view_populated else None

    def set_column_widths(self):
        for i, width in enumerate(self.column_widths):
            self.grid_columnconfigure(i, minsize=width)
            self.header_frame.grid_columnconfigure(i, minsize=width)

    def populate_subview(self):
        self.add_column_headers()
        self.set_column_widths()

        swh_names = []
        if self.app_data.baseline_or_proposed.get() == "Proposed":
            swh_names += self.app_data.get_rmd(
                ASHRAE9012019ModelOptions.PROPOSED
            ).service_water_heating_distribution_systems
            swh_names += self.app_data.get_rmd(
                ASHRAE9012019ModelOptions.PROPOSED
            ).service_water_heating_equipment
        elif self.app_data.baseline_or_proposed.get() == "Baseline":
            swh_names += self.app_data.get_rmd(
                ASHRAE9012019ModelOptions.BASELINE_0
            ).service_water_heating_distribution_systems
            swh_names += self.app_data.get_rmd(
                ASHRAE9012019ModelOptions.BASELINE_0
            ).service_water_heating_equipment

        for i, swh_name in enumerate(swh_names):
            self.add_row(i, swh_name)

        self.is_view_populated = True

        # Populate with any loaded data if it exists
        self.set_subview_data()

    def add_column_headers(self):
        name_label = ctk.CTkLabel(
            self.header_frame, text="Name/Description", font=LABEL_FONT
        )
        name_label.grid(row=0, column=0, pady=5)
        if not self.app_data.is_all_new_construction.get():
            status_label = ctk.CTkLabel(
                self.header_frame, text="Status", font=LABEL_FONT
            )
            status_label.grid(row=0, column=1, pady=5)
        draw_pattern_label = ctk.CTkLabel(
            self.header_frame, text="Draw Pattern", font=LABEL_FONT
        )
        draw_pattern_label.grid(row=0, column=2, pady=5)
        tank_type_label = ctk.CTkLabel(
            self.header_frame, text="Tank Type", font=LABEL_FONT
        )
        tank_type_label.grid(row=0, column=3, pady=5)
        tank_height_label = ctk.CTkLabel(
            self.header_frame, text="Tank Height (ft)", font=LABEL_FONT
        )
        tank_height_label.grid(row=0, column=4, pady=5)

    def add_row(self, i, swh_name):
        name_label = ctk.CTkLabel(self, text=swh_name)
        name_label.grid(row=(i + 1), column=0, padx=PAD20END, pady=PAD20END, sticky=W)
        if not self.app_data.is_all_new_construction.get():
            status_combo = ctk.CTkComboBox(
                self,
                values=self.app_data.StatusDescriptions,
                state=READONLY,
            )
            status_combo._entry.configure(justify=LEFT)
            status_combo.grid(row=(i + 1), column=1, padx=PAD20END, pady=PAD20END)
        draw_pattern_combo = ctk.CTkComboBox(
            self,
            values=self.app_data.StatusDescriptions,
            state=READONLY,
        )
        draw_pattern_combo._entry.configure(justify=LEFT)
        draw_pattern_combo.grid(row=(i + 1), column=2, padx=PAD20END, pady=PAD20END)
        # TODO: Fix values population
        tank_type_combo = ctk.CTkComboBox(
            self,
            values=self.app_data.StatusDescriptions,
            state=READONLY,
        )
        tank_type_combo._entry.configure(justify=LEFT)
        tank_type_combo.grid(row=(i + 1), column=3, padx=PAD20END, pady=PAD20END)
        tank_height_entry = ctk.CTkEntry(self)
        tank_height_entry.grid(row=(i + 1), column=4, padx=PAD20END, pady=PAD20END)

    def get_subview_data(self):
        return {}

    def set_subview_data(self):
        pass
