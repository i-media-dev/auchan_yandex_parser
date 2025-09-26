import logging

from dotenv import load_dotenv
import pandas as pd
import requests
from parser.logging_config import setup_logging
from parser.constants import (
    DEFAULT_FOLDER,
    YANDEX_METRICA_URL,
    METRICA_LIMIT,
    REPORT_FIELDS_METRICA,
    DEFAULT_COLUMNS_CAMPAIGN,
)
from parser.mixins import ColumnMixin, FileMixin

setup_logging()
load_dotenv()


class YandexMetricaReports(ColumnMixin, FileMixin):
    """Класс для получения и сохранения данных отчетов из Яндекс metrica."""

    def __init__(
        self,
        token: str,
        dates_list: list,
        login: list,
        metrica_id: str,
        report_fields: list = REPORT_FIELDS_METRICA,
        columns: list = DEFAULT_COLUMNS_CAMPAIGN,
        folder_name: str = DEFAULT_FOLDER,
        limit: int = METRICA_LIMIT
    ):
        FileMixin.__init__(
            self,
            dates_list=dates_list,
            folder_name=folder_name
        )
        ColumnMixin.__init__(self, columns=columns)
        if not token:
            logging.error('Токен отсутствует или не действителен')
        self.token = token
        self.logins = login
        self.report_fields = report_fields
        self.metrica_id = metrica_id
        self.limit = limit

    def _get_metrica_reports(self):
        """
        Защищенный метод.
        Получает отчет из Яндекс metrica для указанного id и периода.
        """
        start_date = self.dates_list[0]
        end_date = self.dates_list[-1]
        url = YANDEX_METRICA_URL
        headers = {
            "Authorization": f"OAuth {self.token}"
        }
        params = {
            "ids": self.metrica_id,
            "metrics": "ym:s:ecommercePurchases,ym:s:ecommerceRevenue",
            "dimensions": "ym:s:date,ym:s:lastsignDirectClickOrder, "
            "ym:s:DeviceCategory",
            "date1": start_date,
            "date2": end_date,
            "accuracy": "full",
            "limit": self.limit
        }
        try:
            response = requests.get(url, headers=headers, params=params)
            if response.status_code == requests.codes.ok:
                data = response.json()

                if not data or 'data' not in data or not data['data']:
                    logging.warning('Нет данных для кампании ')
                    return []

                return data['data']
            else:
                logging.error(f'Ошибка API: {response.status_code}')
                return []
        except Exception as e:
            logging.error(f'Ошибка: {e}')
            return []

    def _get_all_metrika_data(self):
        """Защищенный метод, получает все данные из Яндекс metrica."""
        result = []
        data = self._get_metrica_reports()
        try:
            for i in data:
                if '-' in str(i['dimensions'][1]['name']):
                    result.append(
                        [
                            i['dimensions'][0]['name'],
                            i['dimensions'][1]['name'].split('|')[0],
                            i['dimensions'][2]['name'],
                            int(i['metrics'][0]),
                            int(float(i['metrics'][1]))
                        ]
                    )

            df = pd.DataFrame(result, columns=self.report_fields)
            campaign_parts = self._split_campaign(df['CampaignName'])
            df = pd.concat([df, campaign_parts], axis=1)
            df = self._rename_columns(df)
            return df
        except Exception as e:
            logging.error(f'Ошибка при получении данных из метрики: {e}')
            raise

    def save_data(self, filename_data: str) -> None:
        """
        Метод сохраняет новые данные, объединяя с существующими.
        Наследуется от миксина FileMixin
        """
        df_new = self._get_all_metrika_data()
        super().save_data(df_new, filename_data)
