import datetime as dt
import logging

from dotenv import load_dotenv
import pandas as pd
import requests
from parser.constants import (
    DATE_FORMAT,
    DAYS_BEFORE,
    DEFAULT_COLUMNS_CAMPAIGN,
    DEFAULT_FOLDER,
    REPORT_FIELDS_APPMETRICA,
    YANDEX_APPMETRICA_URL,
    APPMETRICA_LIMIT,
)
from parser.logging_config import setup_logging
from parser.mixins import ColumnMixin, FileMixin

load_dotenv()
setup_logging()


class YandexAppMetricaReports(ColumnMixin, FileMixin):
    """
    Класс для получения и сохранения данных
    отчетов из Яндекс appmetrica.
    """

    def __init__(
        self,
        token: str,
        dates_list: list,
        appmetrica_id: str,
        filename_temp: str,
        report_fields: list = REPORT_FIELDS_APPMETRICA,
        columns: list = DEFAULT_COLUMNS_CAMPAIGN,
        folder_name: str = DEFAULT_FOLDER,
        limit: str = APPMETRICA_LIMIT
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
        self.appmetrica_id = appmetrica_id
        self.filename_temp = filename_temp
        self.report_fields = report_fields
        self.limit = limit or '1000'

    def _get_appmetrica_report(
        self,
        date_reports: str,
        campaign_name: str,
    ) -> list:
        """
        Защищенный метод.
        Получает отчет из Яндекс.Апметрика для указанного магазина и периода.
        """
        try:
            date_obj = dt.datetime.strptime(date_reports, DATE_FORMAT)
            days_before = date_obj - dt.timedelta(days=DAYS_BEFORE)
            days_before = days_before.strftime(DATE_FORMAT)
            url = YANDEX_APPMETRICA_URL
            headers = {
                "Authorization": f"OAuth {self.token}"}
            params = {
                "ids": self.appmetrica_id,
                "date1": date_reports,
                "date2": date_reports,
                "group": "Day",
                "metrics": "ym:ec2:ecomRevenueFiatRUB,ym:ec2:ecomOrdersCount",
                "dimensions": "ym:ec2:date",
                "limit": self.limit,
                "accuracy": "1",
                "include_undefined": "true",
                "currency": "RUB",
                "event_attribution": "last_appmetrica",
                "sort": "-ym:ec2:ecomOrdersCount",
                "lang": "ru",
                "request_domain": "ru"
            }

            filters = (
                "(exists ym:o:device with "
                "(exists(urlParamKey=='utm_campaign' "
                f"and urlParamValue=='{campaign_name}') "
                f"and specialDefaultDate>='{days_before}' "
                f"and specialDefaultDate<='{date_reports}'))"
            )
            params['filters'] = filters
            logging.info(f'Параметры запроса: {params}')

            response = requests.get(
                url,
                params=params,
                headers=headers,
            )
            logging.info(f'Полный URL запроса: {response.request.url}')
            response.raise_for_status()
            data = response.json()

            if not data or 'data' not in data or not data['data']:
                logging.warning(
                    'Нет данных для кампании '
                    f'{campaign_name} на {date_reports}'
                )
                return [date_reports, campaign_name, 0, 0.0]
            else:
                logging.info(
                    'Данные для кампании '
                    f'{campaign_name} на {date_reports} успешно получены'
                )

            first_data_item = data['data'][0]
            revenue, transactions = first_data_item.get('metrics', [0.0, 0.0])
            return [
                date_reports,
                campaign_name,
                int(float(transactions)),
                float(revenue)
            ]
        except requests.exceptions.RequestException as e:
            logging.error(f'Ошибка запроса к api: {e}')
            raise
        except Exception as e:
            logging.error(f'Ошибка: {e}')
            raise

    def _get_all_appmetrica_data(
        self,
        filename_temp: str
    ) -> pd.DataFrame:
        """
        Защищенный метод, получает данные из Яндекс Апметрика
        для указанного id и периода.
        """
        data_list = []

        df = pd.DataFrame(columns=self.report_fields)
        temp_cache_path = self._get_file_path(filename_temp)
        try:
            campaign_df = pd.read_csv(
                temp_cache_path,
                sep=';',
                encoding='cp1251'
            )
            campaigns_list = campaign_df['CampaignName'].unique().tolist()
        except FileNotFoundError:
            logging.error('Файл с кампаниями не найден')
            return df

        for date_str in self.dates_list:
            for campaign_name in campaigns_list:
                try:
                    if 'rmp' in campaign_name:
                        continue

                    data = self._get_appmetrica_report(date_str, campaign_name)
                    data_list.append(data)
                except Exception as e:
                    logging.error(
                        f'Ошибка для кампании {campaign_name} '
                        f'на дату {date_str}: {e}')
                    continue
        if data_list:
            df = pd.DataFrame(data_list, columns=self.report_fields)
        else:
            df = pd.DataFrame(columns=self.report_fields)

        df['Transactions'] = df['Transactions'].astype(int)
        df['Revenue'] = df['Revenue'].astype(float)
        df['Device'] = 'MOBILE'
        campaign_parts = self._split_campaign(df['CampaignName'])
        df = pd.concat([df, campaign_parts], axis=1)

        return df

    def save_data(self, filename_data: str) -> None:
        """
        Метод сохраняет новые данные, объединяя с существующими.
        Наследуется от миксина FileMixin
        """
        df_new = self._get_all_appmetrica_data(self.filename_temp)
        super().save_data(df_new, filename_data)
