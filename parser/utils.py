import datetime as dt
import logging
import os
from dotenv import load_dotenv
from parser.constants import (
    APPMETRICA_FILENAME,
    DATE_FORMAT,
    DAYS_TO_GENERATE_APPMETRICA,
    DAYS_TO_GENERATE_DIRECT,
    DAYS_TO_GENERATE_METRICA,
    DIRECT_FILENAME,
    METRICA_FILENAME,
)
from parser.logging_config import setup_logging
from parser.ya_appmetrica import YandexAppMetricaReports
from parser.ya_direct import YandexDirectReports
from parser.ya_metrica import YandexMetricaReports


setup_logging()


def get_date_list(
    days_int: int,
    stop_int: int = 0,
    step_int: int = 1
) -> list[str]:
    """Функция генерирует список дат за указанное количество дней."""
    dates_list = []

    for i in range(days_int, stop_int, step_int):
        tempday = dt.datetime.now()
        tempday -= dt.timedelta(days=i)
        tempday_str = tempday.strftime(DATE_FORMAT)
        dates_list.append(tempday_str)
    return dates_list


def initialize_components(
    logins: list[str],
    client_m_id: str,
    client_am_id: str,
) -> tuple:
    """
    Инициализирует и возвращает все необходимые
    компоненты для работы проекта.
    """
    load_dotenv()

    token_direct = str(os.getenv('YANDEX_DIRECT_TOKEN'))
    token_metrica = str(os.getenv('YANDEX_METRICA_TOKEN'))
    token_appmetrica = str(os.getenv('YANDEX_APPMETRICA_TOKEN'))

    if not token_direct or not token_appmetrica or not token_metrica:
        logging.error('Отсутствуют переменные окружения')
        raise ValueError

    date_list_direct = get_date_list(DAYS_TO_GENERATE_DIRECT, 0, -1)
    date_list_appmetrica = get_date_list(DAYS_TO_GENERATE_APPMETRICA, 2)
    date_list_metrica = get_date_list(DAYS_TO_GENERATE_METRICA, 0, -1)

    metrica = YandexMetricaReports(
        token=token_metrica,
        dates_list=date_list_metrica,
        login=logins,
        metrica_id=client_m_id
    )

    direct = YandexDirectReports(
        token=token_direct,
        dates_list=date_list_direct,
        login=logins
    )

    appmetrica = YandexAppMetricaReports(
        token=token_appmetrica,
        dates_list=date_list_appmetrica,
        appmetrica_id=client_am_id,
        filename_temp=f'{DIRECT_FILENAME}.csv',
    )

    return appmetrica, direct, metrica


def run(
    obj_direct: YandexDirectReports,
    obj_metrica: YandexMetricaReports,
    obj_appmetrica: YandexAppMetricaReports,
) -> None:
    """Функция запуска активных методов объектов класса."""
    obj_direct.save_data(filename_data=f'{DIRECT_FILENAME}.csv')
    obj_metrica.save_data(filename_data=f'{METRICA_FILENAME}.csv')
    # obj_appmetrica.save_data(filename_data=f'{APPMETRICA_FILENAME}.csv')
