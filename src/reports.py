import json
from datetime import datetime
from typing import Optional
import os
import pandas as pd
import datetime

from dateutil.relativedelta import relativedelta

from config import DATA_DIR
from src.utils import read_exsel


def spending_by_category(transactions: pd.DataFrame, category: str, date: Optional[str] = None) -> pd.DataFrame:
    """Функция, которая возвращает траты по заданной категории за последние 3 месяца"""

    if date == None:
        date_end = datetime.datetime.now()
    else:
        date_end = datetime.datetime.strptime(date, "%d.%m.%Y")

    transactions["Дата платежа"] = pd.to_datetime(transactions["Дата платежа"], format="%d.%m.%Y")

    date_start = date_end - relativedelta(months=3)
    filtered_df = transactions[
        (transactions["Категория"] == category)
        & (transactions["Дата платежа"] >= date_start)
        & (transactions["Дата платежа"] <= date_end)
    ]

    if filtered_df.empty:
        return(f"Не найдены расходы по категории {category} за указанный период")
    else:
        total_sum = filtered_df["Сумма операции с округлением"].sum()

        result = {
            "category": category,
            "total_sum": total_sum,
            "date_start": date_start.strftime("%Y-%m-%d"),
            "date_end": date_end.strftime("%Y-%m-%d"),
        }

        return result

if __name__ == "__main__":

    operations_path = os.path.join(DATA_DIR, "operations.xlsx")
    transactions_ex = read_exsel(operations_path)
    transactions = pd.DataFrame(transactions_ex)
    print(spending_by_category(transactions, 'Супермаркеты', '10.10.2024'))