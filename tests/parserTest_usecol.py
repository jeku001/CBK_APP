from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import os
import time
import pandas as pd

class Parser:
    def __init__(self, base_folder, additional_columns=None, start_year=None, end_year=None, workers=1):
        self.base_folder = base_folder
        self.additional_columns = additional_columns if additional_columns else []
        self.start_year = start_year
        self.end_year = end_year
        self.workers = workers
        self.start_time = -1
        self.end_time = -1

    @staticmethod
    def parse_single_file(file_path, required_columns):
        try:
            # Use usecols to load only necessary columns
            df = pd.read_csv(file_path, encoding="iso-8859-1", usecols=required_columns)
            selected_data = df.sort_values(by=["'Date (J2000 mseconds)"], ascending=True)
            return selected_data
        except Exception as e:
            print(f"Error processing file {file_path}: {e}")
            return pd.DataFrame(columns=required_columns)

    def parse_data_no_merging(self, file_pattern="0-Power Board", progress_callback=None):
        self.start_time = time.time()  # start time of the entire process
        required_columns = [
            "'Date (YYYY-MM-DD HH:MM:SS)",
            "'Date Millisecond Offset",
            "'Date (J2000 mseconds)"
        ] + self.additional_columns

        if self.start_year is not None:
            self.start_year = int(self.start_year)
        if self.end_year is not None:
            self.end_year = int(self.end_year)

        scan_start_time = time.time()

        files_to_process = []
        for root, dirs, files in os.walk(self.base_folder):
            folder_name = os.path.basename(root)
            if len(folder_name) >= 4 and folder_name[:4].isdigit():
                folder_year = int(folder_name[:4])
                if (self.start_year and folder_year < self.start_year) or (
                        self.end_year and folder_year > self.end_year):
                    dirs[:] = []
                    continue

            for file in files:
                if file_pattern in file and file.endswith(".csv"):
                    file_path = os.path.join(root, file)
                    files_to_process.append(file_path)

        scan_end_time = time.time()
        scan_duration = scan_end_time - scan_start_time
        print(f"File scanning completed in {scan_duration:.2f} seconds")
        print(f"Found {len(files_to_process)} files to process.")
        data_list = []
        total_files = len(files_to_process)

        # Use ThreadPoolExecutor or ProcessPoolExecutor based on file count and whether multiprocessing is enabled
        if self.workers > 1:
            executor_class = ThreadPoolExecutor if total_files < 500 else ProcessPoolExecutor
            print(f"Using {executor_class.__name__} with {self.workers} parallel tasks.")

            with executor_class(max_workers=self.workers) as executor:
                results = executor.map(self.parse_single_file, files_to_process, [required_columns] * total_files)
                for res_df in results:
                    if not res_df.empty:
                        data_list.append(res_df)

        else:
            print("Using single-threaded parsing...")
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
        total_duration = self.end_time - self.start_time
        print(f"Processing completed in {total_duration:.2f} seconds (including file scanning).")

        return long_df

if __name__ == "__main__":
    parser = Parser("G:\\CBK_windows_test_package",
        ["'Wheel Sum Current(mA)"],
        start_year=None,
        end_year=None,
        workers=8)
    for i in range(20):
        parsed_data = parser.parse_data_no_merging()
        print(f"{i}")
