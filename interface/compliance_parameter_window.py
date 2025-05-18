import json
from pathlib import Path

import customtkinter as ctk
from PIL import Image
from tkinter import Menu
from functools import partial
from tkinter.filedialog import asksaveasfilename

from interface.CTkMessagebox import CTkMessagebox
from interface.rulesets import import_views, static_files_path
from interface.disclaimer_window import DisclaimerWindow
from interface.error_window import ErrorWindow

ctk.set_appearance_mode("Light")  # Modes: "System" (standard), "Dark", "Light"
ctk.set_default_color_theme(
    "dark-blue"
)  # Themes: "blue" (standard), "green", "dark-blue"
ICON_SIZE = (36, 36)


class ComplianceParameterWindow(ctk.CTkToplevel):
    def __init__(self, main_app):
        super().__init__()
        self.main_app = main_app

        self.title(
            f"eQUEST 229 RPD Generator - {self.main_app.data.project_name.get()}"
        )

        self.grid_propagate(False)
        self.bg_color = self.cget("fg_color")[0]

        # Expand subviews vertically to fill maximum window space, support for vertical window resizing
        self.grid_rowconfigure(1, weight=1)

        # Uncomment this if we want to be able to expand the window and have all the contents scale with the resize.
        # If so, we'll have to make some adjustments so the top button bar doesn't act weird.
        # for i in range(self.grid_size()[0]):
        #     self.grid_columnconfigure(i, weight=1)

        # Set the instance Views based on the selected ruleset
        self.views = {
            name: cls(self)
            for name, cls in import_views(
                self.main_app.data.selected_ruleset.get()
            ).items()
        }
        # Remove the SurfacesView if the selected ruleset is ASHRAE 90.1-2019 PRM and there are no doors in the baseline model
        if (
            self.main_app.data.selected_ruleset.get() == "ASHRAE 90.1-2019 PRM"
            and len(self.main_app.data.get_rmd("BASELINE_0").door_names) == 0
        ):
            self.views.pop("SurfacesView", None)
        self.static_filepath = static_files_path(
            self.main_app.data.selected_ruleset.get()
        )

        self.navbar_buttons = {}

        # Initialize attributes to hold references to Widgets & Windows
        self.current_view = None

        self.warnings_button = None
        self.errors_button = None
        self.back_button = None
        self.next_button = None
        self.generate_RPD_button = None
        self.baseline_label = None
        self.baseline_proposed_switch = None
        self.proposed_label = None

        self.license_window = None
        self.disclaimer_window = None
        self.error_window = None

        # Create main application widgets
        self.menubar = self.create_menu_bar()
        self.create_button_bar()
        self.create_nav_bar()

        # TODO - let ruleset specify landing page for compliance parameter window
        self.show_view("ProjectInfoView")

        self.geometry(f"{162*len(self.views)}x{750}")
        self.minsize((162 * len(self.views)), 350)

    def toggle_baseline_proposed(self):
        """When the selected ruleset is ASHRAE 90.1-2019 PRM, enable toggling between the Baseline and Proposed model data"""
        new_state = self.main_app.data.baseline_or_proposed.get()
        old_state = "Baseline" if new_state == "Proposed" else "Proposed"

        if old_state in self.current_view.current_subview_name:
            self.current_view.current_subview_name = (
                self.current_view.current_subview_name.replace(old_state, new_state)
            )
        self.current_view.show_subview(self.current_view.current_subview_name)

    def create_menu_bar(self):
        menubar = Menu(self)
        file_menu = Menu(menubar, tearoff=0)
        file_menu.add_command(label="New", command="donothing")
        file_menu.add_command(label="Open", command=self.load_project_data)
        file_menu.add_command(label="Save", command=self.save_project_data)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.quit)
        menubar.add_cascade(label="File", menu=file_menu)

        help_menu = Menu(menubar, tearoff=0)
        help_menu.add_command(label="Instructions", command="donothing")
        help_menu.add_command(label="Background", command="donothing")
        help_menu.add_separator()
        help_menu.add_command(label="License", command="donothing")
        help_menu.add_command(label="Disclaimer", command=self.open_disclaimer)
        menubar.add_cascade(label="About", menu=help_menu)

        self.config(menu=menubar)
        return menubar

    def create_button_bar(self):
        # Create a frame to hold the buttons
        button_bar = ctk.CTkFrame(self, width=162 * len(self.views), height=50)
        button_bar.grid(
            row=0, column=0, columnspan=max(8, len(self.views)), sticky="nsew"
        )

        # Define a custom order for views to appear
        custom_order = [
            "ProjectInfoView",
            "BuildingAreasView",
            "ZonesView",
            "SpacesView",
            "SurfacesView",
            "SystemsView",
            "ExteriorLightingView",
            "ServiceWaterHeatingView",
            "MiscellaneousView",
            "ResultsView",
        ]

        # Create a mapping from key to index
        order_dict = {name: index for index, name in enumerate(custom_order)}
        sorted_keys = sorted(
            self.views.keys(), key=lambda k: order_dict.get(k, float("inf"))
        )

        # Iterate through the ruleset's Views and create the associated buttons to access them
        view_names = [type(self.views[k]).__name__ for k in sorted_keys]
        button_names = [self.views[k].button_name for k in sorted_keys]
        icon_paths = [self.views[k].icon for k in sorted_keys]

        for index, (view_name, button_name, icon_path) in enumerate(
            zip(view_names, button_names, icon_paths)
        ):
            # Load and resize the icon
            icon = Image.open(f"{self.static_filepath}/{icon_path}").convert("RGBA")
            icon = icon.resize(ICON_SIZE, Image.LANCZOS)  # Resize icon

            r, g, b, alpha = icon.split()
            white_icon = Image.merge("RGBA", (alpha, alpha, alpha, alpha))

            # Create a CTkImage with the new size
            icon_image = ctk.CTkImage(light_image=white_icon, size=ICON_SIZE)

            # Create a frame for each button
            button_frame = ctk.CTkFrame(
                button_bar, width=162, height=50, corner_radius=0
            )
            button_frame.grid(row=0, column=index, sticky="nsew")

            # Create the button inside the frame
            button = ctk.CTkButton(
                button_frame,
                image=icon_image,
                text=button_name,
                font=("Arial", 12),
                width=158,
                height=46,
                corner_radius=0,
                compound="left",
                command=partial(
                    self.show_view, view_name
                ),  # Use partial to bind view_name
            )
            button.place(relx=0.5, rely=0.5, anchor="center")
            self.navbar_buttons[button_name] = button

            # Keep a reference to the image
            button.image = icon_image

    def create_nav_bar(self):
        # Create a frame to hold the buttons
        nav_bar = ctk.CTkFrame(self, width=162 * len(self.views), height=50)
        nav_bar.grid(row=2, column=0, columnspan=max(8, len(self.views)), sticky="nsew")

        # Create frame to hold baseline/proposed toggle
        baseline_proposed_frame = ctk.CTkFrame(
            nav_bar, height=50, fg_color="transparent"
        )
        baseline_proposed_frame.grid(
            row=0, column=5, columnspan=2, padx=10, sticky="ew"
        )

        # Configure the grid for uniform spacing
        for i in range(
            max(8, len(self.views))
        ):  # Adjust based on the number of columns used
            nav_bar.grid_columnconfigure(i, weight=1, uniform="nav")

        self.warnings_button = ctk.CTkButton(
            nav_bar,
            text="Warnings",
            width=90,
            fg_color="orange",
            hover_color="#FF8C00",
            command=lambda: self.raise_error_window(
                "\n".join(self.main_app.data.warnings)
            ),
        )
        self.warnings_button.grid(row=0, column=0, padx=10, pady=(5, 10), sticky="ew")

        self.errors_button = ctk.CTkButton(
            nav_bar,
            text="Errors",
            width=90,
            fg_color="red",
            hover_color="#E60000",
            command=lambda: self.raise_error_window(
                "\n".join(self.main_app.data.errors)
            ),
        )
        self.errors_button.grid(row=0, column=1, padx=10, pady=(5, 10), sticky="ew")

        self.back_button = ctk.CTkButton(
            nav_bar, text="Back", width=100, corner_radius=12
        )
        self.back_button.grid(row=0, column=3, padx=10, pady=(5, 10), sticky="ew")
        self.next_button = ctk.CTkButton(
            nav_bar, text="Next", width=100, corner_radius=12
        )
        self.next_button.grid(row=0, column=4, padx=10, pady=(5, 10), sticky="ew")

        self.generate_RPD_button = ctk.CTkButton(
            nav_bar,
            text="Generate RPD",
            width=100,
            fg_color="green",
            hover_color="#006400",
            command=self.main_app.data.call_write_rpd_json_from_rmds,
        )
        self.generate_RPD_button.grid(
            row=0,
            column=max(8, len(self.views)) - 1,
            padx=10,
            pady=(5, 10),
            sticky="ew",
        )

        if self.main_app.data.selected_ruleset.get() == "ASHRAE 90.1-2019 PRM":
            # Setup the baseline/proposed toggle
            self.baseline_label = ctk.CTkLabel(baseline_proposed_frame, text="Baseline")
            self.baseline_label.grid(row=0, column=0, padx=5, pady=(5, 10), sticky="e")

            self.baseline_proposed_switch = ctk.CTkSwitch(
                baseline_proposed_frame,
                variable=self.main_app.data.baseline_or_proposed,
                text="",
                height=20,
                width=50,
                switch_height=20,
                switch_width=50,
                command=self.toggle_baseline_proposed,
                onvalue="Proposed",
                offvalue="Baseline",
            )
            self.baseline_proposed_switch.deselect()
            self.baseline_proposed_switch.grid(row=0, column=1, padx=10)

            self.proposed_label = ctk.CTkLabel(baseline_proposed_frame, text="Proposed")
            self.proposed_label.grid(row=0, column=2, padx=5, sticky="w")

    def show_baseline_proposed_toggle(self, show_toggle):
        if show_toggle:
            self.baseline_label.grid()
            self.baseline_proposed_switch.grid()
            self.proposed_label.grid()
        else:
            self.baseline_label.grid_remove()
            self.baseline_proposed_switch.grid_remove()
            self.proposed_label.grid_remove()

    def show_back_next_buttons_toggle(
        self, show_back_button=True, show_next_button=True
    ):
        if show_back_button:
            self.back_button.configure(state="normal")
        else:
            self.back_button.configure(state="disabled")

        if show_next_button:
            self.next_button.configure(state="normal")
        else:
            self.next_button.configure(state="disabled")

    def show_view(self, view_name):
        # Clear previous view
        if self.current_view is not None:
            self.current_view.grid_forget()

        # Show new view
        view = self.views.get(view_name)
        if view:
            self.current_view = view
            self.current_view.grid(
                row=1, column=0, columnspan=max(8, len(self.views)), sticky="nsew"
            )
            self.current_view.open_view()

    def open_disclaimer(self):
        if self.disclaimer_window is None or not self.disclaimer_window.winfo_exists():
            self.disclaimer_window = DisclaimerWindow(self)
            self.disclaimer_window.after(100, self.disclaimer_window.lift, None)
        else:
            self.disclaimer_window.focus()  # if window exists, focus it

    def raise_error_window(self, error_text):
        if not error_text:
            return

        if self.error_window is None or not self.error_window.winfo_exists():
            self.error_window = ErrorWindow(self, error_text)
            self.error_window.after(100, self.error_window.lift)
        else:
            self.error_window.focus()  # if window exists, focus it

    def save_project_data(self):
        self.main_app.data.interface_data.clear()
        for view in self.views.values():
            # Skip incomplete views
            if not hasattr(view, "get_view_data"):
                continue
            self.main_app.data.interface_data.update(view.get_view_data())

        # Save the project data to a file
        # file_path = str(Path(self.main_app.data.output_directory.get()) / f"{self.main_app.data.project_name.get()}_data.json")
        file_path = asksaveasfilename(
            initialdir=str(Path(self.main_app.data.output_directory.get())),
            initialfile=f"{self.main_app.data.project_name.get()}_data",
            title="Save As",
            filetypes=[("JSON", "*.json")],
            defaultextension=".json",
        )
        with open(file_path, "w") as project_save_file:
            json.dump(self.main_app.data.interface_data, project_save_file, indent=4)

    def load_project_data(self):
        """Load a saved project data file. A saved data file will have already undergone
        basic validation. Not necessarily true if use has manually edited the file.
        Further validation will likely happen on RPD generation."""
        # Throw warning dialog with y/n for replacing existing data
        msg = CTkMessagebox(
            title="Warning",
            message="Loading a new project will overwrite/erase existing data. Would you like to continue?",
            icon="warning",
            option_1="No",
            option_2="Yes",
        )
        if msg.get() == "No":
            return
        self.main_app.data.populate_window_with_saved_project_data()
        self.main_app.refresh_compliance_parameter_window()
