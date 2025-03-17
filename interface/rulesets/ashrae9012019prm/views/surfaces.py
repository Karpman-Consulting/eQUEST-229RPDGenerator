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
            "Baseline ExteriorSurfaceSubview": ExteriorSurfaceSubview(
                self.subview_frame
            ),
            "Proposed ExteriorSurfaceSubview": ExteriorSurfaceSubview(
                self.subview_frame
            ),
            "Baseline InteriorSurfaceSubview": InteriorSurfaceSubview(
                self.subview_frame
            ),
            "Proposed InteriorSurfaceSubview": InteriorSurfaceSubview(
                self.subview_frame
            ),
            "Baseline UndergroundSurfaceSubview": UndergroundSurfaceSubview(
                self.subview_frame
            ),
            "Proposed UndergroundSurfaceSubview": UndergroundSurfaceSubview(
                self.subview_frame
            ),
            "Baseline WindowSurfaceSubview": WindowSurfaceSubview(self.subview_frame),
            "Proposed WindowSurfaceSubview": WindowSurfaceSubview(self.subview_frame),
            "Baseline SkylightSurfaceSubview": SkylightSurfaceSubview(
                self.subview_frame
            ),
            "Proposed SkylightSurfaceSubview": SkylightSurfaceSubview(
                self.subview_frame
            ),
            "Baseline DoorSurfaceSubview": DoorSurfaceSubview(self.subview_frame),
            "Proposed DoorSurfaceSubview": DoorSurfaceSubview(self.subview_frame),
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
        self.main_window.show_baseline_proposed_toggle(True)

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

        self.current_subview_name = (
            f"{self.app_data.baseline_or_proposed.get()} ExteriorSurfaceSubview"
        )
        self.show_subview(
            f"{self.app_data.baseline_or_proposed.get()} ExteriorSurfaceSubview"
        )

    def create_subbutton_bar(self):
        callback_methods = {}
        current_state = self.app_data.baseline_or_proposed.get()
        if not self.app_data.is_all_new_construction.get():
            if len(self.app_data.rmds[0].ext_wall_names) > 0:
                callback_methods["Exterior"] = lambda: self.show_subview(
                    f"{current_state} ExteriorSurfaceSubview"
                )
            if len(self.app_data.rmds[0].int_wall_names) > 0:
                callback_methods["Interior"] = lambda: self.show_subview(
                    f"{current_state} InteriorSurfaceSubview"
                )
            if len(self.app_data.rmds[0].undg_wall_names) > 0:
                callback_methods["Underground"] = lambda: self.show_subview(
                    f"{current_state} UndergroundSurfaceSubview"
                )
        if len(self.app_data.rmds[0].door_names) > 0:
            callback_methods["Doors"] = lambda: self.show_subview(
                f"{current_state} DoorSurfaceSubview"
            )
        if len(self.app_data.rmds[0].window_names) > 0:
            callback_methods["Windows"] = lambda: self.show_subview(
                f"{current_state} WindowSurfaceSubview"
            )
        if len(self.app_data.rmds[0].skylight_names) > 0:
            callback_methods["Skylights"] = lambda: self.show_subview(
                f"{current_state} SkylightSurfaceSubview"
            )

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


