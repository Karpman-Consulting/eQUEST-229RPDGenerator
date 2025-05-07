import customtkinter as ctk

from interface.base_view import BaseView
from interface.constants import *
from interface.ctk_xyframe import CTkXYFrame


class ServiceWaterHeatingView(BaseView):
    button_name = "Service Water\nHeating"
    icon = "misc.png"

    def __init__(self, window):
        super().__init__(window)
        self.main_window = window

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

        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Directions
        self.directions_frame.grid(row=0, column=0, sticky=FILL, padx=50, pady=20)
        self.directions_label.grid(row=0, column=0)
        self.directions_widget.grid(row=0, column=1)

        # Subview frame
        self.view_frame.grid(row=1, column=0, sticky=FILL, padx=20, pady=PAD20END)
        self.view_frame.grid_rowconfigure(0, weight=1)
        self.view_frame.grid_columnconfigure(0, weight=1)

        current_state = self.app_data.baseline_or_proposed.get()
        self.current_subview_name = current_state + " SWHSubview"
        self.show_subview(current_state + " SWHSubview")

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

    def get_view_data(self):
        view_data = {}
        for subview in self.subviews.values():
            view_data[subview.json_representation] = subview.get_subview_data()
        return view_data


class ServiceWaterHeatingSubview(CTkXYFrame):
    # Set right after subview is created
    json_representation = None

    def __init__(self, view_frame):
        super().__init__(view_frame)
        self.spaces_view = view_frame.master
        self.app_data = self.spaces_view.app_data
        self.is_view_populated = False
        self.widget_rows = []

    def __repr__(self):
        return "ServiceWaterHeatingSubview"

    def open_subview(self):
        self.populate_subview() if not self.is_view_populated else None

    def populate_subview(self):
        # Create widgets for the subview
        # self.grid_rowconfigure(0, weight=1)
        # self.grid_columnconfigure(0, weight=1)

        # Create widgets here
        # Example: self.label = ctk.CTkLabel(self, text="Example Label")
        # self.label.grid(row=0, column=0, sticky=ctk.W)

        # Add widgets to the widget_rows list
        # Example: self.widget_rows.append(self.label)

        self.is_view_populated = True

        # Populate with any loaded data if it exists
        self.set_subview_data()

    def add_column_headers(self):
        pass

    def add_row(self):
        pass

    def get_subview_data(self):
        return {}

    def set_subview_data(self):
        pass
