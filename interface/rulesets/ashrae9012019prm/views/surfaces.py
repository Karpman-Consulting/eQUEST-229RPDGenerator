import customtkinter as ctk

from interface.ctk_xyframe import CTkXYFrame
from interface.base_view import BaseView
from interface.main_app_data import ASHRAE9012019ModelOptions
from interface.constants import *


class SurfacesView(BaseView):
    button_name = "Surfaces"
    icon = "surfaces.png"

    def __init__(self, window):
        super().__init__(window)
        self.main_window = window

        # All subviews will be placed inside this frame.
        # Single row/column allows formatting of subview to be handled by the subview itself
        self.subview_frame = ctk.CTkFrame(self)
        self.current_subview = None
        self.current_subview_name = None

        self.subviews = {
            "DoorSurfaceSubview": DoorSurfaceSubview(self.subview_frame),
        }
        self.subview_buttons = {}

        # Directions frame holds all directions info and will get 'gridded' within the surfaces view grid
        self.directions_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.directions_label = ctk.CTkLabel(
            self.directions_frame,
            text="Directions: ",
            font=LABEL_FONT,
        )
        self.directions_widget = ctk.CTkLabel(
            self.directions_frame,
            text=" Assign the various data parameters for each surface.",
            font=LABEL_FONT,
        )

        # Subview buttons
        self.border_line = ctk.CTkFrame(self, height=2, fg_color=BLACK)
        self.subview_button_frame = ctk.CTkFrame(
            self, corner_radius=0, fg_color="transparent"
        )
        self.create_subbutton_bar()

    def __repr__(self):
        return "SurfacesView"

    def open_view(self):
        self.toggle_active_button("Surfaces")
        self.grid_propagate(False)
        self.main_window.show_baseline_proposed_toggle(False)

        # 3 rows in the main surface view structure.
        # Subview frame (row 4, index 3) has a weight to make it fill up the empty space in the window
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

        self.current_subview_name = "DoorSurfaceSubview"
        self.show_subview("DoorSurfaceSubview")

    def create_subbutton_bar(self):
        callback_methods = {}
        if len(self.app_data.rmds[0].door_names) > 0:
            callback_methods["Doors"] = lambda: self.show_subview("DoorSurfaceSubview")

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

        subview = self.subviews.get(subview_name)
        if subview:
            self.current_subview_name = subview_name
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

    def get_view_data(self):
        view_data = {}
        for subview in self.subviews.values():
            view_data[subview.json_representation] = subview.get_subview_data()
        return view_data


class DoorSurfaceSubview(CTkXYFrame):
    json_representation = "doors"

    def __init__(self, subview_frame):
        super().__init__(subview_frame)
        self.surfaces_view = subview_frame.master
        self.app_data = self.surfaces_view.window.main_app.data
        self.is_subview_populated = False
        self.widget_rows = []

    def __repr__(self):
        return "DoorSurfaceSubview"

    def open_subview(self):
        self.surfaces_view.toggle_active_subbutton("Doors")
        self.populate_subview() if not self.is_subview_populated else None

    def populate_subview(self):
        self.add_column_headers()

        # Get doors from relevant rmd
        door_names = self.app_data.get_rmd(
            ASHRAE9012019ModelOptions.BASELINE_0
        ).door_names
        for i, door_name in enumerate(door_names):
            self.add_row(i, door_name)

        self.is_subview_populated = True

        # Populate with any loaded data if it exists
        self.set_subview_data()

    def add_column_headers(self):
        name_label = ctk.CTkLabel(self, text="Name", font=LABEL_FONT)
        name_label.grid(row=0, column=0, padx=PAD20END, pady=5)
        classification_label = ctk.CTkLabel(
            self, text="Classification", font=LABEL_FONT
        )
        classification_label.grid(row=0, column=2, padx=PAD20END, pady=5)

    def add_row(self, i, door_name):
        surface_label = ctk.CTkLabel(self, text=f"{door_name}")
        surface_label.grid(
            row=(i + 1), column=0, padx=PAD20END, pady=PAD20END, sticky=W
        )
        classification_combo = ctk.CTkComboBox(
            self,
            values=self.app_data.SubsurfaceSubclassificationDescriptions2019ASHRAE901,
            state=READONLY,
        )
        classification_combo.set("Swinging Door")
        classification_combo._entry.configure(justify=LEFT)
        classification_combo.grid(row=(i + 1), column=2, padx=PAD20END, pady=PAD20END)

        self.widget_rows.append(
            [
                surface_label,
                classification_combo,
            ]
        )

    def get_subview_data(self):
        subview_data = []
        for door_name, classification in self.widget_rows:
            subview_data.append(
                {
                    "Door Name": door_name.cget("text"),
                    "Classification": classification.get(),
                }
            )
        return subview_data

    def set_subview_data(self):
        """Set the subview data from a previously saved state."""
        for door_name, classification in self.widget_rows:
            door_classification = self.get_classification_from_door_name(
                door_name.cget("text")
            )
            if door_classification:
                # Set the classification from the saved data. Else keep as default
                classification.set(door_classification)

    def get_classification_from_door_name(self, door_name):
        door_data = self.app_data.all_project_data.get("doors", [])
        for door in door_data:
            if door.get("Door Name") == door_name:
                return door.get("Classification", "Swinging Door")
        return None
