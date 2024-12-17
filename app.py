import time
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from parser import Parser
import os

# Tkinter Application
class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Data Parser Application")
        self.base_folder = ""

        self.additional_columns = []
        self.file_pattern = "0-Power Board"  # Domyślny wzorzec
        self.available_columns = [
            "'HKC Current(mA)",
            "'ADCC Current(mA)",
            "'Rate Sensor Current(mA)",
            "'Sun Sensor Current(mA)",
            "'Wheel Sum Current(mA)"
        ]

        self.file_patterns = [
            "0-Power Board", "1-BCDR0", "3-S-Band", "4-HKC", "5-IOBC",
            "6-ACS", "7-ADCS", "8-ADC_SUB", "9-Header Board"
        ]

        # UI Elements
        tk.Label(root, text="Base Folder:").grid(row=0, column=0, padx=10, pady=5)
        self.folder_entry = tk.Entry(root, width=50)
        self.folder_entry.grid(row=0, column=1, padx=10, pady=5)
        tk.Button(root, text="Browse", command=self.browse_folder).grid(row=0, column=2, padx=10, pady=5)

        tk.Label(root, text="Start Year:").grid(row=1, column=0, padx=10, pady=5)
        self.start_year_entry = tk.Entry(root)
        self.start_year_entry.grid(row=1, column=1, padx=10, pady=5)

        tk.Label(root, text="End Year:").grid(row=2, column=0, padx=10, pady=5)
        self.end_year_entry = tk.Entry(root)
        self.end_year_entry.grid(row=2, column=1, padx=10, pady=5)

        tk.Label(root, text="File Pattern:").grid(row=3, column=0, padx=10, pady=5)
        self.pattern_combo = ttk.Combobox(root, values=self.file_patterns, state="readonly")
        self.pattern_combo.grid(row=3, column=1, padx=10, pady=5)
        self.pattern_combo.set(self.file_patterns[0])  # Ustaw domyślny wybór

        tk.Label(root, text="Select Columns:").grid(row=4, column=0, padx=10, pady=5)
        self.column_vars = []
        for i, col in enumerate(self.available_columns):
            var = tk.BooleanVar()
            self.column_vars.append(var)
            tk.Checkbutton(root, text=col, variable=var).grid(row=5+i, column=1, sticky="w")

        tk.Button(root, text="Run Parser", command=self.run_parser).grid(row=12, column=1, padx=10, pady=20)

    def browse_folder(self):
        folder_selected = filedialog.askdirectory()
        self.folder_entry.delete(0, tk.END)
        self.folder_entry.insert(0, folder_selected)

    def run_parser(self):
        self.base_folder = self.folder_entry.get()
        start_year = self.start_year_entry.get()
        end_year = self.end_year_entry.get()
        self.file_pattern = self.pattern_combo.get()

        if not self.base_folder:
            messagebox.showerror("Error", "Please select a base folder")
            return

        try:
            start_year = int(start_year) if start_year else None
            end_year = int(end_year) if end_year else None

            self.additional_columns = [col for col, var in zip(self.available_columns, self.column_vars) if var.get()]

            parser = Parser(self.base_folder, self.additional_columns, start_year, end_year)
            parsed_data = parser.parse_data_no_merging(file_pattern=self.file_pattern)

            # Zapisanie pliku w katalogu roboczym
            output_file = os.path.join(os.getcwd(), "longDF.csv")
            parsed_data.to_csv(output_file, index=False)
            messagebox.showinfo("Success", f"File saved to: {output_file}")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
