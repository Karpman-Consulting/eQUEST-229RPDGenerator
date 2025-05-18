import customtkinter as ctk
from PIL import Image

import interface.custom_widgets as cw
from interface.CTkToolTip import CTkToolTip
from interface.ctk_xyframe import CTkXYFrame
from interface.base_view import BaseView
from interface.CTkMessagebox import CTkMessagebox
from interface.constants import *

BPF_AREA_OPTIONS = [
    "Multifamily",
    "Healthcare/hospital",
    "Hotel/motel",
    "Office",
    "Restaurant",
    "Retail",
    "School",
    "Warehouse",
    "All others",
]


class BuildingAreasView(BaseView):
    button_name = "Building Areas"
    icon = "building_areas.png"

    def __init__(self, window):
        super().__init__(window)
        self.main_window = window

        self.building_combos = []
        self.building_widgets_by_row = []
        self.building_area_widgets_by_row = []

        # All subviews will be placed inside this frame.
        # Single row/column allows formatting of subview to be handled by the subview itself
        self.subview_frame = ctk.CTkFrame(self)
        self.current_subview = None

        self.subviews = {
            "Buildings": BuildingSubview(self.subview_frame),
            "Building Areas": BuildingAreasSubview(self.subview_frame),
        }
        self.subview_buttons = {}

        # Directions frame holds all directions info and will get 'gridded' within the surfaces view grid
        self.directions_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.directions_label = ctk.CTkLabel(
            self.directions_frame,
            text="Directions: ",
            anchor=E,
            justify=LEFT,
            font=LABEL_FONT,
        )
        directions_text = "Create Buildings and Building Areas as needed to describe your project. A building area is a group of spaces that share a building area type. A Building Area \nmay span more than one floor. There may be multiple Building Areas on a single floor. For best results, define buildings first."
        self.directions_widget = ctk.CTkLabel(
            self.directions_frame,
            text=directions_text,
            font=LABEL_FONT,
            anchor=W,
            justify=LEFT,
        )
        self.subviews = {
            "Buildings": BuildingSubview(self.subview_frame),
            "Building Areas": BuildingAreasSubview(self.subview_frame),
        }

        # Subview buttons
        self.border_line = ctk.CTkFrame(self, height=2, fg_color=BLACK)
        self.subview_button_frame = ctk.CTkFrame(
            self, corner_radius=0, fg_color="transparent"
        )
        self.create_subbutton_bar()

        if not hasattr(self.app_data, "buildings") or not self.app_data.buildings:
            self.app_data.buildings = {
                "Building 1": {
                    "above_grade_floors": 0,
                    "below_grade_floors": 0,
                    "areas": {},
                }
            }

    def __repr__(self):
        return "BuildingAreasView"

    def open_view(self):
        self.toggle_active_button("Building Areas")
        self.grid_propagate(False)
        self.main_window.show_baseline_proposed_toggle(False)

        # 2 rows in the main surface view structure.
        # View frame (row 2, index 1) has a weight to make it fill up the empty space in the window
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

        if self.subview_buttons:
            # Open the first subview available
            self.show_subview(next(iter(self.subview_buttons)))

    def remove_widgets(self, widgets):
        for widget in widgets:
            widget.grid_remove()
        if widgets in self.building_widgets_by_row:
            self.building_widgets_by_row.remove(widgets)
        if widgets in self.building_area_widgets_by_row:
            self.building_area_widgets_by_row.remove(widgets)

    def get_building_area_name(self, building_name):
        existing_areas = self.app_data.buildings.get(building_name, {}).get("areas", {})
        default_num = len(existing_areas) + 1
        area_name_default = f"{building_name} Area {default_num}"
        while area_name_default in existing_areas:
            default_num += 1
            area_name_default = f"{building_name} Area {default_num}"
        return area_name_default

    def remove_building_area(self, building_name, area_name):
        try:
            del self.app_data.buildings[building_name]["areas"][area_name]
        except KeyError:
            pass

    def add_building_area(self, building_name, area_name, data=None):
        if building_name in self.app_data.buildings:
            self.app_data.buildings[building_name]["areas"][area_name] = data or {}

    def add_or_update_building(
        self, building_name, above_grade_floors, below_grade_floors
    ):
        if building_name not in self.app_data.buildings:
            self.app_data.buildings[building_name] = {
                "above_grade_floors": above_grade_floors,
                "below_grade_floors": below_grade_floors,
                "areas": {},
            }
        else:
            self.app_data.buildings[building_name][
                "above_grade_floors"
            ] = above_grade_floors
            self.app_data.buildings[building_name][
                "below_grade_floors"
            ] = below_grade_floors

    def remove_building(self, building_name):
        self.app_data.buildings.pop(building_name, None)

    def building_has_areas(self, building_name):
        return bool(self.app_data.buildings.get(building_name, {}).get("areas"))


