import json
import unittest
from datetime import datetime
from unittest.mock import patch

import pandas as pd
import os
import tempfile
import pytest

from src.utils import read_exsel, read_json, kart_user_info, top_transactions, hello_date

def test_hello_date():
    with patch('datetime.datetime') as mock_datetime:
        mock_datetime.now.return_value = datetime(2023, 10, 10, 2, 0, 0)
        assert hello_date() == "Доброй ночи"

    with patch('datetime.datetime') as mock_datetime:
        mock_datetime.now.return_value = datetime(2023, 10, 10, 8, 0, 0)
        assert hello_date() == "Доброе утро"

    with patch('datetime.datetime') as mock_datetime:
        mock_datetime.now.return_value = datetime(2023, 10, 10, 14, 0, 0)
        assert hello_date() == "Добрый день"

    with patch('datetime.datetime') as mock_datetime:
        mock_datetime.now.return_value = datetime(2023, 10, 10, 19, 0, 0)
        assert hello_date() == "Добрый вечер"


def test_read_exsel_valid_file():
    data = {
        "Дата операции": ["2023-01-01"],
        "Номер карты": ["1234 5678 9012 3456"],
        "Сумма операции": [100],
        "Сумма платежа": [100],
        "Кэшбэк": [1],
        "Сумма операции с округлением": [101],
    }
    df = pd.DataFrame(data)

    with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as tmp_file:
        df.to_excel(tmp_file.name, index=False)

        result_df = read_exsel(tmp_file.name)
        assert not result_df.empty
        assert set(result_df.columns) == set(data.keys())

    os.remove(tmp_file.name)


def test_read_exsel_empty_file():
    with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as tmp_file:
        pd.DataFrame().to_excel(tmp_file.name, index=False)

        with pytest.raises(ValueError, match="Анализируемый файл пустой"):
            read_exsel(tmp_file.name)

    os.remove(tmp_file.name)


def test_read_exsel_missing_column():
    data = {
        "Дата операции": ["2023-01-01"],
        "Номер карты": ["1234 5678 9012 3456"],
        "Сумма операции": [100],
        "Сумма платежа": [100],
        "Кэшбэк": [1],
        # "Сумма операции с округлением" отсутствует
    }
    df = pd.DataFrame(data)

    with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as tmp_file:
        df.to_excel(tmp_file.name, index=False)

        with pytest.raises(ValueError, match="Отсутствует необходимый столбец: Сумма операции с округлением"):
            read_exsel(tmp_file.name)

    os.remove(tmp_file.name)


def test_read_exsel_file_not_found():
    with pytest.raises(ValueError, match="Файл с транзакциями не найден"):
        read_exsel("non_existing_file.xlsx")


class TestReadJson(unittest.TestCase):

    def test_read_valid_json(self):
        # Создаем временный JSON файл
        valid_json_content = '{"currencies": ["USD", "EUR"], "stocks": ["AAPL", "MSFT"]}'
        with tempfile.NamedTemporaryFile(delete=False, suffix=".json") as temp_file:
            temp_file.write(valid_json_content.encode("utf-8"))
            temp_file.close()
            result = read_json(temp_file.name)
            self.assertEqual(result, json.loads(valid_json_content))
            os.remove(temp_file.name)

    def test_file_not_found(self):
        with self.assertRaises(ValueError) as context:
            read_json("non_existent_file.json")
        self.assertEqual(str(context.exception), "Файл с настройками не найден")

    def test_invalid_json(self):
        invalid_json_content = '{"currencies": ["USD", "EUR", "invalid json"'
        with tempfile.NamedTemporaryFile(delete=False, suffix=".json") as temp_file:
            temp_file.write(invalid_json_content.encode("utf-8"))
            temp_file.close()
            result = read_json(temp_file.name)
            self.assertTrue(result.startswith("Ошибка чтения файла"))
            os.remove(temp_file.name)


class TestKartUserInfo(unittest.TestCase):

    @patch("src.utils.read_exsel")
    def test_kart_user_info(self, mock_read_exsel):
        # Настраиваем мок
        test_data = {
            "Дата операции": ["01.10.2023 10:00:00", "02.10.2023 12:00:00", "03.10.2023 14:00:00"],
            "Номер карты": ["1234567812345678", "1234567812345678", "8765432187654321"],
            "Сумма операции с округлением": [50.0, 30.0, 80.0],
            "Кэшбэк": [5.0, 3.0, 7.0],
        }

        df = pd.DataFrame(test_data)
        mock_read_exsel.return_value = df

        user_date = "01.10.2023 00:00:00"
        operations_path = "fake_path.xlsx"
        result = kart_user_info(user_date, operations_path)
        expected_result = [
            {"last_digits": "1234567812345678", "total_spent": 80.0, "cashback": 8.0},
            {"last_digits": "8765432187654321", "total_spent": 80.0, "cashback": 7.0},
        ]
        self.assertEqual(result, expected_result)

    @patch("src.utils.read_exsel")
    def test_kart_user_info_no_transactions(self, mock_read_exsel):
        mock_read_exsel.return_value = pd.DataFrame(
            columns=["Дата операции", "Номер карты", "Сумма операции с округлением", "Кэшбэк"]
        )
        user_date = "01.10.2023 00:00:00"
        operations_path = "fake_path.xlsx"
        result = kart_user_info(user_date, operations_path)
        self.assertEqual(result, [])


@patch("src.utils.read_exsel")
def test_top_transactions(mock_read_exsel):
    # Заменим реальное чтение Excel на наш фиктивный метод
    data = {
        "Дата операции": [
            "01.01.2023 10:00:00",
            "02.01.2023 10:00:00",
            "03.01.2023 10:00:00",
            "04.01.2023 10:00:00",
            "05.01.2023 10:00:00",
            "01.02.2023 10:00:00",
            "01.03.2023 10:00:00",
        ],
        "Сумма операции с округлением": [1000, 2000, 1500, 3000, 2500, 4000, 3500],
        "Сумма платежа": [1000, 2000, 1500, 3000, 2500, 4000, 3500],
        "Категория": ["Food", "Transport", "Utilities", "Entertainment", "Groceries", "Investments", "Savings"],
        "Описание": ["Grocery shopping", "Bus fare", "Electricity bill", "Movie tickets", "Weekly shopping",
                     "Stocks purchase", "Bank interest"]
    }
    df = pd.DataFrame(data)
    mock_read_exsel.return_value = df
    df["Дата операции"] = pd.to_datetime(df["Дата операции"], format="%d.%m.%Y %H:%M:%S")
    user_date = "01.01.2023"
    operations_path = "dummy_path"  # Не используется, так как мы подменяем метод
    result = top_transactions(user_date, operations_path)

    expected_result = [
        {"date": "01.02.2023", "amount": 4000, "category": "Investments", "description": "Stocks purchase"},
        {"date": "01.03.2023", "amount": 3500, "category": "Savings", "description": "Bank interest"},
        {"date": "04.01.2023", "amount": 3000, "category": "Entertainment", "description": "Movie tickets"},
        {"date": "05.01.2023", "amount": 2500, "category": "Groceries", "description": "Weekly shopping"},
        {"date": "02.01.2023", "amount": 2000, "category": "Transport", "description": "Bus fare"}
    ]

    # Проверка результатов
    assert result == expected_result, f"Expected {expected_result}, but got {result}"
