import customtkinter as ctk

from interface.ctk_xyframe import CTkXYFrame
from interface.base_view import BaseView
from interface.main_app_data import ASHRAE9012019ModelOptions
from interface.constants import *


class SpacesView(BaseView):
    button_name = "Spaces"
    icon = "spaces.png"

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
            text="Assign the various space data parameters for each space.",
            font=LABEL_FONT,
        )
        self.subviews = {
            "Baseline SpacesSubview": SpacesSubview(self.view_frame),
            "Proposed SpacesSubview": SpacesSubview(self.view_frame),
        }

    def __repr__(self):
        return "SpacesView"

    def open_view(self):
        self.toggle_active_button("Spaces")
        self.grid_propagate(False)
        self.main_window.show_baseline_proposed_toggle(True)

        # 2 rows in the main surface view structure.
        # View frame (row 2, index 1) has a weight to make it fill up the empty space in the window
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
        self.current_subview_name = current_state + " SpacesSubview"
        self.show_subview(current_state + " SpacesSubview")

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


class SpacesSubview(CTkXYFrame):
    def __init__(self, view_frame):
        super().__init__(view_frame)
        self.spaces_view = view_frame.master
        self.app_data = self.spaces_view.app_data
        self.is_view_populated = False

    def __repr__(self):
        return "SpacesSubview"

    def open_subview(self):
        self.spaces_view.main_window.next_button.configure(command=self.view_next)
        self.spaces_view.main_window.back_button.configure(command=self.view_back)
        self.spaces_view.main_window.show_back_next_buttons_toggle()
        self.populate_subview() if not self.is_view_populated else None

    def view_next(self):
        self.spaces_view.main_window.show_view("SurfacesView")

    def view_back(self):
        self.spaces_view.main_window.show_view("ZonesView")

    def populate_subview(self):
        self.add_column_headers()

        #  Get spaces from relevant rmd. Throw error if none found
        space_names = []
        if self.app_data.baseline_or_proposed.get() == "Proposed":
            space_names = self.app_data.get_rmd(
                ASHRAE9012019ModelOptions.PROPOSED
            ).space_map.keys()
        elif self.app_data.baseline_or_proposed.get() == "Baseline":
            space_names = self.app_data.get_rmd(
                ASHRAE9012019ModelOptions.BASELINE_0
            ).space_map.keys()

        for i, space_name in enumerate(space_names):
            # Add data vars for each space
            self.app_data.lighting_space_type_vars[space_name] = ctk.StringVar()
            # Add widget row for each space
            self.add_row(i, space_name)

        self.is_view_populated = True

    def add_column_headers(self):
        name_label = ctk.CTkLabel(self, text="Name", font=LABEL_FONT)
        name_label.grid(row=0, column=0, padx=PAD20END, pady=5)
        if not self.app_data.is_all_new_construction.get():
            status_label = ctk.CTkLabel(self, text="Status", font=LABEL_FONT)
            status_label.grid(row=0, column=1, padx=PAD20END, pady=5)
        lighting_space_type_label = ctk.CTkLabel(
            self, text="Lighting Space Type", font=LABEL_FONT
        )
        lighting_space_type_label.grid(row=0, column=2, padx=PAD20END, pady=5)
        envelope_space_type_label = ctk.CTkLabel(
            self, text="Envelope Space Type", font=LABEL_FONT
        )
        envelope_space_type_label.grid(row=0, column=3, padx=PAD20END, pady=5)
        ventilation_space_type_label = ctk.CTkLabel(
            self, text="Ventilation Space Type", font=LABEL_FONT
        )
        ventilation_space_type_label.grid(row=0, column=4, padx=PAD20END, pady=5)
        swh_space_type_label = ctk.CTkLabel(
            self, text="SWH Space Type", font=LABEL_FONT
        )
        swh_space_type_label.grid(row=0, column=5, padx=PAD20END, pady=5)
        lighting_occ_controls_label = ctk.CTkLabel(
            self, text="Lighting Occ. Controls", font=LABEL_FONT
        )
        lighting_occ_controls_label.grid(row=0, column=6, padx=PAD20END, pady=5)
        daylighting_controls_label = ctk.CTkLabel(
            self, text="Daylighting Controls", font=LABEL_FONT
        )
        daylighting_controls_label.grid(row=0, column=7, padx=PAD20END, pady=5)
        occ_controls_modeled_via_schedule_label = ctk.CTkLabel(
            self, text="Occ. Controls Modeled via Schedule?", font=LABEL_FONT
        )
        occ_controls_modeled_via_schedule_label.grid(
            row=0, column=8, padx=PAD20END, pady=5
        )
        daylighting_modeled_via_schedule_label = ctk.CTkLabel(
            self, text="Daylighting Modeled via Schedule?", font=LABEL_FONT
        )
        daylighting_modeled_via_schedule_label.grid(
            row=0, column=9, padx=PAD20END, pady=5
        )

    def add_row(self, i, space_name):
        name_label = ctk.CTkLabel(self, text=f"{space_name}")
        name_label.grid(row=(i + 1), column=0, padx=PAD20END, pady=PAD20END, sticky=W)
        if not self.app_data.is_all_new_construction.get():
            status_combo = ctk.CTkComboBox(
                self,
                values=self.app_data.StatusDescriptions,
                state=READONLY,
            )
            status_combo._entry.configure(justify=LEFT)
            status_combo.grid(row=(i + 1), column=1, padx=PAD20END, pady=PAD20END)
        lighting_space_type_combo = ctk.CTkComboBox(
            self,
            values=self.app_data.LightingSpaceDescriptions2019ASHRAE901TG37,
            variable=self.app_data.lighting_space_type_vars[space_name],
            command=lambda _: self.app_data.insert_to_rpd(
                self.app_data.LightingSpaceMapping2019ASHRAE901TG37, space_name
            ),
            state=READONLY,
        )
        lighting_space_type_combo._entry.configure(justify=LEFT)
        lighting_space_type_combo.grid(
            row=(i + 1), column=2, padx=PAD20END, pady=PAD20END
        )
        envelope_space_type_combo = ctk.CTkComboBox(
            self,
            values=self.app_data.EnvelopeSpaceDescriptions2019ASHRAE901,
            state=READONLY,
        )
        envelope_space_type_combo._entry.configure(justify=LEFT)
        envelope_space_type_combo.grid(
            row=(i + 1), column=3, padx=PAD20END, pady=PAD20END
        )
        ventilation_space_type_combo = ctk.CTkComboBox(
            self,
            values=self.app_data.VentilationSpaceDescriptions2019ASHRAE901,
            state=READONLY,
        )
        ventilation_space_type_combo._entry.configure(justify=LEFT)
        ventilation_space_type_combo.grid(
            row=(i + 1), column=4, padx=PAD20END, pady=PAD20END
        )
        swh_space_type_combo = ctk.CTkComboBox(
            self,
            values=self.app_data.ServiceWaterHeatingSpaceDescriptions2019ASHRAE901,
            state=READONLY,
        )
        swh_space_type_combo._entry.configure(justify=LEFT)
        swh_space_type_combo.grid(row=(i + 1), column=5, padx=PAD20END, pady=PAD20END)
        lighting_occ_controls_combo = ctk.CTkComboBox(
            self,
            values=self.app_data.LightingOccupancyControlDescriptions,
            state=READONLY,
        )
        lighting_occ_controls_combo._entry.configure(justify=LEFT)
        lighting_occ_controls_combo.grid(
            row=(i + 1), column=6, padx=PAD20END, pady=PAD20END
        )
        daylighting_controls_combo = ctk.CTkComboBox(
            self,
            values=self.app_data.LightingDaylightingControlDescriptions,
            state=READONLY,
        )
        daylighting_controls_combo._entry.configure(justify=LEFT)
        daylighting_controls_combo.grid(
            row=(i + 1), column=7, padx=PAD20END, pady=PAD20END
        )
        occ_controls_modeled_checkbox = ctk.CTkCheckBox(self, text="", width=30)
        occ_controls_modeled_checkbox.grid(
            row=(i + 1), column=8, padx=PAD20END, pady=PAD20END
        )
        daylighting_modeled_checkbox = ctk.CTkCheckBox(self, text="", width=30)
        daylighting_modeled_checkbox.grid(
            row=(i + 1), column=9, padx=PAD20END, pady=PAD20END
        )
