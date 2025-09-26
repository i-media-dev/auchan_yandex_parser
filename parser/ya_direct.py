import io
import json
import logging
import time
from typing import Any

from dotenv import load_dotenv
import pandas as pd
import requests
from parser.constants import (
    DEFAULT_FOLDER,
    DEFAULT_COLUMNS_CAMPAIGN,
    REPORT_FIELDS_DIRECT,
    REPORT_NAME,
    YANDEX_DIRECT_URL
)
from parser.logging_config import setup_logging
from parser.mixins import ColumnMixin, FileMixin

load_dotenv()
setup_logging()


class YandexDirectReports(ColumnMixin, FileMixin):
    """Класс для получения и сохранения данных отчетов из Яндекс direct."""

    def __init__(
        self,
        token: str,
        dates_list: list,
        login: list,
        report_fields: list = REPORT_FIELDS_DIRECT,
        columns: list = DEFAULT_COLUMNS_CAMPAIGN,
        folder_name: str = DEFAULT_FOLDER
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

    def _decode_if_bytes(self, x: Any) -> Any:
        """
        Защищенный метод. Декодирует байтовую строку в UTF-8,
        если передан bytes.
        """
        if type(x) is type(b''):
            return x.decode('utf8')
        else:
            return x

    def _get_direct_report(
        self,
        login: str,
        date_from: str,
        date_to: str
    ) -> str:
        """
        Защищенный метод.
        Получает отчет из Яндекс direct для указанного логина и периода.
        """

        headers = {
            "Authorization": "Bearer " + self.token,
            "Client-Login": login,
            "Accept-Language": "ru",
            "processingMode": "auto"
        }

        body = {
            "params": {
                "SelectionCriteria": {
                    "DateFrom": date_from,
                    "DateTo": date_to
                },
                "FieldNames": self.report_fields,
                "ReportName": REPORT_NAME,
                "ReportType": "CUSTOM_REPORT",
                "DateRangeType": "CUSTOM_DATE",
                "Format": "TSV",
                "IncludeVAT": "NO",
                "IncludeDiscount": "NO"
            }
        }

        body = json.dumps(body, indent=4)

        while True:
            try:
                response = requests.post(
                    YANDEX_DIRECT_URL,
                    body,
                    headers=headers
                )
                response.encoding = 'utf-8'

                if response.status_code == requests.codes.bad_request:

                    logging.error(
                        'Параметры запроса указаны неверно или достигнут '
                        'лимит отчетов в очереди\n'
                        'RequestId: '
                        f'{response.headers.get('RequestId', None)}\n'
                        f'JSON-код запроса: {self._decode_if_bytes(body)}\n'
                        'JSON-код ответа сервера: '
                        f'{self._decode_if_bytes(response.json())}'
                    )
                    break
                elif response.status_code == requests.codes.ok:
                    logging.info('Ответ успешно получен')
                    break
                elif response.status_code == requests.codes.created:
                    retryIn = int(response.headers.get('retryIn', 60))
                    logging.warning('Отчет еще создается')
                    time.sleep(retryIn)
                elif response.status_code == requests.codes.accepted:
                    retryIn = int(response.headers.get('retryIn', 60))
                    logging.warning('Отчет еще создается')
                    time.sleep(retryIn)
                elif response.status_code == \
                        requests.codes.internal_server_error:
                    logging.error(
                        'Ошибка. Повторить запрос позднее.\n'
                        'RequestId: '
                        f'{response.headers.get('RequestId', None)}\n'
                        'JSON-код ответа сервера: '
                        f'{self._decode_if_bytes(response.json())}'
                    )
                    break
                elif response.status_code == requests.codes.bad_gateway:
                    logging.error(
                        'Время формирования отчета превышено. '
                        'Изменить параметры запроса.\n'
                        'RequestId: '
                        f'{response.headers.get('RequestId', None)}\n'
                        f'JSON-код запроса: {self._decode_if_bytes(body)}\n'
                        'JSON-код ответа сервера: '
                        f'{self._decode_if_bytes(response.json())}'
                    )
                    break
                else:
                    logging.error(
                        'Произошла непредвиденная ошибка.\n'
                        'RequestId: '
                        f'{response.headers.get('RequestId', None)}\n'
                        f'JSON-код запроса: {self._decode_if_bytes(body)}\n'
                        'JSON-код ответа сервера: '
                        f'{self._decode_if_bytes(response.json())}'
                    )
                    break

            except requests.exceptions.ConnectionError:
                logging.error('Произошла ошибка соединения с сервером API')
                break

            except Exception as e:
                logging.error(f'ошибка: {e}')
                break

        return response.text

    def _get_all_direct_data(self) -> pd.DataFrame:
        """Метод получает данные из Яндекс direct для всех клиентов."""
        data_frames = []

        for i, login in enumerate(self.logins, 1):
            try:
                logging.info(
                    f'Выгрузка {i}/{len(self.logins)}, аккаунт: {login}')
                data = self._get_direct_report(
                    login,
                    self.dates_list[0],
                    self.dates_list[-1]
                )
                df = pd.read_csv(
                    io.StringIO(data),
                    sep='\t',
                    encoding='cp1251',
                    header=1
                )
                df['Account'] = login
                campaign_parts = self._split_campaign(df['CampaignName'])
                df = pd.concat([df, campaign_parts], axis=1)
                data_frames.append(df)

                time.sleep(1)

            except Exception as e:
                logging.error(f'Ошибка в аккаунте {login}: {e}')
                continue

        if not data_frames:
            return pd.DataFrame()

        data = pd.concat(data_frames, ignore_index=True)
        data['Source'] = 'yandex'
        data['Cost'] = data['Cost'] * 1.2 / 1000000
        data = data[~data['Date'].str.contains(
            'Total',
            case=False,
            na=False
        )]
        return data

    def save_data(self, filename_data: str) -> None:
        """
        Метод сохраняет новые данные, объединяя с существующими.
        Наследуется от миксина FileMixin
        """
        df_new = self._get_all_direct_data()
        super().save_data(df_new, filename_data)
