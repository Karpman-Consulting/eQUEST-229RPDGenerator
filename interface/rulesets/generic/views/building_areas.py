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

        # All subviews will be placed inside this frame.
        # Single row/column allows formatting of subview to be handled by the subview itself
        self.subview_frame = ctk.CTkFrame(self)
        self.current_subview = None

        self.subviews = {
            "Building Areas": BuildingAreasSubview(self.subview_frame),
            "Buildings": BuildingSubview(self.subview_frame),
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

        # TODO - Change as part of the save/load work
        #  Building data structures
        self.areas_by_building = {"Building 1": ["Building 1 Area 1"]}
        self.above_grade_floors_by_building = {"Building 1": 0}
        self.below_grade_floors_by_building = {"Building 1": 0}
        self.app_data.building_area_options = ["Building 1 Area 1"]

    def __repr__(self):
        return "BuildingAreasView"

    def open_view(self):
        self.toggle_active_button("Building Areas")
        self.grid_propagate(False)

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

    def create_subbutton_bar(self):
        callback_methods = {
            "Buildings": lambda: self.show_subview("Buildings"),
            "Building Areas": lambda: self.show_subview("Building Areas"),
        }
        for index, name in enumerate(callback_methods):
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
                command=callback_methods[name],
            )
            self.subview_buttons[name] = button

    def show_subview(self, subview_name):
        # Clear previous subview
        if self.current_subview is not None:
            self.current_subview.grid_forget()
            if self.current_subview is self.subviews["Buildings"]:
                self.current_subview.save_buildings()

        # Show new subview
        subview = self.subviews.get(subview_name)
        if subview:
            self.current_subview = subview
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
                )
            else:
                self.subview_buttons[name].configure(
                    fg_color=SUBVIEW_BUTTON_COLOR,
                    hover_color=SUBVIEW_BUTTON_COLOR,
                    text_color=BLACK,
                )

    def remove_widgets(self, widgets):
        for widget in widgets:
            widget.grid_remove()
        if widgets in self.building_widgets_by_row:
            self.building_widgets_by_row.remove(widgets)
        if widgets in self.building_area_widgets_by_row:
            self.building_area_widgets_by_row.remove(widgets)

    # TODO: Change to support adding and removing data from each view into the app's data structure.
    def get_building_area_name(self, building_name):
        building_areas = self.areas_by_building.get(building_name)
        default_num = len(building_areas) + 1
        area_name_default = f"{building_name} Area {str(default_num)}"
        while area_name_default in building_areas:
            default_num += 1
            area_name_default = f"{building_name} Area {str(default_num)}"
        return area_name_default

    # TODO: Change to support adding and removing data from each view into the app's data structure.
    def remove_building_area(self, building_name, area_name):
        if area_name in self.areas_by_building[building_name]:
            self.areas_by_building[building_name].remove(area_name)
        if area_name in self.app_data.building_area_options:
            self.app_data.building_area_options.remove(area_name)

    # TODO: Change to support adding and removing data from each view into the app's data structure.
    def add_building_area(self, building_name, area_name):
        self.areas_by_building[building_name].append(area_name)
        self.app_data.building_area_options.append(area_name)

    # TODO: Change to support adding and removing data from each view into the app's data structure.
    def add_or_update_building(
        self, building_name, above_grade_floors, below_grade_floors
    ):
        if building_name not in self.areas_by_building:
            self.areas_by_building[building_name] = []
        self.above_grade_floors_by_building[building_name] = above_grade_floors
        self.below_grade_floors_by_building[building_name] = below_grade_floors

    # TODO: Change to support adding and removing data from each view into the app's data structure.
    def remove_building(self, building_name):
        self.areas_by_building.pop(building_name, None)
        self.above_grade_floors_by_building.pop(building_name, None)
        self.below_grade_floors_by_building.pop(building_name, None)

        # Remove all building areas from the deleted building.
        rows_to_remove = []
        for i, building_area_row in enumerate(self.building_area_widgets_by_row):
            # Get the building name from the first widget in the row
            building_area_building_name = building_area_row[0].get()

            if building_area_building_name == building_name and i == 0:
                # TODO: Setup here will change a bit too with different data structures and defaults. Less hardcoded.
                building_area_row[0].set("")
                building_area_row[1].delete(0, "end")
                building_area_row[1].insert(0, "")

            elif building_area_building_name == building_name:
                rows_to_remove.append(building_area_row)

        for row_to_remove in rows_to_remove:
            self.remove_widgets(row_to_remove)

    # TODO: Change to support adding and removing data from each view into the app's data structure.
    def building_has_areas(self, building_name):
        return len(self.areas_by_building[building_name]) > 0

    def get_view_data(self):
        view_data = {}
        for subview in self.subviews.values():
            view_data[subview.json_representation] = subview.get_subview_data()
        return view_data


