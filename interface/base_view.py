import customtkinter as ctk

from interface.constants import *


class BaseView(ctk.CTkFrame):
    def __init__(self, window):
        super().__init__(window)
        self.window = window
        self.app_data = self.window.main_app.data
        self.configure(height=600)

    def toggle_active_button(self, active_button_name):
        for name, button in self.window.navbar_buttons.items():
            if name == active_button_name:
                self.window.navbar_buttons[name].configure(
                    fg_color=ACTIVE_VIEW_BUTTON_COLOR,
                    hover_color=ACTIVE_VIEW_BUTTON_COLOR,
                    text_color=WHITE,
                    font=NAV_FONT,
                )
            else:
                self.window.navbar_buttons[name].configure(
                    fg_color=VIEW_BUTTON_COLOR,
                    hover_color=VIEW_BUTTON_HOVER_COLOR,
                    text_color=WHITE,
                    font=NAV_FONT,
                )

    def update_warnings_errors(self):
        if len(self.app_data.warnings) > 0:
            self.window.warnings_button.configure(
                text=f"Warnings ({len(self.app_data.warnings)})",
                font=NAV_FONT,
                state=NORMAL,
                fg_color=ORANGE,
            )
        else:
            self.window.warnings_button.configure(
                text=f"Warnings",
                font=NAV_FONT,
                state=DISABLED,
                fg_color=GRAY,
            )
        if len(self.app_data.errors) > 0:
            self.window.errors_button.configure(
                text=f"Errors ({len(self.app_data.errors)})",
                font=NAV_FONT,
                state=NORMAL,
                fg_color=RED,
            )
        else:
            self.window.errors_button.configure(
                text=f"Errors",
                font=NAV_FONT,
                state=DISABLED,
                fg_color=GRAY,
            )
