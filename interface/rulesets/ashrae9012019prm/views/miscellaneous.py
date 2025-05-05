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
        self.main_window.next_button.configure(command=self.view_next)
        self.main_window.back_button.configure(command=self.view_back)
        self.main_window.show_back_next_buttons_toggle()
        self.toggle_active_button("Misc.")
        self.grid_propagate(False)
        self.main_window.show_baseline_proposed_toggle(False)

    def view_next(self):
        self.main_window.show_view("ResultsView")

    def view_back(self):
        self.main_window.show_view("SystemsView")
