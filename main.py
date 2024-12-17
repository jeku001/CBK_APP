import os
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.widgets import Cursor
from plot import Plots
from analysis import Analysis

if __name__ == "__main__":

    file_path = "longDF.csv"
    analyzer = Analysis()
    #analyzer.sort(file_path)
    df = pd.read_csv(file_path)
    df["'Date (YYYY-MM-DD HH:MM:SS)"] = pd.to_datetime(df["'Date (YYYY-MM-DD HH:MM:SS)"])

    analyzer.describe(file_path)
    analyzer.find_outliers_std(df,"'Sun Sensor Current(mA)", std_threshold = 20, remove=False, view=True, show_date=True)
    analyzer.find_outliers_roll_ZScore(df, "'Sun Sensor Current(mA)", window = 50, z_threshold=10, remove=False, view=True, show_date=True)

    plotter = Plots()
    plotter.plot(df)

#spyder