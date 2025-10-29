from datetime import datetime
from parser.constants import COMMON_FILENAME, DEFAULT_FOLDER
from pathlib import Path

import pandas as pd


class Table:
    pd.set_option('display.width', 1500)
    pd.set_option('display.max_columns', None)
    pd.set_option('display.max_colwidth', None)
    pd.set_option('display.max_rows', 10)
    pd.set_option('display.float_format', lambda x: '%.4f' % x)

    def __init__(self, start_date='2025-10-01', end_date='2025-10-20'):
        self.start_date = start_date
        self.end_date = end_date
        self.start_date_d = self._date_format(start_date)
        self.end_date_d = self._date_format(end_date)
        self.plan = None
        self.fact = None
        self.plan_on_date = None
        self.df = None

    @staticmethod
    def _date_format(date_as_text):
        """Формат даты в виде 01.10 из текста"""
        a = datetime.strptime(date_as_text, '%Y-%m-%d').date()
        return a.strftime('%d.%m')

    def fact_file(self):
        """Получить отчёт common"""
        fact_file = Path(
            __file__).parent.parent / DEFAULT_FOLDER / f'{COMMON_FILENAME}.csv'
        df = pd.read_csv(fact_file, delimiter=';', decimal=',')
        # df['Date'] = df['Date'].apply(lambda x: self._date_format(x))
        df = df[(df['Date'] >= self.start_date) &
                (df['Date'] <= self.end_date)]
        df = df[[
            'Clicks',
            'Transactions',
            'Revenue',
            'Cost',
        ]]
        df = df.sum().to_frame().T

        df['name'] = f'Факт с {self.start_date_d} по {self.end_date_d}'

        self.fact = df

    def plan_file(self):
        """Получить данные плана"""
        plan_file = Path(__file__).parent.parent / 'presentation' / 'plan.xlsx'
        df = pd.read_excel(plan_file)
        # df['Дата'] = df['Дата'].apply(lambda x: self._date_format(x))
        df = df[(df['Дата'] >= self.start_date) &
                (df['Дата'] <= self.end_date)]
        df = (df[[
            'Клики',
            'Заказы',
            'Доход',
            'Расход (до НДС и АК)',
        ]])
        df['name'] = 'ПЛАН'
        self.plan = df

    def plan_on_date_file(self):
        """План на дату"""
        df = self.plan
        df = df.drop('name', axis=1)
        df = df.apply(lambda x: x / 31 * int(self.end_date[-2:]))
        df['name'] = f'ПЛАН на {self.end_date_d}'

        self.plan_on_date = df

    def plan_done(self):
        """Выполнение плана"""
        self.df['% реализации ПЛАНА'] = (
            self.df[f'Факт с {self.start_date_d} по {self.end_date_d}'] /
            self.df['ПЛАН']
        )
        return self.df

    def plan_on_date_done(self):
        """Выполнение плана на дату"""
        self.df[f'% реализации ПЛАНА на {self.end_date_d}'] = (
            self.df[f'Факт с {self.start_date_d} по {self.end_date_d}'] /
            self.df[f'ПЛАН на {self.end_date_d}']
        )
        return self.df

    def add_counted_metrics(self):
        """Получить расчётные метрики"""
        df = self.df

        df['CvR %'] = df['Заказы'] / df['Клики']
        df['Средний чек'] = df['Доход'] / df['Заказы']
        df['CPO'] = df['Расход (до НДС и АК)'] / df['Заказы']
        df['ДРР %'] = df['Расход (до НДС и АК)'] / df['Доход']

        self.df = df

    def match(self):
        """Соединить «файлы»"""
        self.fact = self.fact.rename(
            columns=dict(
                zip(
                    self.fact.columns.tolist(),
                    self.plan.columns.tolist(),
                )
            )
        )

        self.df = pd.concat([
            self.plan,
            self.fact,
            self.plan_on_date
        ])

        self.df = self.df.set_index('name')
        self.df.index.name = None

    def fin_format(self):
        """Финальное форматирование чисел"""
        for col in self.df.columns:
            self.df[col] = self.df.apply(
                lambda row: f"{float(row[col]):.0f}"
                if col not in
                ['% реализации ПЛАНА', '% реализации ПЛАНА на 20.10'] and
                row.name not in ['CvR %', 'ДРР %']
                else f"{float(row[col]):.2f}",
                axis=1
            )

        self.df = self.df.reindex(['Клики', 'Заказы', 'CvR %', 'Доход', 'CPO',
                                   'ДРР %', 'Средний чек',
                                   'Расход (до НДС и АК)'])
        self.df = self.df.reindex(
            columns=['ПЛАН', '% реализации ПЛАНА',
                     f'ПЛАН на {self.end_date_d}',
                     f'Факт с {self.start_date_d} по {self.end_date_d}',
                     f'% реализации ПЛАНА на {self.end_date_d}'])


def inner_main():
    """Основная логика скрипта"""
    ex = Table()

    # --- metrics are columns ---
    ex.fact_file()
    ex.plan_file()
    ex.plan_on_date_file()
    ex.match()
    ex.add_counted_metrics()

    # --- files are columns ---
    ex.df = ex.df.T
    ex.plan_done()
    ex.plan_on_date_done()

    ex.fin_format()

    print(ex.df)


if __name__ == '__main__':
    inner_main()