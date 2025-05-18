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
        # Call base layout with no directions and no subviews
        self.open_view_with_subviews("Ext. Lighting")
