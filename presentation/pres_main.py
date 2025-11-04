import pandas as pd

from presentation.diagram import diagram_run
from presentation.fact_plan_period import fact_plan_period_run


def pres_run():
    with pd.ExcelWriter('pres_data.xlsx') as writer:
        fact_plan_period_run().to_excel(writer, sheet_name='fact plan period')
        diagram_run().to_excel(writer, sheet_name='diagram')
