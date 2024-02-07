import customtkinter as ctk
from tkinter import Menu
from interface.license_window import LicenseWindow


ctk.set_appearance_mode("Dark")  # Modes: "System" (standard), "Dark", "Light"
ctk.set_default_color_theme("dark-blue")  # Themes: "blue" (standard), "green", "dark-blue"


class MainApplicationWindow(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("DOE2/eQUEST-Standard 229 RPD Generator")
        self.geometry(f"{1300}x{700}")

        self.menubar = Menu(self)
        file_menu = Menu(self.menubar, tearoff=0)
        file_menu.add_command(label="New", command="donothing")
        file_menu.add_command(label="Open", command="donothing")
        file_menu.add_command(label="Save", command="donothing")
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.quit)
        self.menubar.add_cascade(label="File", menu=file_menu)

        help_menu = Menu(self.menubar, tearoff=0)
        help_menu.add_command(label="Instructions", command="donothing")
        help_menu.add_command(label="Background", command="donothing")
        file_menu.add_separator()
        help_menu.add_command(label="Disclaimer", command=self.open_license)
        self.menubar.add_cascade(label="About", menu=help_menu)

        self.config(menu=self.menubar)

        self.license_window = None

    def open_license(self):
        if self.license_window is None or not self.license_window.winfo_exists():
            self.license_window = LicenseWindow(self)
            self.license_window.after(100, self.license_window.lift)
        else:
            self.license_window.focus()  # if window exists, focus it
