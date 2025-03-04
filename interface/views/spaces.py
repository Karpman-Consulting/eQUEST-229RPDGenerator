import threading

import customtkinter as ctk

from interface.CTkScrollableDropdown import CTkScrollableDropdown
from interface.ctk_xyframe import CTkXYFrame
from interface.base_view import BaseView


LABEL_FONT = ("Arial", 14, "bold")
READONLY = "readonly"
LEFT = "left"
E = "e"
W = "w"
FILL = "nsew"
PAD20END = (0, 20)
DROPDOWN_HOVER_COLOR = "#5B9BD5"


class SpacesView(BaseView):
    def __init__(self, window):
        super().__init__(window)

        self.view_frame = ctk.CTkFrame(self)

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
            "Spaces": SpacesSubview(self.view_frame),
        }

    def __repr__(self):
        return "SpacesView"

    def open_view(self):
        self.toggle_active_button("Spaces")
        self.grid_propagate(False)

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

        spaces_view = self.subviews["Spaces"]
        spaces_view.grid(row=0, column=0, sticky=FILL)


class SpacesSubview(CTkXYFrame):
    def __init__(self, view_frame):
        super().__init__(view_frame)
        self.spaces_view = view_frame.master
        self.app_data = self.spaces_view.app_data
        if self.app_data.use_threads:
            thread = threading.Thread(target=self.populate_subview)
            thread.start()
        else:
            self.populate_subview()

    def __repr__(self):
        return "SpacesSubview"

    def populate_subview(self):
        self.add_column_headers()

        for i, space_name in enumerate(self.app_data.rmds[0].space_map.keys()):
            # Add data vars for each space
            self.app_data.lighting_space_type_vars[space_name] = ctk.StringVar()
            # Add widget row for each space
            self.add_row(i, space_name)

    def add_column_headers(self):
        name_label = ctk.CTkLabel(self, text="Name", font=LABEL_FONT)
        name_label.grid(row=0, column=0, padx=PAD20END, pady=5)
        if not self.app_data.is_all_new_construction:
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
        if not self.app_data.is_all_new_construction:
            status_combo = ctk.CTkComboBox(self, state=READONLY)
            status_combo.grid(row=(i + 1), column=1, padx=PAD20END, pady=PAD20END)
            CTkScrollableDropdown(
                status_combo,
                values=self.app_data.StatusDescriptions,
                justify=LEFT,
                hover_color=DROPDOWN_HOVER_COLOR,
            )
        lighting_space_type_combo = ctk.CTkComboBox(
            self,
            variable=self.app_data.lighting_space_type_vars[space_name],
            command=lambda _: self.app_data.insert_to_rpd(
                self.app_data.LightingSpaceMapping2019ASHRAE901TG37, space_name
            ),
            state=READONLY,
        )
        lighting_space_type_combo.grid(
            row=(i + 1), column=2, padx=PAD20END, pady=PAD20END
        )
        CTkScrollableDropdown(
            lighting_space_type_combo,
            values=self.app_data.LightingSpaceDescriptions2019ASHRAE901TG37,
            justify=LEFT,
            hover_color=DROPDOWN_HOVER_COLOR,
        )
        envelope_space_type_combo = ctk.CTkComboBox(self, state=READONLY)
        envelope_space_type_combo.grid(
            row=(i + 1), column=3, padx=PAD20END, pady=PAD20END
        )
        CTkScrollableDropdown(
            envelope_space_type_combo,
            values=self.app_data.EnvelopeSpaceDescriptions2019ASHRAE901,
            justify=LEFT,
            hover_color=DROPDOWN_HOVER_COLOR,
        )
        ventilation_space_type_combo = ctk.CTkComboBox(self, state=READONLY)
        ventilation_space_type_combo.grid(
            row=(i + 1), column=4, padx=PAD20END, pady=PAD20END
        )
        CTkScrollableDropdown(
            ventilation_space_type_combo,
            values=self.app_data.VentilationSpaceDescriptions2019ASHRAE901,
            justify=LEFT,
            hover_color=DROPDOWN_HOVER_COLOR,
        )
        swh_space_type_combo = ctk.CTkComboBox(self, state=READONLY)
        swh_space_type_combo.grid(row=(i + 1), column=5, padx=PAD20END, pady=PAD20END)
        CTkScrollableDropdown(
            swh_space_type_combo,
            values=self.app_data.ServiceWaterHeatingSpaceDescriptions2019ASHRAE901,
            justify=LEFT,
            hover_color=DROPDOWN_HOVER_COLOR,
        )
        lighting_occ_controls_combo = ctk.CTkComboBox(self, state=READONLY)
        lighting_occ_controls_combo.grid(
            row=(i + 1), column=6, padx=PAD20END, pady=PAD20END
        )
        CTkScrollableDropdown(
            lighting_occ_controls_combo,
            values=self.app_data.LightingOccupancyControlDescriptions,
            justify=LEFT,
            hover_color=DROPDOWN_HOVER_COLOR,
        )
        daylighting_controls_combo = ctk.CTkComboBox(self, state=READONLY)
        daylighting_controls_combo.grid(
            row=(i + 1), column=7, padx=PAD20END, pady=PAD20END
        )
        CTkScrollableDropdown(
            daylighting_controls_combo,
            values=self.app_data.LightingDaylightingControlDescriptions,
            justify=LEFT,
            hover_color=DROPDOWN_HOVER_COLOR,
        )
        occ_controls_modeled_checkbox = ctk.CTkCheckBox(self, text="", width=30)
        occ_controls_modeled_checkbox.grid(
            row=(i + 1), column=8, padx=PAD20END, pady=PAD20END
        )
        daylighting_modeled_checkbox = ctk.CTkCheckBox(self, text="", width=30)
        daylighting_modeled_checkbox.grid(
            row=(i + 1), column=9, padx=PAD20END, pady=PAD20END
        )
