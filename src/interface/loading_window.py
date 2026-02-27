import customtkinter as ctk


class LoadingWindow(ctk.CTkToplevel):
    def __init__(self, parent, message="Working..."):
        super().__init__(parent)
        self.title("Please wait")
        self.resizable(False, False)
        self.transient(parent)
        self.update_idletasks()
        self.geometry(
            "760x220+%d+%d"
            % (
                parent.winfo_rootx() + (parent.winfo_width() // 2) - 380,
                parent.winfo_rooty() + (parent.winfo_height() // 2) - 110,
            )
        )

        self.message_box = ctk.CTkTextbox(
            self,
            height=130,
            font=("Consolas", 13),
            wrap="char",
        )
        self.message_box.pack(padx=16, pady=(16, 8), fill="both", expand=True)
        self._recent_lines = [message]
        self.message_box.insert("1.0", message)
        self.message_box.configure(state="disabled")

        self.progress = ctk.CTkProgressBar(self, mode="determinate")
        self.progress.pack(padx=16, pady=(0, 16), fill="x")
        self.progress.set(0)

    def set_message(self, text: str):
        self._recent_lines.append(text)
        self._recent_lines = self._recent_lines[-10:]
        self.message_box.configure(state="normal")
        self.message_box.delete("1.0", "end")
        self.message_box.insert("1.0", "\n".join(self._recent_lines))
        self.message_box.see("end")
        self.message_box.configure(state="disabled")

    def set_progress(self, value: float):
        """value: 0.0 → 1.0"""
        self.progress.set(value)

    def close(self):
        if self.winfo_exists():
            # hide immediately
            self.withdraw()
            # destroy safely shortly after (when idle)
            self.after(50, lambda: self.winfo_exists() and self.destroy())
