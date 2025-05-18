import customtkinter as ctk
from interface.constants import *


class BaseView(ctk.CTkFrame):
    def __init__(self, window):
        super().__init__(window)
        self.window = window
        self.app_data = self.window.main_app.data
        self.configure(height=600)

        self.subview_frame = ctk.CTkFrame(self)
        self.current_subview_name = None
        self.current_subview = None
        self.subviews = {}
        self.subview_buttons = {}

        self.border_line = ctk.CTkFrame(self, height=2, fg_color=BLACK)
        self.subview_button_frame = ctk.CTkFrame(
            self, corner_radius=0, fg_color="transparent"
        )

        self.directions_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.directions_label = ctk.CTkLabel(
            self.directions_frame,
            text="Directions:",
            anchor=E,
            justify=LEFT,
            font=LABEL_FONT,
        )
        self.directions_widget = None

    def toggle_active_button(self, active_button_name):
        for name, button in self.window.navbar_buttons.items():
            if name == active_button_name:
                button.configure(
                    fg_color=ACTIVE_VIEW_BUTTON_COLOR,
                    hover_color=ACTIVE_VIEW_BUTTON_COLOR,
                    text_color=WHITE,
                    font=NAV_FONT,
                )
            else:
                button.configure(
                    fg_color=VIEW_BUTTON_COLOR,
                    hover_color=VIEW_BUTTON_HOVER_COLOR,
                    text_color=WHITE,
                    font=NAV_FONT,
                )

    def toggle_active_subbutton(self, active_subbutton_name):
        for name, button in self.subview_buttons.items():
            if name == active_subbutton_name:
                button.configure(
                    fg_color=ACTIVE_SUBVIEW_BUTTON_COLOR,
                    hover_color=ACTIVE_SUBVIEW_BUTTON_COLOR,
                    text_color=BLACK,
                    font=("Arial", 12, "bold"),
                )
            else:
                button.configure(
                    fg_color=SUBVIEW_BUTTON_COLOR,
                    hover_color=SUBVIEW_BUTTON_COLOR,
                    text_color=BLACK,
                    font=("Arial", 12, "bold"),
                )

    def update_warnings_errors(self):
        self.window.warnings_button.configure(
            text=(
                f"Warnings ({len(self.app_data.warnings)})"
                if self.app_data.warnings
                else "Warnings"
            ),
            font=NAV_FONT,
            state=NORMAL if self.app_data.warnings else DISABLED,
            fg_color=ORANGE if self.app_data.warnings else GRAY,
        )
        self.window.errors_button.configure(
            text=(
                f"Errors ({len(self.app_data.errors)})"
                if self.app_data.errors
                else "Errors"
            ),
            font=NAV_FONT,
            state=NORMAL if self.app_data.errors else DISABLED,
            fg_color=RED if self.app_data.errors else GRAY,
        )

    def init_subviews(self, subviews_dict):
        self.subviews = {
            name: view_class(self.subview_frame)
            for name, view_class in subviews_dict.items()
        }

    def create_subbutton_bar(self):
        for name in self.subviews:
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
                command=lambda n=name: self.show_subview(n),
            )
            self.subview_buttons[name] = button

    def show_subview(self, name):
        if self.current_subview:
            if hasattr(self.current_subview, "on_exit"):
                self.current_subview.on_exit()
            self.current_subview.grid_forget()

        subview = self.subviews.get(name)
        if subview:
            self.current_subview = subview
        else:
            current_state = getattr(self.app_data, "baseline_or_proposed", None)
            if callable(current_state):
                current_state = current_state()
            elif hasattr(current_state, "get"):
                current_state = current_state.get()

            filtered_subviews = [
                value for key, value in self.subviews.items() if current_state in key
            ]
            if filtered_subviews:
                self.current_subview = filtered_subviews[0]
            else:
                return  # No valid subview found

        self.current_subview.grid(row=0, column=0, sticky="nsew")

        if hasattr(self.current_subview, "focus_set"):
            self.current_subview.focus_set()
        if hasattr(self.current_subview, "open_subview"):
            self.current_subview.open_subview()

    def open_view_with_subviews(self, view_name, directions_text=None):
        self.toggle_active_button(view_name)
        self.grid_propagate(False)

        self.grid_rowconfigure(3, weight=1)
        self.grid_columnconfigure(0, weight=1)

        if directions_text:
            self.directions_widget = ctk.CTkLabel(
                self.directions_frame,
                text=directions_text,
                font=LABEL_FONT,
                anchor=W,
                justify=LEFT,
            )
            self.directions_frame.grid(row=0, column=0, sticky="ew", padx=50, pady=20)
            self.directions_label.grid(row=0, column=0)
            self.directions_widget.grid(row=0, column=1)

        self.subview_button_frame.grid(row=1, column=0, sticky="w", padx=20)
        for index, (name, button) in enumerate(self.subview_buttons.items()):
            button.grid(row=0, column=index, padx=(0, 4))

        self.border_line.grid(row=2, column=0, columnspan=5, sticky="ew", padx=20)

        self.subview_frame.grid(row=3, column=0, sticky="nsew", padx=20, pady=PAD20END)
        self.subview_frame.grid_rowconfigure(0, weight=1)
        self.subview_frame.grid_columnconfigure(0, weight=1)

        if self.subview_buttons:
            self.show_subview(next(iter(self.subview_buttons)))

    def get_view_data(self):
        view_data = {}
        for subview in self.subviews.values():
            view_data[subview.json_representation] = subview.get_subview_data()
        return view_data