class BuildingSubview(CTkXYFrame):
    def __init__(self, view_frame):
        super().__init__(view_frame)
        self.building_areas_view = view_frame.master
        self.app_data = self.building_areas_view.app_data
        self.is_view_populated = False
        self.building_count = 0
        self.json_representation = "buildings"

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
            remove_button.grid_remove()

        building_name_entry = ctk.CTkEntry(self)
        building_name_entry.grid(row=row, column=0, padx=PAD20END, pady=PAD20END)

        # Default set to "Building 1" here. We need to make a whole pass at setting defaults so this may change
        if is_first_row:
            building_name_entry.insert(
                0, next(iter(self.building_areas_view.areas_by_building))
            )
        else:
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
        for building_name in list(self.building_areas_view.areas_by_building.keys()):
            if building_name not in available_buildings:
                self.building_areas_view.remove_building(building_name)
        # Update building combo options in the building areas subview
        for combo in self.building_areas_view.building_combos:
            combo.configure(
                values=list(self.building_areas_view.areas_by_building.keys())
            )
        if self.building_areas_view.building_combos:
            self.building_areas_view.building_combos[0].set(
                list(self.building_areas_view.areas_by_building.keys())[0]
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
            building_data = {
                "Building Name": row[0].get(),
                "Floors Above Grade": row[1].get(),
                "Floors Below Grade": row[2].get(),
            }
            subview_data.append(building_data)
        return subview_data


class BuildingAreasSubview(CTkXYFrame):
    def __init__(self, view_frame):
        super().__init__(view_frame)
        self.building_areas_view = view_frame.master
        self.app_data = self.building_areas_view.app_data
        self.is_view_populated = False
        self.json_representation = "building_areas"
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
            if (
                area_name_entry.get()
                not in self.building_areas_view.areas_by_building[
                    building_name_combo.get()
                ]
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
                and new_area_name
                not in self.building_areas_view.areas_by_building[building_name]
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
            values=list(self.building_areas_view.areas_by_building.keys()),
            command=populate_area_name,
            state=READONLY,
        )
        building_name_combo._entry.configure(justify=LEFT)
        building_name_combo.grid(row=row, column=0, padx=PAD20END, pady=PAD20END)
        area_name_entry = ctk.CTkEntry(
            self, validate="key", validatecommand=(vcmd, "%P")
        )
        area_name_entry.grid(row=row, column=1, padx=PAD20END, pady=PAD20END)
        status_checkbox = None
        if is_first_row:
            default_building = next(iter(self.building_areas_view.areas_by_building))
            building_name_combo.set(default_building)
            area_name_entry.insert(
                0, self.building_areas_view.areas_by_building[default_building][0]
            )

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
            remove_button.grid(row=row, column=7, padx=PAD20END, pady=PAD20END)

        self.add_area_button.grid(
            row=(row + 1),
            column=0,
            columnspan=2,
            sticky=FILL,
            padx=PAD20END,
            pady=PAD20END,
        )

        # Add widgets to the list for later access
        row_widgets = [
            building_name_combo,
            area_name_entry,
            fenestration_type_combo,
            lighting_type_combo,
            hvac_area_combo,
            bpf_area_combo,
        ]

        if not self.app_data.is_all_new_construction.get():
            row_widgets.append(status_checkbox)

        if not is_first_row:
            row_widgets.append(remove_button)

        self.building_areas_view.building_area_widgets_by_row.append(row_widgets)

        # TODO: This separate building combos list will go away when app data structure is folded in
        self.building_areas_view.building_combos.append(building_name_combo)
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
