import customtkinter as ctk

from interface.base_view import BaseView


class BuildingsView(BaseView):
    def __init__(self, window):
        super().__init__(window)
        self.main_window = window

    def __repr__(self):
        return "BuildingsView"

    def open_view(self):
        self.toggle_active_button("Buildings")
        self.grid_propagate(False)
        self.main_window.show_baseline_proposed_toggle(False)
