import os
import pandas as pd
import time
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

class Parser:
    def __init__(self, base_folder, additional_columns=None, start_year=None, end_year=None):
        self.base_folder = base_folder
        self.additional_columns = additional_columns if additional_columns else []
        self.start_year = start_year
        self.end_year = end_year

    def parse_data_no_merging(self, file_pattern="0-Power Board"):
        start_time = time.time()
        data_list = []
        total_rows = 0

        # Konwersja lat na liczby (jeśli podane)
        if self.start_year is not None:
            self.start_year = int(self.start_year)
        if self.end_year is not None:
            self.end_year = int(self.end_year)

        # Przechodzimy przez strukturę folderów
        for root, dirs, files in os.walk(self.base_folder):
            folder_name = os.path.basename(root)

            # Filtrujemy foldery na podstawie roku
            if len(folder_name) >= 4 and folder_name[:4].isdigit():
                folder_year = int(folder_name[:4])
                if (self.start_year and folder_year < self.start_year) or (self.end_year and folder_year > self.end_year):
                    dirs[:] = []  # Pomijamy podfoldery
                    continue

            # Przetwarzanie plików w bieżącym folderze
            for file in files:
                if file_pattern in file and file.endswith(".csv"):
                    file_path = os.path.join(root, file)
                    try:
                        df = pd.read_csv(file_path, encoding="iso-8859-1")
                        required_columns = ["'Date (YYYY-MM-DD HH:MM:SS)", "'Date Millisecond Offset", "'Date (J2000 mseconds)"] + self.additional_columns

                        if not all(col in df.columns for col in required_columns):
                            continue

                        # Wybór wymaganych kolumn
                        selected_data = df[required_columns]

                        # Sortowanie danych po kolumnie 'Date (J2000 mseconds)'
                        data_sorted = selected_data.sort_values(by=["'Date (J2000 mseconds)"], ascending=True)

                        data_list.append(data_sorted)
                        total_rows += data_sorted.shape[0]
                    except Exception as e:
                        print(f"Error processing file {file_path}: {e}")

        # Połącz wszystkie dane
        if data_list:
            long_df = pd.concat(data_list, ignore_index=True)
        else:
            long_df = pd.DataFrame(columns=required_columns)

        end_time = time.time()
        print(f"Processing completed in {end_time - start_time:.2f} seconds")
        print(f"Total rows processed: {total_rows}")

        return long_df

# Tkinter Application
class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Data Parser Application")
        self.base_folder = ""

        self.additional_columns = []
        self.available_columns = [
            "'HKC Current(mA)",
            "'ADCC Current(mA)",
            "'Rate Sensor Current(mA)",
            "'Sun Sensor Current(mA)",
            "'Wheel Sum Current(mA)"
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

        tk.Label(root, text="Select Columns:").grid(row=3, column=0, padx=10, pady=5)
        self.column_vars = []
        for i, col in enumerate(self.available_columns):
            var = tk.BooleanVar()
            self.column_vars.append(var)
            tk.Checkbutton(root, text=col, variable=var).grid(row=4+i, column=1, sticky="w")

        tk.Button(root, text="Run Parser", command=self.run_parser).grid(row=10, column=1, padx=10, pady=20)

    def browse_folder(self):
        folder_selected = filedialog.askdirectory()
        self.folder_entry.delete(0, tk.END)
        self.folder_entry.insert(0, folder_selected)

    def run_parser(self):
        self.base_folder = self.folder_entry.get()
        start_year = self.start_year_entry.get()
        end_year = self.end_year_entry.get()

        if not self.base_folder:
            messagebox.showerror("Error", "Please select a base folder")
            return

        try:
            start_year = int(start_year) if start_year else None
            end_year = int(end_year) if end_year else None

            self.additional_columns = [col for col, var in zip(self.available_columns, self.column_vars) if var.get()]

            parser = Parser(self.base_folder, self.additional_columns, start_year, end_year)
            parsed_data = parser.parse_data_no_merging()

            output_file = os.path.join(self.base_folder, "longDF.csv")
            parsed_data.to_csv(output_file, index=False)
            messagebox.showinfo("Success", f"File saved to: {output_file}")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