class BuildingSubview(CTkXYFrame):
    json_representation = "buildings"

    def __init__(self, view_frame):
        super().__init__(view_frame)
        self.building_areas_view = view_frame.master
        self.app_data = self.building_areas_view.app_data
        self.is_view_populated = False
        self.building_count = 0

        self.add_building_button = ctk.CTkButton(
            self,
            text="Add Building",
            width=200,
            corner_radius=10,
            command=lambda: self.add_row(self.building_count + 1),
        )

    def __repr__(self):
        return "BuildingSubview"

    def open_subview(self):
        self.building_areas_view.toggle_active_subbutton("Buildings")
        self.populate_subview() if not self.is_view_populated else None

    def populate_subview(self):
        self.add_column_headers()
        self.add_row(self.building_count + 1, is_first_row=True)
        # If there is more than one building in the loaded data, add them to the view and load saved data
        loaded_buildings = self.app_data.interface_data.get("buildings", [])
        if len(loaded_buildings) > 1:
            for _ in range(1, len(loaded_buildings)):
                self.add_row(self.building_count + 1)
        self.set_subview_data()
        self.is_view_populated = True

    def add_column_headers(self):
        building_name_label = ctk.CTkLabel(self, text="Building Name", font=LABEL_FONT)
        building_name_label.grid(row=0, column=0, padx=PAD20END, pady=5)
        above_grade_floors_label = ctk.CTkLabel(
            self, text="# Floors Above Grade", font=LABEL_FONT
        )
        above_grade_floors_label.grid(row=0, column=1, padx=PAD20END, pady=5)
        below_grade_floors_label = ctk.CTkLabel(
            self, text="# Floors Below Grade", font=LABEL_FONT
        )
        below_grade_floors_label.grid(row=0, column=2, padx=PAD20END, pady=5)

    def add_row(self, row, is_first_row=False):
        def remove_row():
            building_name = building_name_entry.get()

            if building_name and self.building_areas_view.building_has_areas(
                building_name
            ):
                msg = CTkMessagebox(
                    title="Warning",
                    message=f"{building_name} has areas assigned to it. This will remove the {building_name} and all associated areas. Would you like to continue?",
                    icon="warning",
                    option_1="No",
                    option_2="Yes",
                )
                if msg.get() == "No":
                    return

            self.building_areas_view.remove_building(building_name_entry.get())
            self.building_areas_view.remove_widgets(row_widgets)
            if remove_button:
                remove_button.grid_remove()

        building_name_entry = ctk.CTkEntry(self)
        building_name_tooltip = CTkToolTip(
            building_name_entry,
            message="Enter name for the building",
        )
        building_name_entry.grid(row=row, column=0, padx=PAD20END, pady=PAD20END)

        if is_first_row and self.app_data.buildings:
            building_name_entry.insert(0, next(iter(self.app_data.buildings)))

        remove_button = None
        if not is_first_row:
            remove_image = ctk.CTkImage(
                light_image=Image.open(
                    f"{self.building_areas_view.main_window.static_filepath}/white_x.png"
                ),
                dark_image=None,
                size=(10, 10),
            )
            remove_button = ctk.CTkButton(
                self,
                text="",
                image=remove_image,
                width=28,
                corner_radius=10,
                fg_color="red",
                hover_color="darkred",
                command=remove_row,
            )
            remove_button.grid(row=row, column=3, padx=PAD20END, pady=PAD20END)

        # TODO: Customize spinboxes to allow validation
        # TODO: Customize spinboxes to support tooltips
        above_grade_spinbox = cw.IntSpinbox(self)
        above_grade_tooltip = CTkToolTip(
            above_grade_spinbox,
            message="Enter number of floors above grade for the building",
        )
        above_grade_spinbox.grid(row=row, column=1, padx=PAD20END, pady=PAD20END)
        below_grade_spinbox = cw.IntSpinbox(self)
        below_grade_tooltip = CTkToolTip(
            below_grade_spinbox,
            message="Enter number of floors below grade for the building",
        )
        below_grade_spinbox.grid(row=row, column=2, padx=PAD20END, pady=PAD20END)

        self.add_building_button.grid(
            row=(row + 1),
            column=0,
            columnspan=2,
            sticky=FILL,
            padx=PAD20END,
            pady=PAD20END,
        )
        self.building_count += 1

        # Add widgets to the list for later access
        row_widgets = [building_name_entry, above_grade_spinbox, below_grade_spinbox]
        self.building_areas_view.building_widgets_by_row.append(row_widgets)

    def save_buildings(self):
        available_buildings = []
        for row_widgets in self.building_areas_view.building_widgets_by_row:
            building_name_entry, above_grade_spinbox, below_grade_spinbox = row_widgets
            if building_name_entry.get():
                # Add or update building in app_data
                available_buildings.append(building_name_entry.get())
                self.building_areas_view.add_or_update_building(
                    building_name_entry.get(),
                    above_grade_spinbox.get(),
                    below_grade_spinbox.get(),
                )
        # Check for duplicate building names
        if len(available_buildings) != len(set(available_buildings)):
            CTkMessagebox(
                title="Error",
                message="Duplicate building names found. Please ensure all building names are unique.",
                icon="warning",
            )
            return
        # Remove buildings from app_data that are not in the list of available buildings
        for building_name in list(self.app_data.buildings.keys()):
            if building_name not in available_buildings:
                self.building_areas_view.remove_building(building_name)
        # Update building combo options in the building areas subview
        for combo in self.building_areas_view.building_combos:
            combo.configure(values=list(self.app_data.buildings.keys()))
        if self.building_areas_view.building_combos:
            self.building_areas_view.building_combos[0].set(
                list(self.app_data.buildings.keys())[0]
            )
        # Update first building area name, based on the first building in the list
        if self.building_areas_view.building_area_widgets_by_row:
            first_building_area_row = (
                self.building_areas_view.building_area_widgets_by_row[0]
            )
            building_name_combo = first_building_area_row[0]
            area_name_entry = first_building_area_row[1]
            if building_name_combo.get() and not area_name_entry.get():
                # Update the area name entry with the new default building area name
                area_name_entry.insert(
                    0,
                    self.building_areas_view.get_building_area_name(
                        building_name_combo.get()
                    ),
                )

    def get_subview_data(self):
        subview_data = []
        for row in self.building_areas_view.building_widgets_by_row:
            building_name_entry, above_grade_spinbox, below_grade_spinbox = row
            building_data = {
                "Building Name": building_name_entry.get(),
                "Floors Above Grade": above_grade_spinbox.get(),
                "Floors Below Grade": below_grade_spinbox.get(),
            }
            subview_data.append(building_data)
        return subview_data

    def set_subview_data(self):
        # Check that number of rows in the view matches the number of buildings in the app_data
        building_data = self.app_data.interface_data.get("buildings", [])
        if not len(building_data) == len(
            self.building_areas_view.building_widgets_by_row
        ):
            # Mismatch in the number of buildings and rows, cannot set subview data
            return
        for index, row in enumerate(self.building_areas_view.building_widgets_by_row):
            building_name_entry, above_grade_spinbox, below_grade_spinbox = row
            building_name_entry.delete(0, "end")
            building_name_entry.insert(0, building_data[index].get("Building Name", ""))
            above_grade_spinbox.set(building_data[index].get("Floors Above Grade", 0))
            below_grade_spinbox.set(building_data[index].get("Floors Below Grade", 0))


