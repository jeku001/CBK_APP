import matplotlib.pyplot as plt


class Plots:
    def __init__(self):
        pass

    @staticmethod
    def plot(df, selected_columns=None, plot_type_var="linear"):
        all_columns = df.columns[3:]
        columns_to_plot = selected_columns if selected_columns else all_columns

        for column in columns_to_plot:
            if column in df.columns:
                plt.figure(figsize=(12, 6))

                if plot_type_var == "logarithmic":
                    plt.plot(df[df.columns[0]], df[column], label=column)
                    plt.yscale("log")
                    plt.title(f'Logarithmic scale: {column}')
                else:
                    plt.plot(df[df.columns[0]], df[column], label=column)
                    plt.title(f'Linear scale: {column}')

                plt.xlabel('Time')
                plt.ylabel('Values')
                plt.legend(loc="upper right")
                plt.grid(True)

                # cursor = Cursor(plt.gca(), useblit=True, color='red', linewidth=1)
                # plt.savefig("wykres.pdf", format="pdf")
                plt.show()
