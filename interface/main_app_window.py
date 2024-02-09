import customtkinter as ctk
from tkinter import Menu
from interface.disclaimer_window import DisclaimerWindow
from interface.ctk_xyframe import CTkXYFrame
from PIL import Image
from interface.main_app_data import MainAppData


ctk.set_appearance_mode("Light")  # Modes: "System" (standard), "Dark", "Light"
ctk.set_default_color_theme(
    "dark-blue"
)  # Themes: "blue" (standard), "green", "dark-blue"


class MainApplicationWindow(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.app_data = MainAppData()

        self.title("eQUEST 229 RPD Generator")
        self.geometry(f"{1300}x{700}")
        self.minsize(1300, 350)

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
        help_menu.add_separator()
        help_menu.add_command(label="License", command="donothing")
        help_menu.add_command(label="Disclaimer", command=self.open_disclaimer)
        self.menubar.add_cascade(label="About", menu=help_menu)

        self.config(menu=self.menubar)

        self.bg_color = self.cget("fg_color")[0]

        # Define buttons bar - Always Active
        self.create_button_bar()

        # Initialize Widgets/Windows that will not always be active
        self.scrollable_frame = None
        self.license_window = None
        self.disclaimer_window = None
        self.continue_button = None

        # Initialize the configuration window to select and test the eQUEST installation path
        self.configuration_window()

        # Define scrollable frame
        # self.create_scrollable_frame()

    def create_button_bar(self):
        # Define button names
        button_names = [
            "Project Info",
            "Buildings",
            "Building Segments",
            "Spaces",
            "Surfaces",
            "Systems",
            "Ext. Lighting",
            "Misc.",
            "Results",
        ]

        # Define button icons
        icon_paths = [
            "menu.png",
            "buildings.png",
            "building_segments.png",
            "spaces.png",
            "surfaces.png",
            "systems.png",
            "ext_lighting.png",
            "misc.png",
            "results.png",
        ]

        for index, (name, icon_path) in enumerate(zip(button_names, icon_paths)):
            # Load and recolor the icon for the button
            icon = Image.open(f"interface/static/{icon_path}").convert("RGBA")

            r, g, b, alpha = icon.split()
            white_icon = Image.merge(
                "RGBA", (alpha, alpha, alpha, alpha)
            )  # Merge all channels into alpha to keep transparency
            icon_image = ctk.CTkImage(white_icon)

            # Create a frame for each button that will act as the border
            button_frame = ctk.CTkFrame(self, width=144, height=36, corner_radius=0)
            button_frame.grid(row=0, column=index, sticky="nsew")

            # Then create the button inside this frame with the icon
            button = ctk.CTkButton(
                button_frame,
                image=icon_image,
                text=name,
                width=140,
                height=30,
                corner_radius=0,
                state="disabled",
                compound="left",
            )
            button.place(relx=0.5, rely=0.5, anchor="center")

            # Keep a reference to the image to prevent garbage collection
            button.image = icon_image

    def clear_window(self):
        # Clear the window of all widgets after the first row which contains the button bar
        for widget in self.winfo_children():
            if int(widget.grid_info()["row"]) > 0:
                widget.grid_forget()

    def create_scrollable_frame(self):
        self.scrollable_frame = CTkXYFrame(self, width=1175, height=700)

        self.scrollable_frame.grid(row=1, column=0, columnspan=8, sticky="nsew")

    def open_disclaimer(self):
        if self.disclaimer_window is None or not self.disclaimer_window.winfo_exists():
            self.disclaimer_window = DisclaimerWindow(self)
            self.disclaimer_window.after(100, self.disclaimer_window.lift)
        else:
            self.disclaimer_window.focus()  # if window exists, focus it

    def configuration_window(self):
        directions_label = ctk.CTkLabel(
            self,
            text="Directions: ",
            anchor="e",
            justify="left",
            font=("Arial", 14, "bold"),
        )
        directions_label.grid(row=1, column=0, sticky="ew", padx=5, pady=20)
        instruction_text = (
            "Use the buttons below to select and validate the path to your eQUEST 3-65-7175 installation directory. \n"
            "The 'Auto' button will attempt to find the directory automatically. If manually browsing, you will select "
            "the folders that contain your eQUEST installation files and library data files. \n"
            "Click the 'Test' button to validate the eQUEST files required for this application. Upon a successful "
            "test, you will be able to continue to the next page."
        )
        directions = ctk.CTkLabel(
            self, text=instruction_text, anchor="w", justify="left"
        )
        directions.grid(row=1, column=1, columnspan=8, sticky="ew", padx=5, pady=20)

        # Create the labels for the path entry fields
        install_path_label = ctk.CTkLabel(
            self, text="Installation Path: ", anchor="e", justify="right", font=("Arial", 14, "bold")
        )
        install_path_label.grid(row=2, column=0, sticky="nsew", padx=5, pady=5)

        # Create the path entry field
        install_path_entry = ctk.CTkEntry(
            self, width=50, corner_radius=5, textvariable=self.app_data.installation_path
        )
        install_path_entry.grid(
            row=2, column=1, columnspan=7, sticky="ew", padx=5, pady=5
        )

        # Create the button to manually browse for the eQUEST installation
        install_browse_button = ctk.CTkButton(
            self, text="Browse", width=100, corner_radius=12
        )
        install_browse_button.grid(row=2, column=8, padx=5, pady=5)

        # Create the labels for the path entry fields
        userlib_path_label = ctk.CTkLabel(
            self, text="(Optional)      \nUser Library: ", anchor="e", justify="right", font=("Arial", 14, "bold")
        )
        userlib_path_label.grid(row=3, column=0, sticky="nsew", padx=5, pady=5)

        # Create the path entry field
        user_lib_path_entry = ctk.CTkEntry(
            self, width=50, corner_radius=5, textvariable=self.app_data.user_lib_path
        )
        user_lib_path_entry.grid(
            row=3, column=1, columnspan=7, sticky="ew", padx=5, pady=(20, 5)
        )

        # Create the button to manually browse for the eQUEST installation
        user_lib_browse_button = ctk.CTkButton(
            self, text="Browse", width=100, corner_radius=12
        )
        user_lib_browse_button.grid(row=3, column=8, padx=5, pady=(20, 5))

        # Create a frame to hold the file path Auto and Browse buttons
        path_button_frame = ctk.CTkFrame(self, fg_color=self.bg_color)
        path_button_frame.grid(
            row=4, column=1, columnspan=7, sticky="ew", padx=5, pady=5
        )
        path_button_frame.grid_columnconfigure((0, 1, 2), weight=1)

        # Create the button to run the automated attempt to find the eQUEST installation
        auto_button = ctk.CTkButton(
            path_button_frame,
            text="Auto",
            width=100,
            corner_radius=12,
            command=self.app_data.find_equest_installation,
        )
        auto_button.grid(row=0, column=1, padx=5, pady=5)

        # Create a frame to hold the Test button
        lower_button_frame = ctk.CTkFrame(self, fg_color=self.bg_color)
        lower_button_frame.grid(
            row=5, column=1, columnspan=7, sticky="ew", padx=5, pady=(20, 5)
        )
        lower_button_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)

        # Create the button to test the eQUEST installation files
        test_button = ctk.CTkButton(
            lower_button_frame,
            text="Test",
            width=100,
            corner_radius=12,
            command=self.verify_files
        )
        test_button.grid(row=0, column=1, padx=(350, 5), pady=5)

        # Create the button to continue to the Project Info page
        self.continue_button = ctk.CTkButton(
            lower_button_frame,
            text="Continue",
            width=100,
            corner_radius=12,
            state="disabled",
        )
        self.continue_button.grid(row=0, column=2, padx=(5, 350), pady=5)

    def verify_files(self):
        self.app_data.verify_equest_installation()
        self.toggle_continue_button()

    def toggle_continue_button(self):
        if self.app_data.files_verified:
            print(self.app_data.files_verified)
            self.continue_button.configure(state="normal")
        else:
            self.continue_button.configure(state="disabled")
