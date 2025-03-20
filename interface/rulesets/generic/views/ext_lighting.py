import customtkinter as ctk

from interface.base_view import BaseView


class ExteriorLightingView(BaseView):
    button_name = "Ext. Lighting"
    icon = "ext_lighting.png"

    def __init__(self, window):
        super().__init__(window)
        self.main_window = window

    def __repr__(self):
        return "ExteriorLightingView"

    def open_view(self):
        self.toggle_active_button("Ext. Lighting")
        self.grid_propagate(False)