class ExteriorSurfaceSubview(CTkXYFrame):
    def __init__(self, subview_frame):
        super().__init__(subview_frame)
        self.surfaces_view = subview_frame.master
        self.app_data = self.surfaces_view.window.main_app.data
        self.is_subview_populated = False

    def __repr__(self):
        return "ExteriorSurfaceSubview"

    def open_subview(self):
        self.surfaces_view.toggle_active_subbutton("Exterior")
        self.populate_subview() if not self.is_subview_populated else None

    def populate_subview(self):
        self.add_column_headers()

        #  Get exterior walls from relevant rmd. Throw error if none found
        ext_wall_names = []
        if self.app_data.baseline_or_proposed.get() == "Proposed":
            ext_wall_names = self.app_data.get_rmd(
                ASHRAE9012019ModelOptions.PROPOSED
            ).ext_wall_names
        elif self.app_data.baseline_or_proposed.get() == "Baseline":
            ext_wall_names = self.app_data.get_rmd(
                ASHRAE9012019ModelOptions.BASELINE_0
            ).ext_wall_names

        for i, ext_wall_name in enumerate(ext_wall_names):
            self.add_row(i, ext_wall_name)

        self.is_subview_populated = True

    def add_column_headers(self):
        name_label = ctk.CTkLabel(self, text="Name", font=LABEL_FONT)
        name_label.grid(row=0, column=0, padx=PAD20END, pady=5)
        status_label = ctk.CTkLabel(self, text="Status", font=LABEL_FONT)
        status_label.grid(row=0, column=1, padx=PAD20END, pady=5)

    def add_row(self, i, ext_wall_name):
        surface_label = ctk.CTkLabel(self, text=f"{ext_wall_name}")
        surface_label.grid(
            row=(i + 1), column=0, padx=PAD20END, pady=PAD20END, sticky=W
        )
        status_combo = ctk.CTkComboBox(
            self,
            values=self.app_data.StatusDescriptions,
            state=READONLY,
        )
        status_combo._entry.configure(justify=LEFT)
        status_combo.grid(row=(i + 1), column=1, padx=PAD20END, pady=PAD20END)


class InteriorSurfaceSubview(CTkXYFrame):
    def __init__(self, subview_frame):
        super().__init__(subview_frame)
        self.surfaces_view = subview_frame.master
        self.app_data = self.surfaces_view.window.main_app.data
        self.is_subview_populated = False

    def __repr__(self):
        return "InteriorSurfaceSubview"

    def open_subview(self):
        self.surfaces_view.toggle_active_subbutton("Interior")
        self.populate_subview() if not self.is_subview_populated else None

    def populate_subview(self):
        self.add_column_headers()

        #  Get interior walls from relevant rmd. Throw error if none found
        int_wall_names = []
        if self.app_data.baseline_or_proposed.get() == "Proposed":
            int_wall_names = self.app_data.get_rmd(
                ASHRAE9012019ModelOptions.PROPOSED
            ).int_wall_names
        elif self.app_data.baseline_or_proposed.get() == "Baseline":
            int_wall_names = self.app_data.get_rmd(
                ASHRAE9012019ModelOptions.BASELINE_0
            ).int_wall_names

        for i, int_wall_name in enumerate(int_wall_names):
            self.add_row(i, int_wall_name)

        self.is_subview_populated = True

    def add_column_headers(self):
        name_label = ctk.CTkLabel(self, text="Name", font=LABEL_FONT)
        name_label.grid(row=0, column=0, padx=PAD20END, pady=5)
        status_label = ctk.CTkLabel(self, text="Status", font=LABEL_FONT)
        status_label.grid(row=0, column=1, padx=PAD20END, pady=5)

    def add_row(self, i, int_wall_name):
        surface_label = ctk.CTkLabel(self, text=f"{int_wall_name}")
        surface_label.grid(
            row=(i + 1), column=0, padx=PAD20END, pady=PAD20END, sticky=W
        )
        status_combo = ctk.CTkComboBox(
            self,
            values=self.app_data.StatusDescriptions,
            state=READONLY,
        )
        status_combo._entry.configure(justify=LEFT)
        status_combo.grid(row=(i + 1), column=1, padx=PAD20END, pady=PAD20END)


