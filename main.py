import os
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.widgets import Cursor
from plot import Plots
from analysis import Analysis
from parser import Parser

if __name__ == "__main__":
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

    parser = Parser(base_folder, additional_columns, start_year, end_year)
    parsed_data = parser.parse_data_no_merging()

    output_file = os.path.join(os.getcwd(), "longDF.csv")
    parsed_data.to_csv(output_file, index=False)
    print(f"File saved to: {output_file}")




#spyder