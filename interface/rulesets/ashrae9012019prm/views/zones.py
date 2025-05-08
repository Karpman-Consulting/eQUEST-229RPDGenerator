import customtkinter as ctk
import interface.custom_widgets as cw
from PIL import Image

from interface.CTkToolTip import CTkToolTip
from interface.ctk_xyframe import CTkXYFrame
from interface.base_view import BaseView
from interface.constants import *


class ZonesView(BaseView):
    button_name = "Zones"
    icon = "square.png"

    def __init__(self, window):
        super().__init__(window)
        self.main_window = window

        self.view_frame = ctk.CTkFrame(self)
        self.building_areas_combos = []

        # Directions frame holds all directions info and will get 'gridded' within the surfaces view grid
        self.directions_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.directions_label = ctk.CTkLabel(
            self.directions_frame,
            text="Directions: ",
            anchor=E,
            justify=LEFT,
            font=LABEL_FONT,
        )
        directions_text = "Assign all Zones in your model to the Building Areas created on the previous tab. This can be done by Floor, or more granularly by Zone. If any zones in the \nmodel represent multiple zones in the design, provide the quantity of aggregated zones. If a zone's infiltration in the Proposed model is based on a \nmeasured infiltration rate declare so here."
        self.directions_widget = ctk.CTkLabel(
            self.directions_frame,
            text=directions_text,
            font=LABEL_FONT,
            anchor=W,
            justify=LEFT,
        )
        self.subviews = {
            "Zones": ZonesSubview(self.view_frame),
        }

    def __repr__(self):
        return "ZonesView"

    def open_view(self):
        self.toggle_active_button("Zones")
        self.grid_propagate(False)
        self.main_window.show_baseline_proposed_toggle(False)

        # 2 rows in the main surface view structure.
        # View frame (row 2, index 1) has a weight to make it fill up the empty space in the window
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Directions
        self.directions_frame.grid(row=0, column=0, sticky=FILL, padx=50, pady=20)
        self.directions_label.grid(row=0, column=0, sticky=E + W, padx=5, pady=20)
        self.directions_widget.grid(
            row=0, column=1, columnspan=8, sticky="new", padx=5, pady=20
        )

        # Subview frame
        self.view_frame.grid(row=1, column=0, sticky=FILL, padx=20, pady=PAD20END)
        self.view_frame.grid_rowconfigure(0, weight=1)
        self.view_frame.grid_columnconfigure(0, weight=1)

        zones_view = self.subviews["Zones"]
        zones_view.grid(row=0, column=0, sticky=FILL)
        zones_view.open_view()

        # Update building areas on view open
        for combo in self.building_areas_combos:
            combo.configure(values=self.main_window.main_app.data.building_area_options)

    def get_view_data(self):
        view_data = {}
        for subview in self.subviews.values():
            view_data[subview.json_representation] = subview.get_subview_data()
        return view_data


