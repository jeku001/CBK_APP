import pandas as pd

data = pd.read_csv("additional_data/2010_2024_Sunspot_number_F10_daily.csv", header=None)
print(data.loc[1])