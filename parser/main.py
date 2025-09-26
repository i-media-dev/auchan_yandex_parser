from parser.constants import APPMETRICA_ID, CLIENT_LOGINS, METRICA_ID
from parser.decorators import time_of_script
from parser.utils import initialize_components, run


@time_of_script
def main():
    """Основная логика скрипта."""
    appmetrica, direct, metrica = initialize_components(
        CLIENT_LOGINS,
        METRICA_ID,
        APPMETRICA_ID,
    )
    run(direct, metrica, appmetrica)


if __name__ == '__main__':
    main()
