import unittest
from unittest.mock import patch, MagicMock
import pandas as pd
from parser import Parser


class TestParser(unittest.TestCase):

    @patch('os.walk')
    @patch('pandas.read_csv')
    def test_parse_data_no_merging_basic(self, mock_read_csv, mock_os_walk):
        # Symulujemy strukturę katalogów i plików
        mock_os_walk.return_value = [
            ('/base/2020', ['subdir'], ['0-Power Board_file1.csv']),
            ('/base/2020/subdir', [], ['0-Power Board_file2.csv']),
            ('/base/2021', [], ['1-BCDR0_file3.csv'])
        ]

        # Dane z pliku CSV, symulacja
        df_mock = pd.DataFrame({
            "'Date (YYYY-MM-DD HH:MM:SS)": ["2020-01-01 00:00:00", "2020-01-01 01:00:00"],
            "'Date Millisecond Offset": [0, 500],
            "'Date (J2000 mseconds)": [1000, 2000],
            "'S-Band Tx Voltage(V)": [3.3, 3.4]
        })

        # Każde wywołanie read_csv zwróci df_mock
        mock_read_csv.return_value = df_mock

        parser = Parser(
            base_folder='/base',
            additional_columns=["'S-Band Tx Voltage(V)"],
            start_year=None,
            end_year=None
        )

        # Parsujemy dla "0-Power Board"
        result_df = parser.parse_data_no_merging(file_pattern="0-Power Board")

        # Sprawdźmy, czy dane zostały scalone (z dwóch plików matching pattern)
        # Oczekujemy 4 wiersze (2 z file1, 2 z file2), file3 nie pasuje do wzorca
        self.assertEqual(len(result_df), 4)
        self.assertIn("'S-Band Tx Voltage(V)", result_df.columns)

        # Sprawdzamy sortowanie - dane powinny być posortowane wg "'Date (J2000 mseconds)"
        j2000_values = result_df["'Date (J2000 mseconds)"].values
        self.assertTrue(all(j2000_values[i] <= j2000_values[i + 1] for i in range(len(j2000_values) - 1)))

    @patch('os.walk')
    @patch('pandas.read_csv')
    def test_parse_data_with_year_filter(self, mock_read_csv, mock_os_walk):
        # Symulujemy foldery z rokiem w nazwie
        mock_os_walk.return_value = [
            ('/base/2019', [], ['0-Power Board_old.csv']),
            ('/base/2020', [], ['0-Power Board_data.csv']),
            ('/base/2021', [], ['0-Power Board_new.csv'])
        ]

        df_mock = pd.DataFrame({
            "'Date (YYYY-MM-DD HH:MM:SS)": ["2020-06-01 12:00:00"],
            "'Date Millisecond Offset": [100],
            "'Date (J2000 mseconds)": [3000],
            "'S-Band Tx Voltage(V)": [3.7]
        })
        mock_read_csv.return_value = df_mock

        parser = Parser(
            base_folder='/base',
            additional_columns=["'S-Band Tx Voltage(V)"],
            start_year=2020,
            end_year=2020
        )
        result_df = parser.parse_data_no_merging(file_pattern="0-Power Board")

        # Powinien parsować tylko folder 2020
        self.assertEqual(len(result_df), 1)
        self.assertEqual(result_df["'S-Band Tx Voltage(V)"].iloc[0], 3.7)

    @patch('os.walk')
    @patch('pandas.read_csv')
    def test_parse_data_missing_columns(self, mock_read_csv, mock_os_walk):
        # Jeśli plik nie posiada wszystkich wymaganych kolumn, powinien zostać pominięty
        mock_os_walk.return_value = [
            ('/base/2020', [], ['0-Power Board_incomplete.csv', '0-Power Board_complete.csv'])
        ]

        # Pierwszy df niekompletny - brak "'S-Band Tx Voltage(V)"
        df_incomplete = pd.DataFrame({
            "'Date (YYYY-MM-DD HH:MM:SS)": ["2020-01-01 00:00:00"],
            "'Date Millisecond Offset": [0],
            "'Date (J2000 mseconds)": [1000],
        })

        # Drugi df kompletny
        df_complete = pd.DataFrame({
            "'Date (YYYY-MM-DD HH:MM:SS)": ["2020-01-01 01:00:00"],
            "'Date Millisecond Offset": [500],
            "'Date (J2000 mseconds)": [2000],
            "'S-Band Tx Voltage(V)": [3.3]
        })

        # Pierwsze wywołanie read_csv -> df_incomplete, drugie -> df_complete
        mock_read_csv.side_effect = [df_incomplete, df_complete]

        parser = Parser(
            base_folder='/base',
            additional_columns=["'S-Band Tx Voltage(V)"]
        )
        result_df = parser.parse_data_no_merging(file_pattern="0-Power Board")

        # Powinien znaleźć dane tylko z drugiego pliku
        self.assertEqual(len(result_df), 1)
        self.assertIn("'S-Band Tx Voltage(V)", result_df.columns)


if __name__ == '__main__':
    unittest.main()
