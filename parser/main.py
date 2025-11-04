from parser.common_report import CommonReport
from parser.constants import APPMETRICA_ID, CLIENT_LOGINS, METRICA_ID
from parser.decorators import time_of_script
from parser.utils import initialize_components, run

from presentation.pres_main import pres_run


@time_of_script
def main():
    """Основная логика скрипта."""
    appmetrica, direct, metrica = initialize_components(
        CLIENT_LOGINS,
        METRICA_ID,
        APPMETRICA_ID,
    )
    run(direct, metrica, appmetrica)
    ex = CommonReport()
    ex.save_common_report()
    pres_run()


if __name__ == '__main__':
    main()