class UndergroundSurfaceSubview(CTkXYFrame):
    def __init__(self, subview_frame):
        super().__init__(subview_frame)
        self.surfaces_view = subview_frame.master
        self.app_data = self.surfaces_view.window.main_app.data
        self.is_subview_populated = False

    def __repr__(self):
        return "UndergroundSurfaceSubview"

    def open_subview(self):
        self.surfaces_view.toggle_active_subbutton("Underground")
        self.populate_subview() if not self.is_subview_populated else None

    def populate_subview(self):
        self.add_column_headers()

        #  Get underground walls from relevant rmd. Throw error if none found
        undg_wall_names = []
        if self.app_data.baseline_or_proposed.get() == "Proposed":
            undg_wall_names = self.app_data.get_rmd(
                ASHRAE9012019ModelOptions.PROPOSED
            ).undg_wall_names
        elif self.app_data.baseline_or_proposed.get() == "Baseline":
            undg_wall_names = self.app_data.get_rmd(
                ASHRAE9012019ModelOptions.BASELINE_0
            ).undg_wall_names

        for i, undg_wall_name in enumerate(undg_wall_names):
            self.add_row(i, undg_wall_name)

        self.is_subview_populated = True

    def add_column_headers(self):
        name_label = ctk.CTkLabel(self, text="Name", font=LABEL_FONT)
        name_label.grid(row=0, column=0, padx=PAD20END, pady=5)
        status_label = ctk.CTkLabel(self, text="Status", font=LABEL_FONT)
        status_label.grid(row=0, column=1, padx=PAD20END, pady=5)

    def add_row(self, i, undg_wall_name):
        surface_label = ctk.CTkLabel(self, text=f"{undg_wall_name}")
        surface_label.grid(
            row=(i + 1), column=0, padx=PAD20END, pady=PAD20END, sticky=W
        )
        status_combo = ctk.CTkComboBox(
            self,
            values=self.app_data.StatusDescriptions,
            state=READONLY,
        )
        status_combo._entry.configure(justify=LEFT)
        status_combo.grid(row=(i + 1), column=1, padx=PAD20END, pady=PAD20END)


class WindowSurfaceSubview(CTkXYFrame):
    def __init__(self, subview_frame):
        super().__init__(subview_frame)
        self.surfaces_view = subview_frame.master
        self.app_data = self.surfaces_view.window.main_app.data
        self.is_subview_populated = False

    def __repr__(self):
        return "WindowSurfaceSubview"

    def open_subview(self):
        self.surfaces_view.toggle_active_subbutton("Windows")
        self.populate_subview() if not self.is_subview_populated else None

    def populate_subview(self):
        self.add_column_headers()

        #  Get windows from relevant rmd. Throw error if none found
        window_names = []
        if self.app_data.baseline_or_proposed.get() == "Proposed":
            window_names = self.app_data.get_rmd(
                ASHRAE9012019ModelOptions.PROPOSED
            ).window_names
        elif self.app_data.baseline_or_proposed.get() == "Baseline":
            window_names = self.app_data.get_rmd(
                ASHRAE9012019ModelOptions.BASELINE_0
            ).window_names

        for i, window_name in enumerate(window_names):
            self.add_row(i, window_name)

        self.is_subview_populated = True

    def add_column_headers(self):
        name_label = ctk.CTkLabel(self, text="Name", font=LABEL_FONT)
        name_label.grid(row=0, column=0, padx=PAD20END, pady=5)
        if not self.app_data.is_all_new_construction.get():
            status_label = ctk.CTkLabel(self, text="Status", font=LABEL_FONT)
            status_label.grid(row=0, column=1, padx=PAD20END, pady=5)
        classification_label = ctk.CTkLabel(
            self, text="Classification", font=LABEL_FONT
        )
        classification_label.grid(row=0, column=2, padx=PAD20END, pady=5)
        framing_type_label = ctk.CTkLabel(self, text="Framing Type", font=LABEL_FONT)
        framing_type_label.grid(row=0, column=3, padx=PAD20END, pady=5)
        operable_label = ctk.CTkLabel(self, text="Operable?", font=LABEL_FONT)
        operable_label.grid(row=0, column=4, padx=PAD20END, pady=5)
        open_sensor_label = ctk.CTkLabel(self, text="Open Sensor?", font=LABEL_FONT)
        open_sensor_label.grid(row=0, column=5, padx=PAD20END, pady=5)

    def add_row(self, i, window_name):
        surface_label = ctk.CTkLabel(self, text=f"{window_name}")
        surface_label.grid(
            row=(i + 1), column=0, padx=PAD20END, pady=PAD20END, sticky=W
        )
        if not self.app_data.is_all_new_construction.get():
            status_combo = ctk.CTkComboBox(
                self,
                values=self.app_data.StatusDescriptions,
                state=READONLY,
            )
            status_combo._entry.configure(justify=LEFT)
            status_combo.grid(row=(i + 1), column=1, padx=PAD20END, pady=PAD20END)
        classification_combo = ctk.CTkComboBox(
            self,
            values=self.app_data.SubsurfaceSubclassificationDescriptions2019ASHRAE901,
            state=READONLY,
        )
        classification_combo._entry.configure(justify=LEFT)
        classification_combo.grid(row=(i + 1), column=2, padx=PAD20END, pady=PAD20END)
        framing_type_combo = ctk.CTkComboBox(
            self,
            values=self.app_data.SubsurfaceSubclassificationDescriptions2019ASHRAE901,
            state=READONLY,
        )
        framing_type_combo._entry.configure(justify=LEFT)
        framing_type_combo.grid(row=(i + 1), column=3, padx=PAD20END, pady=PAD20END)
        operable_checkbox = ctk.CTkCheckBox(self, text="", width=30)
        operable_checkbox.grid(row=(i + 1), column=4, padx=PAD20END, pady=PAD20END)
        open_sensor_checkbox = ctk.CTkCheckBox(self, text="", width=30)
        open_sensor_checkbox.grid(row=(i + 1), column=5, padx=PAD20END, pady=PAD20END)


