import customtkinter as ctk


class ErrorWindow(ctk.CTkToplevel):
    def __init__(self, error_text, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.title("ERROR")
        self.geometry("400x400")
        self.resizable(False, False)

        self.error_message = error_text

        # Create a label for the error message
        error_label = ctk.CTkLabel(
            self, text="An Error Occurred:", anchor="w", font=("Helvetica", 20, "bold")
        )
        error_label.pack(fill="x", padx=10, pady=(10, 0))

        text_area_frame = ctk.CTkFrame(self)
        text_area_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        text_area = ctk.CTkTextbox(text_area_frame, wrap="word")
        text_area.pack(side="left", fill="both", expand=True)

        text_area.insert("1.0", error_text)
        text_area.configure(state="disabled")  # Make text area read-only
