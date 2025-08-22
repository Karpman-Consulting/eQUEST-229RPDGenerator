import customtkinter as ctk


class LoadingWindow(ctk.CTkToplevel):
    def __init__(self, parent, message="Working..."):
        super().__init__(parent)
        self.title("Please wait")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()

        self.geometry(
            "350x100+%d+%d"
            % (
                parent.winfo_rootx() + (parent.winfo_width() // 2) - 175,
                parent.winfo_rooty() + (parent.winfo_height() // 2) - 50,
            )
        )

        self.label = ctk.CTkLabel(self, text=message, font=("Arial", 14))
        self.label.pack(padx=16, pady=(16, 8), fill="x")

        self.progress = ctk.CTkProgressBar(self, mode="determinate")
        self.progress.pack(padx=16, pady=(0, 16), fill="x")
        self.progress.set(0)

    def set_message(self, text: str):
        self.label.configure(text=text)

    def set_progress(self, value: float):
        """value: 0.0 → 1.0"""
        self.progress.set(value)

    def close(self):
        self.grab_release()
        self.destroy()
