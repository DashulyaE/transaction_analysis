import datetime
import os
from os import rename

import pandas as pd
from config import DATA_DIR

def hello_date() -> str:
    """Функция, которая в зависимости от текущего времени возвращает пользователю разные приветствия"""

    day_now = datetime.datetime.now()
    time_now = day_now.hour
    if time_now >= 0 and time_now < 6:
        greeting = "Доброй ночи"
        return greeting
    elif time_now >= 6 and time_now < 12:
        greeting = "Доброе утро"
        return greeting
    elif time_now >= 12 and time_now < 18:
        greeting = "Добрый день"
        return greeting
    else:
        greeting = "Добрый вечер"
        return greeting


def kart_user_info(user_date: str):
    """Функция, которая возвращает информацию из файла транзакций по карте:
    последние 4 цифры номера карты, общая сумма расходов и кэшбек"""

    operations_path = os.path.join(DATA_DIR, "operations.xlsx")
    required_columns = ['Дата операции','Номер карты','Сумма операции','Сумма платежа','Кэшбэк','Сумма операции с округлением']
    if os.path.exists(operations_path):
        excel_df = pd.read_excel(operations_path)
        if excel_df.empty:
            print("Анализируемый файл пустой")
            return False
        else:
            for column in required_columns:
                if column not in excel_df.columns:
                    print(f"Отсутствует необходимый столбец: {column}")
                    return False
            excel_df['Дата операции'] = pd.to_datetime(excel_df['Дата операции'], format='%d.%m.%Y %H:%M:%S')
            start_date = user_date
            end_date = datetime.datetime.now()
            filtered_df = excel_df[(excel_df['Дата операции'] >= start_date) & (excel_df['Дата операции'] <= end_date)]
            group_df = filtered_df.groupby('Номер карты').agg(
                total_spent=('Сумма операции с округлением', 'sum'),
                cashback=('Кэшбэк', 'sum')
            ).reset_index()
            group_df = group_df.rename(columns={'Номер карты': 'last_digits'})
            return group_df.to_dict(orient="records")
    else:
        print("Файл с транзакциями не найден")


if __name__ == '__main__':

    print(kart_user_info('01-10-2021 00:00:00'))