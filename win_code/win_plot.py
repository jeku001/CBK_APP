import matplotlib.pyplot as plt
import os, sys
import pandas as pd


class Plots:
    def __init__(self):
        pass

    @staticmethod
    def load_sunspot_data(sunspot_path="2010_2024_Sunspot_number_F10_daily.csv"):
        """ Wczytuje dane o plamach słonecznych, obsługując tryb PyInstaller """

        # Znalezienie poprawnej ścieżki pliku
        if getattr(sys, 'frozen', False):  # Sprawdza, czy program jest skompilowany przez PyInstaller
            base_path = sys._MEIPASS
        else:
            base_path = os.path.abspath(os.path.join(os.getcwd(), "../additional_data"))

        full_path = os.path.join(base_path, sunspot_path)

        # Sprawdzenie, czy plik istnieje
        if not os.path.isfile(full_path):
            raise FileNotFoundError(f"Error: File '{full_path}' not found.")

        try:
            # Wczytywanie pliku CSV
            sunspot_df = pd.read_csv(full_path, sep=r'\s+', engine='python', header=None,
                                     names=["Year", "Day_of_Year", "Hour", "Sunspot_Number", "F10.7_Index"])
            # Tworzenie kolumny z datą
            sunspot_df["Datetime"] = Plots.combine_datetime(sunspot_df)

        except Exception as e:
            raise RuntimeError(f"Error loading CSV file '{full_path}': {e}")

        return sunspot_df


    @staticmethod
    def combine_datetime(df):
        year = df.iloc[:, 0]
        day_of_year = df.iloc[:, 1]
        hour = df.iloc[:, 2]
        dt = pd.to_datetime(year.astype(str), format='%Y') + pd.to_timedelta(day_of_year - 1,
                                                                             unit='D') + pd.to_timedelta(hour, unit='h')
        print(dt)
        return dt

    @staticmethod
    def plot(df, selected_columns=None, plot_type_var="Line", plot_scale_var="linear"):
        x = df[df.columns[0]]
        all_columns = df.columns[3:]
        columns_to_plot = selected_columns if selected_columns else all_columns

        for column in columns_to_plot:
            if column in df.columns:
                plt.figure(figsize=(12, 6))

                y = df[column]

                if plot_type_var == "line":
                    plt.plot(x, y, label=column, linewidth=0.5)
                elif plot_type_var == "scatter":
                    plt.scatter(x, y, s=1, label=column)
                else:
                    print("debug: plot type not in (line, scatter")

                if plot_scale_var == "logarithmic":
                    plt.yscale("log")
                    plt.title(f'Logarithmic scale: {column}')
                else:
                    plt.title(f'Linear scale: {column}')

                plt.xlabel('Time')
                plt.ylabel('Values')
                plt.legend(loc="upper right")
                plt.grid(True)

                plt.show()

    @staticmethod
    def plot_two_cols(df1, column1, df2, column2,
                      plot_type="line", log_scale=False,
                      show=False, add_sunspot=None):
        fig, ax = plt.subplots(figsize=(10, 6))
        add_sunspot = add_sunspot.get()

        if plot_type == "line":
            ax.plot(df1[df1.columns[0]], df1[column1],
                    label=f'{column1} (DF1)', color='blue', linewidth=0.2)
            ax.plot(df2[df2.columns[0]], df2[column2],
                    label=f'{column2} (DF2)', color='orange', linewidth=0.2)
        elif plot_type == "scatter":
            ax.scatter(df1[df1.columns[0]], df1[column1],
                       label=f'{column1} (DF1)', color='blue', s=0.2)
            ax.scatter(df2[df2.columns[0]], df2[column2],
                       label=f'{column2} (DF2)', color='orange', s=0.2)

        if add_sunspot:
            print("wszedlem tu (Jest true)")
            print(f"type of var: {add_sunspot}")
            # print(f"type of var 'z get': {add_sunspot.get()}")
            sunspot_df = Plots.load_sunspot_data()
            x_sun = sunspot_df["Datetime"]
            y_sun = sunspot_df.iloc[:, 3]

            min_year_value = min(df1[df1.columns[0]].min().year, df2[df2.columns[0]].min().year)
            max_year_value = max(df1[df1.columns[0]].max().year, df2[df2.columns[0]].max().year) + 1
            min_year = pd.to_datetime(str(min_year_value), format='%Y')
            max_year = pd.to_datetime(str(max_year_value), format='%Y')
            mask = (sunspot_df["Datetime"] >= min_year) & (sunspot_df["Datetime"] <= max_year)
            filtered_sunspot_df = sunspot_df.loc[mask]
            x_sun = filtered_sunspot_df["Datetime"]
            y_sun = filtered_sunspot_df.iloc[:, 3]

            ax2 = ax.twinx()
            ax2.plot(x_sun, y_sun, label="Sunspot", color="red", linewidth=0.5)

            ax2.set_ylabel("Sunspot Values", color="red")
            ax2.tick_params(axis="y", labelcolor="red")

            lines, labels = ax.get_legend_handles_labels()
            lines2, labels2 = ax2.get_legend_handles_labels()
            ax.legend(lines + lines2, labels + labels2, loc="upper right")
        else:
            ax.legend(loc="upper right")

        if log_scale:
            ax.set_yscale('log')
            ax.set_title(f'Logarithmic Scale Plot: {column1} & {column2}')
        else:
            ax.set_title(f'Plot: {column1} & {column2}')
        ax.set_xlabel("Time (Year)")
        ax.set_ylabel("Values")
        ax.grid(True)
        if show:
            plt.show()
        return plt

