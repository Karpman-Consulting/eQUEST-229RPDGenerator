import customtkinter as ctk

from interface.base_view import BaseView


class MiscellaneousView(BaseView):
    button_name = "Misc."
    icon = "misc.png"

    def __init__(self, window):
        super().__init__(window)
        self.main_window = window

    def __repr__(self):
        return "MiscellaneousView"

    def open_view(self):
        self.toggle_active_button("Misc.")
        self.grid_propagate(False)
