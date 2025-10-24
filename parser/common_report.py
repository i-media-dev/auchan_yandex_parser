from parser.constants import (COMMON_FILENAME, DEFAULT_COLUMNS_CAMPAIGN,
                              DEFAULT_FOLDER, DIRECT_FILENAME,
                              METRICA_FILENAME)
from pathlib import Path

import pandas as pd


class CommonReport:

    report_folder = Path(__file__).parent.parent / DEFAULT_FOLDER

    def __init__(self):
        self.df = None

    def _read_files(self, file):
        """Читает файлы отчётов разных сервисов, преобразует в DataFrame"""
        path = self.report_folder / f'{file}.csv'
        df = pd.read_csv(path, delimiter=';')

        if any(col in df.columns for col in DEFAULT_COLUMNS_CAMPAIGN):
            df = df.drop(columns=[col for col in DEFAULT_COLUMNS_CAMPAIGN if
                                  col in df.columns])

        return df

    def _concat_files(self):
        """Объединяет DF'ы в один отчёт"""
        reports_names_list = [
            DIRECT_FILENAME,
            METRICA_FILENAME,
            # APPMETRICA_FILENAME
        ]

        collection_of_dfs = [self._read_files(file) for file in
                             reports_names_list]
        concat = (
            pd.concat(
                objs=collection_of_dfs,
                ignore_index=True
            )
            .groupby(['Date', 'CampaignName', 'Device'], as_index=False)
            .sum()
        )

        return concat

    def save_common_report(self):

        self._concat_files().to_csv(
            self.report_folder / f'{COMMON_FILENAME}.csv',
            index=False,
            header=True,
            sep=';',
            encoding='cp1251',
            decimal=','
        )
