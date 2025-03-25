import json
import logging
import os
import typing

import pandas as pd

from config import LOGS_DIR

log_file_path = os.path.join(LOGS_DIR, "services.log")
file_logger = logging.getLogger("services")
file_handler = logging.FileHandler(log_file_path, encoding="utf-8", mode="w")
file_formatter = logging.Formatter("%(asctime)s - %(name)s – %(funcName)s – %(levelname)s - %(message)s")
file_handler.setFormatter(file_formatter)
file_logger.addHandler(file_handler)
file_logger.setLevel(logging.DEBUG)


def profitable_cashback(data: pd.DataFrame, year: int, month: int) -> typing.Any:
    """Функция для анализа, какие категории кэшбека наиболее выгодные. Рассчитывает, какие
    суммы потрачены на каждую категорию операций и вычисляет возможный кэшбек по ним"""

    filtered_df = data[(data["Дата платежа"].dt.year == year) & (data["Дата платежа"].dt.month == month)]

    group_df = filtered_df.groupby(["Категория"])
    sum_df = group_df.agg({"Сумма операции с округлением": "sum"})

    sum_df["Возможный кэшбек"] = sum_df["Сумма операции с округлением"] * 0.01

    result = sum_df.sort_values(by="Возможный кэшбек", ascending=False)

    cashback_dict = result["Возможный кэшбек"].to_dict()

    if cashback_dict != {}:
        file_logger.info("Категории и суммы кэшбеков успешно определены")
        json_result = json.dumps(cashback_dict, ensure_ascii=False)
        return json_result
    else:
        file_logger.error("JSON объект не создан.")
        raise ValueError("Проверьте правильность переданных данных. Словарь не создан.")
