from datetime import datetime, timedelta
from parser.constants import COMMON_FILENAME, DEFAULT_FOLDER
from pathlib import Path

import pandas as pd


class Diagram:
    pd.set_option('display.width', 1500)
    pd.set_option('display.max_columns', None)
    pd.set_option('display.max_colwidth', None)
    pd.set_option('display.max_rows', 10)
    pd.set_option('display.float_format', lambda x: '%.4f' % x)

    def __init__(self, end_date='2025-10-20'):
        self.start_date = (datetime.strptime(end_date, '%Y-%m-%d').date() -
                           timedelta(days=7 * 4)).strftime('%Y-%m-%d')
        self.end_date = end_date
        self.fact = None

    def fact_file(self):
        """Получить отчёт common"""
        fact_file = Path(
            __file__).parent.parent / DEFAULT_FOLDER / f'{COMMON_FILENAME}.csv'
        df = pd.read_csv(fact_file, delimiter=';', decimal=',')
        # df['Date'] = df['Date'].apply(lambda x: self._date_format(x))
        df = df[(df['Date'] >= self.start_date) &
                (df['Date'] <= self.end_date)]
        df = df[[
            'Date',
            'Transactions',
            'Cost',
        ]]

        self.fact = df

    def group_by_week(self):

        def get_week_range(date_str):
            date = datetime.strptime(date_str, "%Y-%m-%d").date()
            day_of_week = date.weekday()
            start_of_week = date - timedelta(days=day_of_week)
            end_of_week = start_of_week + timedelta(days=6)

            return (f"{start_of_week.strftime('%d.%m')} - "
                    f"{end_of_week.strftime('%d.%m')}")

        self.fact['Week'] = (self.fact['Date']
                             .apply(lambda x: get_week_range(x)))
        self.fact = self.fact.drop(columns=['Date'])
        self.fact = self.fact.groupby(['Week'], sort=False).sum()

    def set_cpo(self):
        self.fact['CPO'] = self.fact['Cost'] / self.fact['Transactions']

    def fin_format(self):
        self.fact.index.name = None

        self.fact['Transactions'] = self.fact['Transactions'].apply(
            lambda x: f"{float(x):.0f}"
        )
        self.fact['Cost'] = self.fact['Cost'].apply(
            lambda x: f"{float(x):.2f}"
        )
        self.fact['CPO'] = self.fact['CPO'].apply(
            lambda x: f"{float(x):.2f}"
        )


def diagram_run():
    ex = Diagram()
    ex.fact_file()
    ex.group_by_week()
    ex.set_cpo()
    ex.fin_format()
    print(ex.fact)
    return ex.fact
