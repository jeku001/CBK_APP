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
                    plt.plot(x, y, label=column, linewidth=1.0)
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
    def plot_two_cols(df1, column1, df2, column2, plot_type="line", log_scale=False, show=False):
        plt.figure(figsize=(10, 6))
        if plot_type == "line":
            plt.plot(df1[df1.columns[0]], df1[column1], label=f'{column1} (DF1)', color='blue', linewidth=1.0)
            plt.plot(df2[df2.columns[0]], df2[column2], label=f'{column2} (DF2)', color='orange', linewidth=1.0)
        elif plot_type == "scatter":
            plt.scatter(df1[df1.columns[0]], df1[column1], label=f'{column1} (DF1)', color='blue', s=1)
            plt.scatter(df2[df2.columns[0]], df2[column2], label=f'{column2} (DF2)', color='orange', s=1)

        if log_scale:
            plt.yscale('log')
            plt.title(f'Logarithmic Scale Plot: {column1} & {column2}')
        else:
            plt.title(f'Plot: {column1} & {column2}')
        plt.xlabel('Time')
        plt.ylabel('Values')
        plt.legend(loc="upper right")
        plt.grid(True)
        if show:
            plt.show()
        return plt

