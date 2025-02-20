import matplotlib.pyplot as plt
import os, sys
import pandas as pd


class Plots:
    def __init__(self):
        pass

    @staticmethod
    def load_sunspot_data(sunspot_path="2010_2024_Sunspot_number_F10_daily.csv"):
        """
        Ładuje dane o plamach słonecznych z pliku CSV.
        Uwzględnia środowisko PyInstaller, korzystając z sys._MEIPASS.
        Zwraca wczytaną ramkę danych (DataFrame).
        """
        try:
            base_path = sys._MEIPASS
        except Exception:
            base_path = os.path.abspath(os.path.join(".", "../additional_data"))
        full_path = os.path.join(base_path, sunspot_path)
        sunspot_df = pd.read_csv(full_path, delim_whitespace=True, header=None)
        sunspot_df["Datetime"] = Plots.combine_datetime(sunspot_df)
        return sunspot_df

    @staticmethod
    def combine_datetime(df):
        """
        Łączy trzy pierwsze kolumny ramki danych w jeden obiekt typu datetime.
        Zakłada, że:
          - kolumna 0: rok (Year)
          - kolumna 1: dzień roku (Day of Year)
          - kolumna 2: godzina (Hour)
        Zwraca Series z wartościami datetime.
        """
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
                      show=False, add_sunspot=False):
        plt.figure(figsize=(10, 6))
        if plot_type == "line":
            plt.plot(df1[df1.columns[0]], df1[column1],
                     label=f'{column1} (DF1)', color='blue', linewidth=0.5)
            plt.plot(df2[df2.columns[0]], df2[column2],
                     label=f'{column2} (DF2)', color='orange', linewidth=0.5)
        elif plot_type == "scatter":
            plt.scatter(df1[df1.columns[0]], df1[column1],
                        label=f'{column1} (DF1)', color='blue', s=1)
            plt.scatter(df2[df2.columns[0]], df2[column2],
                        label=f'{column2} (DF2)', color='orange', s=1)

        if add_sunspot:
            # Ładujemy dane o plamach słonecznych wraz z kolumną Datetime
            sunspot_df = Plots.load_sunspot_data()
            # Używamy kolumny "Datetime" jako osi X
            x_sun = sunspot_df["Datetime"]
            # Zakładamy, że liczba sunspotów jest w czwartej kolumnie (indeks 3)
            y_sun = sunspot_df.iloc[:, 3]
            if plot_type == "line":
                plt.plot(x_sun, y_sun, label="Sunspot", color="red", linewidth=0.5)
            elif plot_type == "scatter":
                plt.scatter(x_sun, y_sun, label="Sunspot", color="red", s=1)

        if log_scale:
            plt.yscale('log')
            plt.title(f'Logarithmic Scale Plot: {column1} & {column2}')
        else:
            plt.title(f'Plot: {column1} & {column2}')
        plt.xlabel("Time (Year)")
        plt.ylabel("Values")
        plt.legend(loc="upper right")
        plt.grid(True)
        if show:
            plt.show()
        return plt