class BuildingAreasSubview(CTkXYFrame):
    json_representation = "building_areas"

    def __init__(self, view_frame):
        super().__init__(view_frame)
        self.building_areas_view = view_frame.master
        self.app_data = self.building_areas_view.app_data
        self.is_view_populated = False

        self.building_area_count = 0

        self.add_area_button = ctk.CTkButton(
            self,
            text="Add Building Area",
            width=200,
            corner_radius=10,
            command=lambda: self.add_row(self.building_area_count + 1),
        )

    def __repr__(self):
        return "BuildingAreasSubview"

    def open_subview(self):
        self.building_areas_view.toggle_active_subbutton("Building Areas")
        self.populate_subview() if not self.is_view_populated else None

    def populate_subview(self):
        self.add_column_headers()
        self.add_row(self.building_area_count + 1, is_first_row=True)
        # If there is more than one building area in the loaded data, add them to the view
        loaded_building_areas = self.app_data.interface_data.get("building_areas", [])
        if len(loaded_building_areas) > 1:
            for _ in range(1, len(loaded_building_areas)):
                self.add_row(self.building_area_count + 1)
        self.set_subview_data()
        self.is_view_populated = True

    def add_column_headers(self):
        building_name_label = ctk.CTkLabel(self, text="Building Name", font=LABEL_FONT)
        building_name_label.grid(row=0, column=0, padx=PAD20END, pady=5)
        building_name_tooltip = CTkToolTip(
            building_name_label,
            message="Select the building associated with this area",
        )
        area_name_label = ctk.CTkLabel(self, text="Building Area Name", font=LABEL_FONT)
        area_name_label.grid(row=0, column=1, padx=PAD20END, pady=5)

        if not self.app_data.is_all_new_construction.get():
            status_label = ctk.CTkLabel(self, text="All New?", font=LABEL_FONT)
            status_label.grid(row=0, column=2, padx=PAD20END, pady=5)

        fenestration_type_label = ctk.CTkLabel(
            self, text="Fenestration Area Type", font=LABEL_FONT
        )
        fenestration_type_label.grid(row=0, column=3, padx=PAD20END, pady=5)
        lighting_type_label = ctk.CTkLabel(
            self, text="Lighting Area Type", font=LABEL_FONT
        )
        lighting_type_label.grid(row=0, column=4, padx=PAD20END, pady=5)
        hvac_area_type_label = ctk.CTkLabel(
            self, text="HVAC Area Type", font=LABEL_FONT
        )
        hvac_area_type_label.grid(row=0, column=5, padx=PAD20END, pady=5)
        bpf_area_type_label = ctk.CTkLabel(self, text="BPF Area Type", font=LABEL_FONT)
        bpf_area_type_label.grid(row=0, column=6, padx=PAD20END, pady=5)

    def add_row(self, row, is_first_row=False):
        def populate_area_name(value):
            if building_name_combo.get() in self.app_data.buildings:
                if (
                    area_name_entry.get()
                    not in self.app_data.buildings[building_name_combo.get()]["areas"]
                ):
                    area_name_entry.delete(0, "end")
                    area_name_entry.insert(
                        0, self.building_areas_view.get_building_area_name(value)
                    )

        def update_building_area(new_area_name):
            building_name = building_name_combo.get()
            current_area_name = area_name_entry.get()
            if building_name and current_area_name:
                self.building_areas_view.remove_building_area(
                    building_name, current_area_name
                )
            if (
                building_name
                and new_area_name
                and new_area_name not in self.app_data.buildings[building_name]["areas"]
            ):
                self.building_areas_view.add_building_area(building_name, new_area_name)

            return True

        def remove_row():
            # Remove building area from app_data
            building_name = building_name_combo.get()
            if area_name_entry.get():
                self.building_areas_view.remove_building_area(
                    building_name, area_name_entry.get()
                )
            for widget in row_widgets:
                widget.grid_remove()
            self.building_areas_view.building_area_widgets_by_row.remove(row_widgets)

        vcmd = self.register(update_building_area)
        building_name_combo = ctk.CTkComboBox(
            self,
            values=list(self.app_data.buildings.keys()),
            command=populate_area_name,
            state=READONLY,
        )
        building_name_combo._entry.configure(justify=LEFT)
        building_name_combo.grid(row=row, column=0, padx=PAD20END, pady=PAD20END)
        self.building_areas_view.building_combos.append(building_name_combo)
        area_name_entry = ctk.CTkEntry(
            self, validate="key", validatecommand=(vcmd, "%P")
        )
        area_name_entry.grid(row=row, column=1, padx=PAD20END, pady=PAD20END)
        status_checkbox = None

        if is_first_row and self.app_data.buildings:
            default_building = next(iter(self.app_data.buildings))
            building_name_combo.set(default_building)
            default_area_name = self.building_areas_view.get_building_area_name(
                default_building
            )
            area_name_entry.insert(0, default_area_name)

        if not self.app_data.is_all_new_construction.get():
            status_checkbox = ctk.CTkCheckBox(self, text="", width=30)
            status_checkbox.grid(row=row, column=2, padx=(0, 10), pady=PAD20END)

        fenestration_type_combo = ctk.CTkComboBox(
            self,
            values=self.app_data.VerticalFenestrationBuildingAreaDescriptions2019ASHRAE901,
            state=READONLY,
        )
        fenestration_type_combo._entry.configure(justify=LEFT)
        fenestration_type_combo.grid(row=row, column=3, padx=PAD20END, pady=PAD20END)
        lighting_type_combo = ctk.CTkComboBox(
            self,
            values=self.app_data.LightingBuildingAreaDescriptions2019ASHRAE901T951TG38,
            state=READONLY,
        )
        lighting_type_combo._entry.configure(justify=LEFT)
        lighting_type_combo.grid(row=row, column=4, padx=PAD20END, pady=PAD20END)
        hvac_area_combo = ctk.CTkComboBox(
            self,
            values=self.app_data.HeatingVentilatingAirConditioningBuildingAreaDescriptions2019ASHRAE901,
            state=READONLY,
        )
        hvac_area_combo._entry.configure(justify=LEFT)
        hvac_area_combo.grid(row=row, column=5, padx=PAD20END, pady=PAD20END)
        bpf_area_combo = ctk.CTkComboBox(
            self,
            values=BPF_AREA_OPTIONS,
            state=READONLY,
        )
        bpf_area_combo._entry.configure(justify=LEFT)
        bpf_area_combo.grid(row=row, column=6, padx=PAD20END, pady=PAD20END)

        # Add widgets to the list for later access
        row_widgets = [
            building_name_combo,
            area_name_entry,
            fenestration_type_combo,
            lighting_type_combo,
            hvac_area_combo,
            bpf_area_combo,
        ]

        if not is_first_row:
            remove_image = ctk.CTkImage(
                light_image=Image.open(
                    f"{self.building_areas_view.main_window.static_filepath}/white_x.png"
                ),
                dark_image=None,
                size=(10, 10),
            )
            remove_button = ctk.CTkButton(
                self,
                text="",
                image=remove_image,
                width=28,
                corner_radius=10,
                fg_color="red",
                hover_color="darkred",
                command=remove_row,
            )
            remove_button.grid(row=row, column=7, padx=PAD20END, pady=PAD20END)
            row_widgets.append(remove_button)

        self.add_area_button.grid(
            row=(row + 1),
            column=0,
            columnspan=2,
            sticky=FILL,
            padx=PAD20END,
            pady=PAD20END,
        )

        if not self.app_data.is_all_new_construction.get():
            row_widgets.append(status_checkbox)

        self.building_areas_view.building_area_widgets_by_row.append(row_widgets)

        self.building_area_count += 1

    def get_subview_data(self):
        subview_data = []
        for row in self.building_areas_view.building_area_widgets_by_row:
            (
                building_name_combo,
                area_name_entry,
                fenestration_type_combo,
                lighting_type_combo,
                hvac_area_combo,
                bpf_area_combo,
            ) = row[:6]
            building_data = {
                "Building Name": building_name_combo.get(),
                "Building Area Name": area_name_entry.get(),
                "Fenestration Area Type": fenestration_type_combo.get(),
                "Lighting Area Type": lighting_type_combo.get(),
                "HVAC Area Type": hvac_area_combo.get(),
                "BPF Area Type": bpf_area_combo.get(),
            }
            if not self.app_data.is_all_new_construction:
                building_data["All New"] = row[6].get()
            subview_data.append(building_data)
        return subview_data

    def set_subview_data(self):
        # Check that number of rows in the view matches the number of building areas in the app_data
        building_area_data = self.app_data.interface_data.get("building_areas", [])
        if not len(building_area_data) == len(
            self.building_areas_view.building_area_widgets_by_row
        ):
            # Mismatch in the number of building areas and rows, cannot set subview data
            return
        for index, row in enumerate(
            self.building_areas_view.building_area_widgets_by_row
        ):
            (
                building_name_combo,
                area_name_entry,
                fenestration_type_combo,
                lighting_type_combo,
                hvac_area_combo,
                bpf_area_combo,
            ) = row[:6]
            if not self.app_data.is_all_new_construction:
                status_checkbox = row[6]
            else:
                status_checkbox = None
            area_data = building_area_data[index]
            building_name_combo.set(area_data.get("Building Name", ""))
            area_name_entry.delete(0, "end")
            area_name_entry.insert(0, area_data.get("Building Area Name", ""))
            fenestration_type_combo.set(area_data.get("Fenestration Area Type", ""))
            lighting_type_combo.set(area_data.get("Lighting Area Type", ""))
            hvac_area_combo.set(area_data.get("HVAC Area Type", ""))
            bpf_area_combo.set(area_data.get("BPF Area Type", ""))
            if status_checkbox:
                status_checkbox.set(area_data.get("All New", False))
