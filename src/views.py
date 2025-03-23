import os
import json
import typing

from config import DATA_DIR, ROOT_DIR
from src.utils import hello_date, kart_user_info, top_transactions, exchange_rate, stock_prices

operations_path = os.path.join(DATA_DIR, "operations.xlsx")
operations_path_json = os.path.join(ROOT_DIR, "user_settings.json")


def main(date_time: str) -> typing.Any:
    """Главная функция, которая принимает на вход строку с датой и временем в формате
    YYYY-MM-DD HH:MM:SS и возвращающую JSON-ответ со следующими данными:
    - приветствие, в зависимости от времени текущего суток
    - статистику по каждой карте в выбранный промежуток времени
    - топ-5 транзакций по сумме платежа
    - курс валют
    - Стоимость акций из S&P500"""

    result_total = {}
    result_total["greeting"] = hello_date()
    result_total["cards"] = kart_user_info(date_time, operations_path)
    result_total["top_transactions"] = top_transactions(date_time, operations_path)
    result_total["currency_rates"] = exchange_rate(operations_path_json)
    result_total["stock_prices"] = stock_prices(operations_path_json)

    json_result = json.dumps(result_total, ensure_ascii=False)
    return json_result


if __name__ == "__main__":

    date_time_user = "01-10-2020 00:00:00"
    print(main(date_time_user))
