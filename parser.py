import os
import time
import pandas as pd
from concurrent.futures import ProcessPoolExecutor

class Parser:
    def __init__(self, base_folder, additional_columns=None, start_year=None, end_year=None, workers=1):
        self.base_folder = base_folder
        self.additional_columns = additional_columns if additional_columns else []
        self.start_year = start_year
        self.end_year = end_year
        self.workers = workers

    def parse_single_file(self, file_path, required_columns):
        try:
            df = pd.read_csv(file_path, encoding="iso-8859-1")
            if not all(col in df.columns for col in required_columns):
                return pd.DataFrame(columns=required_columns)
            selected_data = df[required_columns]
            data_sorted = selected_data.sort_values(by=["'Date (J2000 mseconds)"], ascending=True)
            return data_sorted
        except Exception as e:
            print(f"Error processing file {file_path}: {e}")
            return pd.DataFrame(columns=required_columns)

    def parse_data_no_merging(self, file_pattern="0-Power Board"):
        self.start_time = time.time()  # start time
        required_columns = [
            "'Date (YYYY-MM-DD HH:MM:SS)",
            "'Date Millisecond Offset",
            "'Date (J2000 mseconds)"
        ] + self.additional_columns

        if self.start_year is not None:
            self.start_year = int(self.start_year)
        if self.end_year is not None:
            self.end_year = int(self.end_year)

        files_to_process = []
        for root, dirs, files in os.walk(self.base_folder):
            folder_name = os.path.basename(root)
            if len(folder_name) >= 4 and folder_name[:4].isdigit():
                folder_year = int(folder_name[:4])
                if (self.start_year and folder_year < self.start_year) or (self.end_year and folder_year > self.end_year):
                    dirs[:] = []
                    continue

            for file in files:
                if file_pattern in file and file.endswith(".csv"):
                    file_path = os.path.join(root, file)
                    files_to_process.append(file_path)

        data_list = []
        if self.workers > 1:
            with ProcessPoolExecutor(max_workers=self.workers) as executor:
                results = executor.map(self.parse_single_file, files_to_process, [required_columns]*len(files_to_process))
                for res_df in results:
                    if not res_df.empty:
                        data_list.append(res_df)
        else:
            for fpath in files_to_process:
                res_df = self.parse_single_file(fpath, required_columns)
                if not res_df.empty:
                    data_list.append(res_df)

        if data_list:
            long_df = pd.concat(data_list, ignore_index=True)
        else:
            long_df = pd.DataFrame(columns=required_columns)

        long_df = long_df.sort_values(by=["'Date (J2000 mseconds)"], ascending=True)
        if "'Date (YYYY-MM-DD HH:MM:SS)" in long_df.columns:
            long_df["'Date (YYYY-MM-DD HH:MM:SS)"] = pd.to_datetime(long_df["'Date (YYYY-MM-DD HH:MM:SS)"])

        self.end_time = time.time()
        print(f"Processing completed in {self.end_time - self.start_time:.2f} seconds")
        return long_df
