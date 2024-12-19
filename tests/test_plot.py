import unittest
from unittest.mock import patch
import pandas as pd
from linux_code.plot import Plots

class TestPlots(unittest.TestCase):

    @patch('matplotlib.pyplot.show')
    @patch('matplotlib.pyplot.savefig')
    @patch('matplotlib.pyplot.plot')
    @patch('matplotlib.pyplot.figure')
    @patch('matplotlib.pyplot.gca')
    def test_plot_linear(self, mock_gca, mock_figure, mock_plot, mock_savefig, mock_show):
        # Tworzymy przykładowe dane
        df = pd.DataFrame({
            "Time": [1, 2, 3],
            "'S-Band Tx Voltage(V)": [3.3, 3.4, 3.5],
            "'S-Band Tx Current(A)": [0.1, 0.11, 0.12]
        })

        # Mockowanie gca, bo Cursor wymaga dostępu do obecnych osi wykresu
        mock_axis = unittest.mock.MagicMock()
        mock_gca.return_value = mock_axis

        plots = Plots()
        plots.plot(df, selected_columns=["'S-Band Tx Voltage(V)"], plot_type="linear")

        # Sprawdźmy, czy plot została wywołana z poprawnymi danymi
        # Nie sprawdzamy wartości dokładnie, tylko czy wywołanie nastąpiło
        mock_plot.assert_called_with(df["Time"], df["'S-Band Tx Voltage(V)"], label="'S-Band Tx Voltage(V)")

        # Sprawdźmy czy zapis do pliku nastąpił
        mock_savefig.assert_called_once_with("wykres.pdf", format="pdf")

        # Sprawdźmy czy show został wywołany
        mock_show.assert_called_once()

    @patch('matplotlib.pyplot.show')
    @patch('matplotlib.pyplot.savefig')
    @patch('matplotlib.pyplot.plot')
    @patch('matplotlib.pyplot.figure')
    @patch('matplotlib.pyplot.gca')
    def test_plot_logarithmic(self, mock_gca, mock_figure, mock_plot, mock_savefig, mock_show):
        df = pd.DataFrame({
            "Time": [10, 20, 30],
            "'S-Band Tx Voltage(V)": [3.3, 3.4, 3.5]
        })

        mock_axis = unittest.mock.MagicMock()
        mock_gca.return_value = mock_axis

        plots = Plots()
        plots.plot(df, selected_columns=["'S-Band Tx Voltage(V)"], plot_type="log")

        # Sprawdzamy czy plot został wywołany
        mock_plot.assert_called_with(df["Time"], df["'S-Band Tx Voltage(V)"], label="'S-Band Tx Voltage(V)")
        mock_savefig.assert_called_once_with("wykres.pdf", format="pdf")
        mock_show.assert_called_once()

if __name__ == '__main__':
    unittest.main()
