import logging
from parser.constants import (DEFAULT_COLUMNS_CAMPAIGN, DEFAULT_DELIMETER,
                              DEFAULT_FOLDER, DEFAULT_VALUE, DEVICES)
from parser.logging_config import setup_logging
from pathlib import Path

import pandas as pd

setup_logging()


class ColumnMixin:
    """
    Миксин-класс, объединяющий в себе общие методы работы с колонками df
    для классов:
    YandexAppMetricaReports, YandexDirectReports, YandexMetricaReports.
    """

    def __init__(
        self,
        columns: list = DEFAULT_COLUMNS_CAMPAIGN,
    ):
        self.columns = columns

    def _split_campaign(
        self,
        column,
        default_value: str = DEFAULT_VALUE,
        delimeter_str: str = DEFAULT_DELIMETER
    ):
        split_df = column.str.split(
            delimeter_str,
            n=len(self.columns)-1,
            expand=True
        )

        for i in range(len(self.columns)):
            if i >= split_df.shape[1]:
                split_df[i] = default_value
            else:
                split_df[i] = split_df[i].fillna(default_value)
        split_df = split_df.iloc[:, :len(self.columns)]
        split_df.columns = self.columns

        return split_df

    def _rename_columns(self, df):
        df['Devices'] = df['Device'].apply(lambda x: DEVICES.get(x.lower()))
        del df['Device']
        df.rename(columns={'Devices': 'Device'}, inplace=True)
        return df


class FileMixin:
    """
    Миксин-класс, объединяющий в себе общие методы работы с файлами
    для классов:
    YandexAppMetricaReports, YandexDirectReports, YandexMetricaReports.
    """

    def __init__(
        self,
        dates_list: list,
        folder_name: str = DEFAULT_FOLDER
    ):
        self.dates_list = dates_list
        self.folder = folder_name

    def _get_file_path(self, filename: str) -> Path:
        """Защищенный метод. Создает путь к файлу в указанной папке."""
        try:
            file_path = Path(__file__).parent.parent / self.folder
            file_path.mkdir(parents=True, exist_ok=True)
            return file_path / filename
        except Exception as e:
            logging.error(f'Ошибка: {e}')
            raise

    def _get_filtered_cache_data(self, filename_data: str) -> pd.DataFrame:
        """Защищенный метод, получает отфильтрованные данные из кэш-файла."""
        cache_path = self._get_file_path(filename_data)
        try:
            old_df = pd.read_csv(
                cache_path,
                sep=';',
                encoding='cp1251',
                header=0
            )

            for dates in self.dates_list:
                old_df = pd.DataFrame(old_df[~pd.Series(
                    old_df['Date']
                ).fillna('').str.contains(
                    fr'{dates}',
                    case=False,
                    na=False
                )])

            return old_df
        except FileNotFoundError:
            logging.warning('Файл кэша не найден. Первый запуск.')
            return pd.DataFrame()
        except pd.errors.EmptyDataError:
            logging.warning('Файл кэша пустой.')
            return pd.DataFrame()
        except Exception as e:
            logging.error(f'Ошибка: {e}')
            raise

    def save_data(self, df_new: pd.DataFrame, filename_data: str) -> None:
        """Метод сохраняет новые данные, объединяя с существующими."""
        df_old = self._get_filtered_cache_data(filename_data)
        try:
            temp_cache_path = self._get_file_path(filename_data)
            if df_new.empty:
                logging.warning('Нет новых данных для сохранения')
                return
            if not isinstance(df_old, pd.DataFrame) or df_old.empty:
                df_new.to_csv(
                    temp_cache_path,
                    index=False,
                    header=True,
                    sep=';',
                    encoding='cp1251'
                )
                logging.info(
                    'Новые данные сохранены. Исторические данные отсутствовали'
                )
                return
            for dates in self.dates_list:
                df_old = df_old[~df_old['Date'].fillna('').str.contains(
                    fr'{dates}', case=False, na=False)]

            df_old = pd.concat([df_new, df_old])
            df_old.to_csv(
                temp_cache_path,
                index=False,
                header=True,
                sep=';',
                encoding='cp1251'
            )
            logging.info('Данные успешно обновлены')
        except Exception as e:
            logging.error(f'Ошибка во время обновления: {e}')
            raise