class SkylightSurfaceSubview(CTkXYFrame):
    def __init__(self, subview_frame):
        super().__init__(subview_frame)
        self.surfaces_view = subview_frame.master
        self.app_data = self.surfaces_view.window.main_app.data
        self.is_subview_populated = False

    def __repr__(self):
        return "SkylightSurfaceSubview"

    def open_subview(self):
        self.surfaces_view.toggle_active_subbutton("Skylights")
        self.populate_subview() if not self.is_subview_populated else None

    def populate_subview(self):
        self.add_column_headers()

        #  Get skylights from relevant rmd. Throw error if none found
        skylight_names = []
        if self.app_data.baseline_or_proposed.get() == "Proposed":
            skylight_names = self.app_data.get_rmd(
                ASHRAE9012019ModelOptions.PROPOSED
            ).skylight_names
        elif self.app_data.baseline_or_proposed.get() == "Baseline":
            skylight_names = self.app_data.get_rmd(
                ASHRAE9012019ModelOptions.BASELINE_0
            ).skylight_names

        for i, skylight_name in enumerate(skylight_names):
            self.add_row(i, skylight_name)

        self.is_subview_populated = True

    def add_column_headers(self):
        name_label = ctk.CTkLabel(self, text="Name", font=LABEL_FONT)
        name_label.grid(row=0, column=0, padx=PAD20END, pady=5)
        if not self.app_data.is_all_new_construction.get():
            status_label = ctk.CTkLabel(self, text="Status", font=LABEL_FONT)
            status_label.grid(row=0, column=1, padx=PAD20END, pady=5)
        classification_label = ctk.CTkLabel(
            self, text="Classification", font=LABEL_FONT
        )
        classification_label.grid(row=0, column=2, padx=PAD20END, pady=5)
        framing_type_label = ctk.CTkLabel(self, text="Framing Type", font=LABEL_FONT)
        framing_type_label.grid(row=0, column=3, padx=PAD20END, pady=5)
        operable_label = ctk.CTkLabel(self, text="Operable?", font=LABEL_FONT)
        operable_label.grid(row=0, column=4, padx=PAD20END, pady=5)
        open_sensor_label = ctk.CTkLabel(self, text="Open Sensor?", font=LABEL_FONT)
        open_sensor_label.grid(row=0, column=5, padx=PAD20END, pady=5)

    def add_row(self, i, skylight_name):
        surface_label = ctk.CTkLabel(self, text=f"{skylight_name}")
        surface_label.grid(
            row=(i + 1), column=0, padx=PAD20END, pady=PAD20END, sticky=W
        )
        if not self.app_data.is_all_new_construction.get():
            status_combo = ctk.CTkComboBox(
                self,
                values=self.app_data.StatusDescriptions,
                state=READONLY,
            )
            status_combo._entry.configure(justify=LEFT)
            status_combo.grid(row=(i + 1), column=1, padx=PAD20END, pady=PAD20END)
        classification_combo = ctk.CTkComboBox(
            self,
            values=self.app_data.SubsurfaceSubclassificationDescriptions2019ASHRAE901,
            state=READONLY,
        )
        classification_combo._entry.configure(justify=LEFT)
        classification_combo.grid(row=(i + 1), column=2, padx=PAD20END, pady=PAD20END)
        framing_type_combo = ctk.CTkComboBox(
            self,
            values=self.app_data.SubsurfaceFrameDescriptions2019ASHRAE901,
            state=READONLY,
        )
        framing_type_combo._entry.configure(justify=LEFT)
        framing_type_combo.grid(row=(i + 1), column=3, padx=PAD20END, pady=PAD20END)
        operable_checkbox = ctk.CTkCheckBox(self, text="", width=30)
        operable_checkbox.grid(row=(i + 1), column=4, padx=PAD20END, pady=PAD20END)
        open_sensor_checkbox = ctk.CTkCheckBox(self, text="", width=30)
        open_sensor_checkbox.grid(row=(i + 1), column=5, padx=PAD20END, pady=PAD20END)


