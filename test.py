import customtkinter as ctk


class AdvancedPlotsWindow(ctk.CTkToplevel):
    def __init__(self, master, some_attr):
        super().__init__(master)
        self.master = master  # Przechowujemy referencję do głównego okna
        self.title("Advanced Plots")
        self.some_attr = some_attr

        # Etykieta wyświetlająca atrybut
        self.label = ctk.CTkLabel(self, text=f"Atrybut: {self.some_attr}")
        self.label.pack(padx=20, pady=20)

        # Przycisk odświeżania danych
        self.refresh_button = ctk.CTkButton(self, text="Refresh", command=self.refresh)
        self.refresh_button.pack(padx=20, pady=10)

    def refresh(self):
        # Aktualizujemy wartość atrybutu z głównego okna
        self.some_attr = self.master.some_attr_value
        self.label.configure(text=f"Atrybut: {self.some_attr}")


class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.geometry("600x400")
        self.right_frame = ctk.CTkFrame(self)
        self.right_frame.pack(padx=20, pady=20, fill="both", expand=True)

        # Przykładowy atrybut, który może ulec zmianie
        self.some_attr_value = "Początkowa wartość"

        self.open_advanced_plots_window_button = ctk.CTkButton(
            self.right_frame,
            text="Advanced Plots",
            command=self.open_advanced_plots_window,
            fg_color="#1ea70b"
        )
        self.open_advanced_plots_window_button.pack(pady=10)

    def open_advanced_plots_window(self):
        AdvancedPlotsWindow(master=self, some_attr=self.some_attr_value)


if __name__ == "__main__":
    app = App()
    app.mainloop()
