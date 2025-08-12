import tkinter as tk

from interface.install_config import InstallConfigWindow
from interface.project_config import ProjectConfigWindow
from interface.main_app_data import MainAppData

from rpd_generator.config import Config
from rpd_generator.utilities import validate_configuration


class MainApplication(tk.Tk):
    def __init__(self):
        super().__init__()
        self.data = MainAppData()

        self.install_config_window = None
        self.project_config_window = None

        # Placeholder so we can see main app window open for sanity check.
        # If it becomes visible we will at least know what it is.
        self.title("Main Application Window")
        self.main_app_window_label = tk.Label(
            self,
            text="\U0001f419 ...You shouldn't be seeing this... \U0001f419",
            font=("Segoe UI Emoji", 20),
        )
        self.main_app_window_label.pack(anchor="center", padx=10, pady=10)
        self.withdraw()

        # To avoid doing a lot of work in the __init__ method, call this to "start" the application
        self.start_application()

    def start_application(self):
        """
        Check for eQUEST installation. If not found, open installation config window. Otherwise, open CompParamWindow
        """
        validate_configuration.find_equest_installation()
        if Config.EQUEST_INSTALL_PATH:
            self.project_config_window = ProjectConfigWindow(self)
            self.project_config_window.protocol("WM_DELETE_WINDOW", self.quit)
        else:
            self.install_config_window = InstallConfigWindow(self)
            self.install_config_window.protocol("WM_DELETE_WINDOW", self.quit)

    def install_config_complete(self):
        """
        Called by InstallConfigWindow when the user has successfully configured the installation path. Closes
        the InstallConfigWindow and opens the ProjectConfigWindow
        """
        self.install_config_window.destroy()
        self.project_config_window = ProjectConfigWindow(self)
        self.project_config_window.protocol("WM_DELETE_WINDOW", self.quit)
