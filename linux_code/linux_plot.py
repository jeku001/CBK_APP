import matplotlib.pyplot as plt


class Plots:
    def __init__(self):
        pass

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
                    plt.plot(x, y, label=column)
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
