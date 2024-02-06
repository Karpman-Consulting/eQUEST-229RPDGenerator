import customtkinter as ctk


ctk.set_appearance_mode("Dark")  # Modes: "System" (standard), "Dark", "Light"
ctk.set_default_color_theme("dark-blue")  # Themes: "blue" (standard), "green", "dark-blue"


class MainApplicationWindow(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("DOE2/eQUEST-Standard 229 RPD Generator")
        self.geometry(f"{1300}x{700}")