import os
import pandas as pd
import time

def parse_data_no_merging(base_folder, additional_columns=[], file_pattern="0-Power Board", start_year=None, end_year=None):
    start_time = time.time()
    data_list = []
    total_rows = 0

    # Konwersja lat na liczby (jeśli podane)
    if start_year is not None:
        start_year = int(start_year)
    if end_year is not None:
        end_year = int(end_year)

    # Przechodzimy przez strukturę folderów
    for root, dirs, files in os.walk(base_folder):
        # Pobieramy nazwę bieżącego folderu
        folder_name = os.path.basename(root)

        # Filtrujemy foldery na podstawie roku (format RRRR-MM)
        if len(folder_name) >= 4 and folder_name[:4].isdigit():
            folder_year = int(folder_name[:4])
            if (start_year and folder_year < start_year) or (end_year and folder_year > end_year):
                # Pomijamy foldery spoza zakresu
                dirs[:] = []  # Usuwamy podfoldery, aby os.walk ich nie przetwarzał
                continue

        # Przetwarzanie plików w bieżącym folderze
        for file in files:
            if file_pattern in file and file.endswith(".csv"): ##pomija csv_old
                file_path = os.path.join(root, file)
                try:
                    df = pd.read_csv(file_path, encoding="iso-8859-1")

                    # Sprawdź, czy wymagane kolumny istnieją
                    required_columns = ["'Date (YYYY-MM-DD HH:MM:SS)", "'Date Millisecond Offset", "'Date (J2000 mseconds)"] + additional_columns
                    if not all(col in df.columns for col in required_columns):
                        continue

                    selected_data = df[required_columns]

                    data_list.append(selected_data)
                    total_rows += selected_data.shape[0]

                except Exception as e:
                    print(f"Error processing file {file_path}: {e}")

    # Połącz wszystkie dane w jeden DataFrame
    if data_list:
        long_df = pd.concat(data_list, ignore_index=True)
    else:
        long_df = pd.DataFrame(columns=required_columns)

    end_time = time.time()
    elapsed_time = end_time - start_time

    print(f"Processing completed in {elapsed_time:.2f} seconds")
    print(f"Total rows processed: {total_rows}")

    return long_df

# Ustawienia
base_folder = "/home/jeku/Nextcloud/UAM_BRITE/Lem/WOD/Parsed"
additional_columns = [
    "'HKC Current(mA)",
    "'ADCC Current(mA)",
    "'Rate Sensor Current(mA)",
    "'Sun Sensor Current(mA)",
    "'Wheel Sum Current(mA)"
]

start_year = 2005
end_year = 2025

# Wywołanie funkcji
parsed_data = parse_data_no_merging(base_folder, additional_columns, start_year=start_year, end_year=end_year)

# Zapisz dane do pliku CSV
script_dir = os.path.dirname(os.path.abspath(__file__)) # zapisze plik w katalogu roboczym wywolania skryptu
output_file = os.path.join(script_dir, "longDF.csv")
parsed_data.to_csv(output_file, index=False)
print(f"File saved to: {output_file}")

