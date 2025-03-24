import os

import pandas as pd

from config import DATA_DIR
from src.utils import read_exsel

if __name__ == "__main__":

    def main():

        operations_path = os.path.join(DATA_DIR, "operations.xlsx")
        transactions = read_exsel(operations_path)
        transactions_df = pd.DataFrame(transactions)

        return transactions_df

    print(main())
    # print(spending_by_category(transactions, "Супермаркеты", '10.10.2018'))
