import customtkinter as ctk

from interface.base_view import BaseView
from interface.constants import *
from interface.ctk_xyframe import CTkXYFrame


class ResultsView(BaseView):
    button_name = "Results"
    icon = "results.png"

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
        self.directions_widget = ctk.CTkLabel(
            self.directions_frame,
            text="Declare your modeled end-uses as regulated or unregulated based on the definitions in  ASHRAE 90.1.",
            font=LABEL_FONT,
        )
        self.subviews = {
            "Baseline ResultsSubview": ResultsSubview(self.view_frame),
            "Proposed ResultsSubview": ResultsSubview(self.view_frame),
        }
        self.subviews["Baseline ResultsSubview"].json_representation = (
            "baseline_results"
        )
        self.subviews["Proposed ResultsSubview"].json_representation = (
            "proposed_results"
        )

    def __repr__(self):
        return "ResultsView"

    def open_view(self):
        self.toggle_active_button("Results")
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
        self.current_subview_name = current_state + " ResultsSubview"
        self.show_subview(current_state + " ResultsSubview")

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


class ResultsSubview(CTkXYFrame):
    # Set right after subview is created
    json_representation = None

    def __init__(self, view_frame):
        super().__init__(view_frame)
        self.spaces_view = view_frame.master
        self.app_data = self.spaces_view.app_data
        self.is_view_populated = False
        self.widget_rows = []

    def __repr__(self):
        return "ResultsSubview"

    def open_subview(self):
        self.populate_subview() if not self.is_view_populated else None

    def populate_subview(self):
        self.add_column_headers()

        end_uses = [
            "Interior Lighting",
            "Fans & Ventilation",
            "Space Heating",
            "Space Cooling",
            "Misc. Equipment",
        ]
        for i, end_use in enumerate(end_uses):
            self.add_row(i, end_use)

        self.is_view_populated = True

        # Populate with any loaded data if it exists
        self.set_subview_data()

    # TODO: Add sticky headers
    def add_column_headers(self):
        end_use_label = ctk.CTkLabel(self, text="End Use", font=LABEL_FONT)
        end_use_label.grid(row=0, column=0, padx=PAD20END, pady=5)
        annual_kwh_label = ctk.CTkLabel(self, text="Annual kWh", font=LABEL_FONT)
        annual_kwh_label.grid(row=0, column=1, padx=PAD20END, pady=5)
        peak_kw_label = ctk.CTkLabel(self, text="Peak kW", font=LABEL_FONT)
        peak_kw_label.grid(row=0, column=2, padx=PAD20END, pady=5)
        annual_cost_label = ctk.CTkLabel(self, text="Annual Cost ($)", font=LABEL_FONT)
        annual_cost_label.grid(row=0, column=3, padx=PAD20END, pady=5)
        regulated_label = ctk.CTkLabel(self, text="Regulated?", font=LABEL_FONT)
        regulated_label.grid(row=0, column=4, padx=PAD20END, pady=5)

    def add_row(self, i, end_use):
        end_use_label = ctk.CTkLabel(self, text=end_use)
        end_use_label.grid(
            row=(i + 1), column=0, padx=PAD20END, pady=PAD20END, sticky=W
        )
        annual_kwh_label = ctk.CTkLabel(self, text="-")
        annual_kwh_label.grid(row=(i + 1), column=1, padx=PAD20END, pady=PAD20END)
        peak_kw_label = ctk.CTkLabel(self, text="-")
        peak_kw_label.grid(row=(i + 1), column=2, padx=PAD20END, pady=PAD20END)
        annual_cost_label = ctk.CTkLabel(self, text="$ - ")
        annual_cost_label.grid(row=(i + 1), column=3, padx=PAD20END, pady=PAD20END)
        regulated_checkbox = ctk.CTkCheckBox(self, text="")
        regulated_checkbox.grid(row=(i + 1), column=4, padx=(50, 0), pady=PAD20END)

    def get_subview_data(self):
        return {}

    def set_subview_data(self):
        pass
