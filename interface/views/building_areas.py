import customtkinter as ctk
import interface.custom_widgets as cw
from PIL import Image

from interface.ctk_xyframe import CTkXYFrame
from interface.base_view import BaseView


LABEL_FONT = ("Arial", 14, "bold")
READONLY = "readonly"
LEFT = "left"
E = "e"
W = "w"
FILL = "nsew"
PAD20END = (0, 20)
BLACK = "black"
SUBVIEW_BUTTON_COLOR = "#FFD966"
ACTIVE_SUBVIEW_BUTTON_COLOR = "#FFED67"


# TODO: Don't allow last row removal for buildings or areas
# TODO: Save buildings on switching tabs
# TODO: Update combo values in building areas on adding/removing building
# TODO: Remove Buildings tab from main frame
class BuildingAreasView(BaseView):
    def __init__(self, window):
        super().__init__(window)

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


class BuildingSubview(CTkXYFrame):
    def __init__(self, view_frame):
        super().__init__(view_frame)
        self.building_areas_view = view_frame.master
        self.app_data = self.building_areas_view.app_data

        self.is_view_populated = False
        self.building_area_count = 0

        self.add_building_button = ctk.CTkButton(
            self,
            text="Add Building",
            width=200,
            corner_radius=10,
            command=lambda: self.add_row(self.building_area_count + 1),
        )

    def __repr__(self):
        return "BuildingAreasSubview"

    def open_subview(self):
        self.building_areas_view.toggle_active_subbutton("Buildings")
        self.populate_subview() if not self.is_view_populated else None

    def populate_subview(self):
        self.add_column_headers()
        self.add_row(self.building_area_count + 1)
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

    def add_row(self, row):
        def remove_row():
            self.app_data.remove_building(building_name_entry.get())
            building_name_entry.grid_remove()
            above_grade_spinbox.grid_remove()
            below_grade_spinbox.grid_remove()
            save_building_button.grid_remove()
            remove_button.grid_remove()

        def save_building():
            self.app_data.add_or_update_building(
                building_name_entry.get(),
                above_grade_spinbox.get(),
                below_grade_spinbox.get(),
            )
            save_building_button.grid_remove()

        def entry_updated(entry):
            if entry != "":
                save_building_button.grid()
            return True

        # Registration only required for validatecommand functions
        val = self.register(entry_updated)

        building_name_entry = ctk.CTkEntry(
            self,
            validate="key",
            validatecommand=(val, "%P"),
        )
        building_name_entry.grid(row=row, column=0, padx=PAD20END, pady=PAD20END)
        # TODO: Customize spinboxes to allow validation
        above_grade_spinbox = cw.IntSpinbox(self)
        above_grade_spinbox.grid(row=row, column=1, padx=PAD20END, pady=PAD20END)
        below_grade_spinbox = cw.IntSpinbox(self)
        below_grade_spinbox.grid(row=row, column=2, padx=PAD20END, pady=PAD20END)
        save_image = ctk.CTkImage(
            light_image=Image.open("interface/static/white_check.png"),
            dark_image=None,
            size=(10, 10),
        )
        save_building_button = ctk.CTkButton(
            self,
            text="",
            image=save_image,
            width=28,
            corner_radius=10,
            command=save_building,
        )
        save_building_button.grid(row=row, column=3, padx=PAD20END, pady=PAD20END)
        remove_image = ctk.CTkImage(
            light_image=Image.open("interface/static/white_x.png"),
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
        remove_button.grid(row=row, column=4, padx=PAD20END, pady=PAD20END)
        self.add_building_button.grid(
            row=(row + 1),
            column=0,
            columnspan=2,
            sticky=FILL,
            padx=PAD20END,
            pady=PAD20END,
        )
        self.building_area_count += 1


class BuildingAreasSubview(CTkXYFrame):
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
        self.add_row(self.building_area_count + 1)
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

    def add_row(self, row):
        def populate_area_name(value):
            area_name_entry.delete(0, "end")
            area_name_entry.insert(0, self.app_data.get_building_area_name(value))

        def remove_row():
            # Remove building area from app_data
            building_name = building_name_combo.get()
            area_name = area_name_entry.get().split(building_name + " ")[1]
            self.app_data.remove_building_area(building_name, area_name)
            building_name_combo.grid_remove()
            area_name_entry.grid_remove()
            status_checkbox.grid_remove()
            fenestration_type_combo.grid_remove()
            lighting_type_combo.grid_remove()
            hvac_area_combo.grid_remove()
            bpf_area_combo.grid_remove()
            remove_button.grid_remove()

        # TODO: Existing rows do not update with new building options right now. Fix.
        building_name_combo = ctk.CTkComboBox(
            self,
            values=list(self.app_data.areas_by_building.keys()),
            command=populate_area_name,
            state=READONLY,
        )
        building_name_combo._entry.configure(justify=LEFT)
        building_name_combo.grid(row=row, column=0, padx=PAD20END, pady=PAD20END)
        area_name_entry = ctk.CTkEntry(self)
        area_name_entry.grid(row=row, column=1, padx=PAD20END, pady=PAD20END)
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
            # TODO: Enumerator for this?
            values=["BPF Option 1"],
            state=READONLY,
        )
        bpf_area_combo._entry.configure(justify=LEFT)
        bpf_area_combo.grid(row=row, column=6, padx=PAD20END, pady=PAD20END)
        remove_image = ctk.CTkImage(
            light_image=Image.open("interface/static/white_x.png"),
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

        self.building_area_count += 1