class ZonesSubview(CTkXYFrame):
    json_representation = "zones"

    def __init__(self, view_frame):
        super().__init__(view_frame)
        self.zones_view = view_frame.master
        self.app_data = self.zones_view.window.main_app.data
        self.is_view_populated = False
        self.zones_by_floor = {}
        self.floor_comboboxes = {}
        self.zone_comboboxes = {}
        self.zone_widgets = {}
        self.collapsed_floors = {}
        self.get_zones_by_floors()

    def __repr__(self):
        return "ZonesSubview"

    def open_view(self):
        self.zones_view.main_window.next_button.configure(command=self.view_next)
        self.zones_view.main_window.back_button.configure(command=self.view_back)
        self.zones_view.main_window.show_back_next_buttons_toggle()
        self.populate_subview() if not self.is_view_populated else None

    def view_next(self):
        self.zones_view.main_window.show_view("SpacesView")

    def view_back(self):
        self.zones_view.main_window.show_view("BuildingAreasView")

    def populate_subview(self):
        self.add_column_headers()

        main_row = 0

        for floor, zones in self.zones_by_floor.items():
            collapse_button = self.add_floor_row(main_row, floor)
            main_row += 1

            for zone in zones:
                self.add_row(main_row, zone)
                main_row += 1

            # Collapse zones immediately after adding them
            self.collapsed_floors[floor] = True
            self.toggle_zone_visibility(floor, collapse_button)

        """Try to populate the subview data after adding all rows. This will ensure that the 
        values in the widgets are in sync with the project data. This should really only happen
        if load data is called. There, the subview will be be marked as non-populated and will 
        call this method again to refresh the data. On initial population (non-load), there should
        not be any data in the project data to populate the widgets with."""
        self.set_subview_data()
        self.is_view_populated = True

    def add_column_headers(self):
        collapse_expand_label = ctk.CTkLabel(self, text="", font=LABEL_FONT)
        collapse_expand_label.grid(row=0, column=0, padx=PAD20END, pady=5)

        zone_floor_label = ctk.CTkLabel(self, text="Floor/Zone", font=LABEL_FONT)
        zone_floor_label.grid(row=0, column=1, padx=PAD20END, pady=5)
        building_area_label = ctk.CTkLabel(self, text="Building Area", font=LABEL_FONT)
        building_area_label.grid(row=0, column=2, padx=PAD20END, pady=5)
        aggregated_zone_quantity_label = ctk.CTkLabel(
            self, text="Aggregated Zone Qty", font=LABEL_FONT
        )
        aggregated_zone_quantity_label.grid(row=0, column=3, padx=PAD20END, pady=5)
        measured_infiltration_rate_label = ctk.CTkLabel(
            self, text="Measured Infiltration Rate?", font=LABEL_FONT
        )
        measured_infiltration_rate_label.grid(row=0, column=4, padx=PAD20END, pady=5)

    def add_floor_row(self, i, floor_name):
        # Frame spanning all columns with a different background color
        floor_row_frame = ctk.CTkFrame(self, fg_color=GRAY30)
        floor_row_frame.grid(row=(i + 1), column=0, columnspan=6, sticky=E + W)

        collapse_button = ctk.CTkButton(
            self,
            text="−",  # Default to expanded state
            width=30,
            height=30,
            corner_radius=10,
            command=lambda: self.toggle_zone_visibility(floor_name, collapse_button),
            bg_color=GRAY30,  # Same color as the frame
        )
        collapse_button_tooltip = CTkToolTip(
            collapse_button,
            message="Show/hide zones on this floor",
        )
        collapse_button.grid(row=(i + 1), column=0, padx=(5, 0))

        # Ensure the frame stretches across all columns
        for col in range(5):
            floor_row_frame.grid_columnconfigure(col, weight=1)

        floor_label = ctk.CTkLabel(
            self,
            text=f"{floor_name}",
            width=135,
            anchor=W,
            font=LABEL_FONT,
            text_color="white",
            bg_color=GRAY30,  # Same color as the frame
        )
        floor_label.grid(row=(i + 1), column=1, padx=20, pady=10, sticky=W)

        # Place the Building Area ComboBox in `self` (not inside `main_row_frame`) to align properly
        building_area_combo = ctk.CTkComboBox(
            self,
            values=self.app_data.building_area_options,
            state=READONLY,
            fg_color=FLOOR_COMBOBOX_COLOR,
            border_color=FLOOR_COMBOBOX_COLOR,
            button_color=FLOOR_COMBOBOX_BTN_COLOR,
            dropdown_fg_color=FLOOR_COMBOBOX_COLOR,
            dropdown_hover_color=LIGHTBLUE,
            bg_color=GRAY30,  # Same color as the frame
            command=lambda value, floor=floor_name: self.set_default_value_by_floor(
                floor, value
            ),
        )
        building_area_combo.set(self.app_data.building_area_options[0])
        building_area_tooltip = CTkToolTip(
            building_area_combo,
            message="Select the building area for all zones on this floor",
        )
        building_area_combo._entry.configure(justify=LEFT)
        building_area_combo.grid(row=(i + 1), column=2, padx=PAD20END, pady=10)

        self.floor_comboboxes[floor_name] = building_area_combo

        # Add empty labels in `main_row_frame` for spacing
        ctk.CTkLabel(floor_row_frame, text="").grid(
            row=0, column=3, padx=PAD20END, pady=PAD10SYM
        )
        ctk.CTkLabel(floor_row_frame, text="").grid(
            row=0, column=4, padx=PAD20END, pady=PAD10SYM
        )

        return collapse_button

    def add_row(self, i, zone_name):
        floor_label = ctk.CTkLabel(self, text=f"{zone_name}")
        floor_label.grid(row=(i + 1), column=1, padx=20, pady=PAD10SYM, sticky=W)
        building_area_combo = ctk.CTkComboBox(
            self,
            values=self.app_data.building_area_options,
            state=READONLY,
        )
        building_area_combo.set(self.app_data.building_area_options[0])
        building_area_tooltip = CTkToolTip(
            building_area_combo,
            message="Select the building area for this zone",
        )
        building_area_combo._entry.configure(justify=LEFT)
        building_area_combo.grid(row=(i + 1), column=2, padx=PAD20END, pady=PAD10SYM)
        self.zones_view.building_areas_combos.append(building_area_combo)

        self.zone_comboboxes[zone_name] = building_area_combo
        # TODO: Apply numerical entry validation
        # TODO: Add tooltip support
        aggregated_zone_qty_spinbox = cw.IntSpinbox(self, width=125, default_value=1)
        aggregated_zone_tooltip = CTkToolTip(
            aggregated_zone_qty_spinbox,
            message="Enter the number of zones comprising this zone",
        )
        aggregated_zone_qty_spinbox.grid(
            row=(i + 1), column=3, padx=PAD20END, pady=PAD10SYM, sticky=FILL
        )
        measured_infiltration_rate_checkbox = ctk.CTkCheckBox(self, text="", width=30)
        measured_infiltration_rate_tooltip = CTkToolTip(
            measured_infiltration_rate_checkbox,
            message="Check if the zone's infiltration is based on a measured rate",
        )
        measured_infiltration_rate_checkbox.grid(
            row=(i + 1), column=4, padx=PAD20END, pady=PAD10SYM
        )

        self.zone_widgets[zone_name] = [
            floor_label,
            building_area_combo,
            aggregated_zone_qty_spinbox,
            measured_infiltration_rate_checkbox,
        ]

    def get_subview_data(self):
        subview_data = []
        for zone_name, widgets in self.zone_widgets.items():
            (
                building_area_combo,
                aggregated_zone_qty_spinbox,
                measured_infiltration_rate_checkbox,
            ) = widgets[1:]
            zone_data = {
                "Zone Name": zone_name,
                "Floor": self.get_floor_from_zone(zone_name),
                "Building Area": building_area_combo.get(),
                "Aggregated Zone Quantity": aggregated_zone_qty_spinbox.get(),
                "Measured Infiltration": measured_infiltration_rate_checkbox.get(),
            }
            subview_data.append(zone_data)
        return subview_data

    def set_subview_data(self):
        # TODO: Set floor row data
        for zone_name, widgets in self.zone_widgets.items():
            zone_row_data = self.get_zone_from_project_data(zone_name)
            if not zone_row_data:
                # If no data found for this zone, skip it
                continue
            (
                building_area_combo,
                aggregated_zone_qty_spinbox,
                measured_infiltration_rate_checkbox,
            ) = widgets[1:]
            building_area_combo.set(
                zone_row_data.get(
                    "Building Area", self.app_data.building_area_options[0]
                )
            )
            aggregated_zone_qty_spinbox.set(
                zone_row_data.get("Aggregated Zone Quantity", 1)
            )
            uses_measured_infiltration = zone_row_data.get(
                "Measured Infiltration", False
            )
            (
                measured_infiltration_rate_checkbox.select()
                if uses_measured_infiltration
                else measured_infiltration_rate_checkbox.deselect()
            )

    def get_zone_from_project_data(self, zone_name):
        """Helper method to get zone data from the main application project data."""
        zone_data = self.app_data.all_project_data.get("zones", [])
        for zone in zone_data:
            if zone.get("Zone Name") == zone_name:
                return zone
        return None

    def get_zones_by_floors(self):
        for zone_name in self.app_data.rmds[0].zone_names:
            zone_obj = self.app_data.rmds[0].get_obj(zone_name)
            if self.zones_by_floor.get(zone_obj.floor_name):
                self.zones_by_floor[zone_obj.floor_name].append(zone_name)
            else:
                self.zones_by_floor[zone_obj.floor_name] = [zone_name]

    def get_floor_from_zone(self, zone_name):
        zone_obj = self.app_data.rmds[0].get_obj(zone_name)
        return zone_obj.floor_name if zone_obj else None

    def set_default_value_by_floor(self, floor_name, selected_value):
        """Update all zones under a floor with the selected value from the floor's combobox"""
        for zone_name in self.app_data.rmds[0].zone_names:
            zone_obj = self.app_data.rmds[0].get_obj(zone_name)
            if zone_obj.floor_name == floor_name:
                if zone_name in self.zone_comboboxes:
                    self.zone_comboboxes[zone_name].set(selected_value)

    def toggle_zone_visibility(self, floor_name, button):
        """Toggles visibility of all zone rows under a given floor"""
        if floor_name in self.zones_by_floor:
            is_collapsed = self.collapsed_floors.get(floor_name, True)

            for zone_name in self.zones_by_floor[floor_name]:
                if zone_name in self.zone_widgets:
                    for widget in self.zone_widgets[zone_name]:
                        if is_collapsed:
                            widget.grid_remove()
                        else:
                            widget.grid()

            button.configure(text="+" if is_collapsed else "−")
            # Update collapse state
            self.collapsed_floors[floor_name] = not is_collapsed
