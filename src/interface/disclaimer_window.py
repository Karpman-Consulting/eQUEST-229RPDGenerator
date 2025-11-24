import customtkinter as ctk


class DisclaimerWindow(ctk.CTkToplevel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.title("DISCLAIMER")
        self.geometry("400x400")
        self.resizable(False, False)

        # Create a label for the "Disclaimer Notice" part
        disclaimer_label = ctk.CTkLabel(
            self, text="Disclaimer Notice", anchor="w", font=("Helvetica", 20, "bold")
        )
        disclaimer_label.pack(fill="x", padx=10, pady=(10, 0))

        # Disclaimer and acknowledgment text without "Disclaimer Notice\n\n"
        disclaimer_text = (
            "Acknowledgment: This material is based upon work supported by the U.S. Department of Energy’s Office of Energy Efficiency and Renewable Energy (EERE) under the Building Technologies Office - DE-FOA-0002813 - Bipartisan Infrastructure Law Resilient and Efficient Codes Implementation.\n\n"
            "Award Number: DE-EE0010949\n\n"
            "Abridged Disclaimer: The views expressed herein do not necessarily represent the view of the U.S. Department of Energy or the United States Government.\n"
        )

        text_area_frame = ctk.CTkFrame(self)
        text_area_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        text_area = ctk.CTkTextbox(text_area_frame, wrap="word")
        text_area.pack(side="left", fill="both", expand=True)

        text_area.insert("1.0", disclaimer_text)
        text_area.configure(state="disabled")  # Make text area read-only
