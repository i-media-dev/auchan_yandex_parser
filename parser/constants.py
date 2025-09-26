YANDEX_DIRECT_URL = 'https://api.direct.yandex.com/json/v5/reports'
"""URL для запроса отчета из Direct."""

YANDEX_METRICA_URL = 'https://api-metrika.yandex.net/stat/v1/data'
"""URL для запроса отчета из Metrica."""

YANDEX_APPMETRICA_URL = 'https://api.appmetrica.yandex.ru/stat/v1/data'
"""URL для запроса отчета из Appmetrica."""

DIRECT_FILENAME = 'auchan_direct'
"""Название файла для выгрузки Яндекс direct."""

METRICA_FILENAME = 'auchan_metrica'
"""Название файла для выгрузки Яндекс metrica."""

APPMETRICA_FILENAME = 'auchan_appmetrica'
"""Название файла для выгрузки Яндекс appmetrica."""

DEFAULT_DELIMETER = '_'
"""Делиметр Campaign по умолчанию."""

DEFAULT_VALUE = '-all'
"""Значение для подставновки в пустые ячейки по умолчанию."""

DATE_FORMAT = '%Y-%m-%d'
"""Формат дат по умолчанию ('%Y-%m-%d')."""

REPORT_NAME = 'all_reports1'
"""Имя отчета по умолчанию."""

DEFAULT_FOLDER = 'data'
"""Папка для сохранения .csv файлов по умолчанию."""

DAYS_TO_GENERATE_DIRECT = 45
"""Количество дней для генерации списка дат по умолчанию."""

DAYS_TO_GENERATE_METRICA = 4
"""Количество дней для генерации списка дат по умолчанию."""

DAYS_TO_GENERATE_APPMETRICA = 1
"""Количество дней для генерации списка дат по умолчанию."""

DAYS_BEFORE = 7
"""Период в днях (7)."""

METRICA_ID = '24584168'
"""ID Еаптека Метрика."""

APPMETRICA_ID = '4431094'
"""ID Еаптека АппМетрика."""

APPMETRICA_LIMIT = '1000'
"""Лимит выдачи отчета на страницу."""

METRICA_LIMIT = 10000
"""Лимит выдачи данных (10000)"""

DEFAULT_COLUMNS_CAMPAIGN = [
    'Geo',
    'Site_type',
    'Generation_method',
    'Category',
    'Subject',
    'Url_type'
]
"""Поля для разбивки Campaign."""

REPORT_FIELDS_DIRECT = [
    "Date",
    "CampaignName",
    "CampaignId",
    "Device",
    "Impressions",
    "Clicks",
    "Cost"
]
"""Запрашиваемые поля для Яндекс Директ."""

REPORT_FIELDS_APPMETRICA = [
    'Date',
    'CampaignName',
    'Transactions',
    'Revenue'
]
"""Запрашиваемые поля для Яндекс Аппметрики."""

REPORT_FIELDS_METRICA = [
    'Date',
    'CampaignName',
    'Device',
    'Transactions',
    'Revenue'
]
"""Запрашиваемые поля для Яндекс Аппметрики."""

CLIENT_LOGINS = [
    'imedia-auchan-cpm',
    'imedia-auchan-rmp',
    'imedia-auchanweb'
]
"""Список логинов Еаптека."""


DEVICES = {
    'pc': 'DESKTOP',
    'smartphones': 'MOBILE',
    'tv': 'SMART_TV',
    'tablets': 'TABLET'
}
"""Словарь стандаритизации значений колонки Device"""