class DoorSurfaceSubview(CTkXYFrame):
    def __init__(self, subview_frame):
        super().__init__(subview_frame)
        self.surfaces_view = subview_frame.master
        self.app_data = self.surfaces_view.window.main_app.data
        self.is_subview_populated = False

    def __repr__(self):
        return "DoorSurfaceSubview"

    def open_subview(self):
        self.surfaces_view.toggle_active_subbutton("Doors")
        self.populate_subview() if not self.is_subview_populated else None

    def populate_subview(self):
        self.add_column_headers()

        #  Get doors from relevant rmd. Throw error if none found
        door_names = []
        if self.app_data.baseline_or_proposed.get() == "Proposed":
            door_names = self.app_data.get_rmd(
                ASHRAE9012019ModelOptions.PROPOSED
            ).door_names
        elif self.app_data.baseline_or_proposed.get() == "Baseline":
            door_names = self.app_data.get_rmd(
                ASHRAE9012019ModelOptions.BASELINE_0
            ).door_names

        for i, door_name in enumerate(door_names):
            self.add_row(i, door_name)

        self.is_subview_populated = True

    def add_column_headers(self):
        name_label = ctk.CTkLabel(self, text="Name", font=LABEL_FONT)
        name_label.grid(row=0, column=0, padx=PAD20END, pady=5)
        status_label = ctk.CTkLabel(self, text="Status", font=LABEL_FONT)
        status_label.grid(row=0, column=1, padx=PAD20END, pady=5)
        classification_label = ctk.CTkLabel(
            self, text="Classification", font=LABEL_FONT
        )
        classification_label.grid(row=0, column=2, padx=PAD20END, pady=5)

    def add_row(self, i, door_name):
        surface_label = ctk.CTkLabel(self, text=f"{door_name}")
        surface_label.grid(
            row=(i + 1), column=0, padx=PAD20END, pady=PAD20END, sticky=W
        )
        status_combo = ctk.CTkComboBox(
            self,
            values=self.app_data.StatusDescriptions,
            state=READONLY,
        )
        status_combo._entry.configure(justify=LEFT)
        status_combo.grid(row=(i + 1), column=1, padx=PAD20END, pady=PAD20END)
        classification_combo = ctk.CTkComboBox(
            self,
            values=self.app_data.SubsurfaceSubclassificationDescriptions2019ASHRAE901,
            state=READONLY,
        )
        classification_combo._entry.configure(justify=LEFT)
        classification_combo.grid(row=(i + 1), column=2, padx=PAD20END, pady=PAD20END)
