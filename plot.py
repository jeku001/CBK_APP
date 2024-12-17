import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.widgets import Cursor

class Plots:
    def __init__(self):
        pass

    def plot(self, df, selected_columns=None):


        all_columns = df.columns[3:] # skip first 3 columns

        columns_to_plot = selected_columns if selected_columns else all_columns

        for column in columns_to_plot:
            if column in df.columns:
                plt.figure(figsize=(12, 6))
                plt.plot(df[df.columns[0]], df[column], label=column)
                plt.title(f'Plot: {column}')
                plt.xlabel('Time')
                plt.ylabel('Values')
                plt.legend()
                plt.grid(True)

                cursor = Cursor(plt.gca(), useblit=True, color='red', linewidth=1)
                plt.show()