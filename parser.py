import os
import time
import pandas as pd
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

        # Zainicjalizowanie required_columns przed pętlą
        required_columns = ["'Date (YYYY-MM-DD HH:MM:SS)", "'Date Millisecond Offset",
                            "'Date (J2000 mseconds)"] + self.additional_columns

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
                if (self.start_year and folder_year < self.start_year) or (
                        self.end_year and folder_year > self.end_year):
                    dirs[:] = []  # Pomijamy podfoldery
                    continue

            # Przetwarzanie plików w bieżącym folderze
            for file in files:
                if file_pattern in file and file.endswith(".csv"):
                    file_path = os.path.join(root, file)
                    try:
                        df = pd.read_csv(file_path, encoding="iso-8859-1")

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
            long_df = pd.DataFrame(columns=required_columns)  # required_columns jest teraz zawsze zainicjalizowane


        end_time = time.time()
        print(f"Processing completed in {end_time - start_time:.2f} seconds")
        print(f"Total rows processed: {total_rows}")
        print(f"sorting data")
        long_df = long_df.sort_values(by=["'Date (J2000 mseconds)"], ascending=True)
        print(f"changing to datetime type")
        long_df["'Date (YYYY-MM-DD HH:MM:SS)"] = pd.to_datetime(long_df["'Date (YYYY-MM-DD HH:MM:SS)"])
        print(f"done")
        return long_df

