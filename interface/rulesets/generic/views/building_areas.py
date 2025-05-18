import customtkinter as ctk
from PIL import Image

import interface.custom_widgets as cw
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

        self.init_subviews(
            {
                "Buildings": BuildingSubview,
                "Building Areas": BuildingAreasSubview,
            }
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
        directions = (
            "Create Buildings and Building Areas as needed to describe your project. "
            "A building area is a group of spaces that share a building area type. "
            "A Building Area may span more than one floor. There may be multiple Building Areas "
            "on a single floor. For best results, define buildings first."
        )
        self.open_view_with_subviews("Building Areas", directions_text=directions)

    def on_exit(self):
        if self.current_subview is self.subviews["Buildings"]:
            self.current_subview.save_buildings()

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
        # Add the first row with the default Building
        self.add_row(self.building_count + 1, is_first_row=True)
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

                # Remove building
                self.building_areas_view.remove_building(building_name_entry.get())

            self.building_areas_view.remove_widgets(row_widgets)
            if remove_button:
                remove_button.grid_remove()

        building_name_entry = ctk.CTkEntry(self)
        building_name_entry.grid(row=row, column=0, padx=PAD20END, pady=PAD20END)

        # Default set to "Building 1" here. We need to make a whole pass at setting defaults so this may change
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
        above_grade_spinbox = cw.IntSpinbox(self)
        above_grade_spinbox.grid(row=row, column=1, padx=PAD20END, pady=PAD20END)
        below_grade_spinbox = cw.IntSpinbox(self)
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

        # Update all existing building name combo boxes in BuildingAreasSubview
        current_buildings = list(self.app_data.buildings.keys())
        for combo in self.building_areas_view.building_combos:
            combo.configure(values=current_buildings)
            # Optional: reset selection if current value is now invalid
            if combo.get() not in current_buildings:
                combo.set(current_buildings[0] if current_buildings else "")

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
            building_data = {
                "Building Name": row[0].get(),
                "Floors Above Grade": row[1].get(),
                "Floors Below Grade": row[2].get(),
            }
            subview_data.append(building_data)
        return subview_data


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
        self.is_view_populated = True

    def add_column_headers(self):
        building_name_label = ctk.CTkLabel(self, text="Building Name", font=LABEL_FONT)
        building_name_label.grid(row=0, column=0, padx=PAD20END, pady=5)
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
            building_data = {
                "Building Name": row[0].get(),
                "Building Area Name": row[1].get(),
                "Fenestration Area Type": row[2].get(),
                "Lighting Area Type": row[3].get(),
                "HVAC Area Type": row[4].get(),
                "BPF Area Type": row[5].get(),
            }
            if not self.app_data.is_all_new_construction:
                building_data["All New"] = row[6].get()
            subview_data.append(building_data)
        return subview_data
