import os
import numpy as np
import pandas as pd




class Analysis:
    def __init__(self):
        pass

    def sort(self, file_path):

        print(f"Sorting file: {file_path}...")
        data = pd.read_csv(file_path)
        data_sorted = data.sort_values(by=["'Date (J2000 mseconds)"], ascending=True)
        data_sorted.to_csv(file_path, index=False)
        print("File sorted and overwritten successfully.")

    def describe(self, file_path, decimal_places=2):

        print(f"Generating summary statistics for: {file_path}...")
        data = pd.read_csv(file_path)
        data_describe = data.iloc[:, 3:].describe().round(decimal_places)
        print(data_describe)
        return data_describe

    def find_outliers_std(self, df, column, std_threshold=3, remove=False, view=True, show_date=True):

        mean = df[column].mean()
        std = df[column].std()
        lower_bound = mean - std_threshold * std
        upper_bound = mean + std_threshold * std

        # Find outliers
        outliers = df[(df[column] < lower_bound) | (df[column] > upper_bound)]

        if view:
            print(f"Outliers in column '{column}':")
            for index, row in outliers.iterrows():
                value = row[column]
                deviations = abs(value - mean) / std
                date = row[df.columns[0]] if show_date else ""
                print(f"Date: {date}, Row: {index}, Value: {value}, Deviations: {deviations:.2f} std")

        if remove:
            df = df.drop(outliers.index)
            print(f"Outliers removed. New DataFrame shape: {df.shape}")
            return df

        return df

    def find_outliers_roll_ZScore(self, df, column, window=50, z_threshold=3, remove=False, view=True, show_date=True):

        rolling_mean = df[column].rolling(window=window, center=True).mean()
        rolling_std = df[column].rolling(window=window, center=True).std()

        z_scores = (df[column] - rolling_mean) / rolling_std
        outliers = df[z_scores.abs() > z_threshold]

        if view:
            print(f"Rolling Z-score outliers in column '{column}':")
            for index, row in outliers.iterrows():
                value = row[column]
                z_score = z_scores.loc[index]
                date = row[df.columns[0]] if show_date else ""
                print(f"Date: {date}, Row: {index}, Value: {value}, Z-score: {z_score:.2f}")

        if remove:
            df = df.drop(outliers.index)
            print(f"Outliers removed. New DataFrame shape: {df.shape}")
            return df

        return df











