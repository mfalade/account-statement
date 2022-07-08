from enum import Enum


class Selector(Enum):
    BALANCE_SHEET = "balance-sheet"
    PACKAGE_FEES = "package__fees"
    ITEM_DEPOSITED_VOLUME = "item-deposited__volume"
    ITEM_DEPOSITED_RATE = "item-deposited__rate"
    ITEM_DEPOSITED_FEES = "item-deposited__fees"
    DEPOSITS_COUNTER_VOLUME = "deposits-counter__volume"
    DEPOSITS_COUNTER_RATE = "deposits-counter__rate"
    DEPOSITS_COUNTER_FEES = "deposits-counter__fees"
    TOTAL_FEES = "total__fees"
    DEBIT_TRANSACTIONS_VOLUME = "debit-transactions__volume"
    DEBIT_TRANSACTIONS_SUM = "debit-transactions__sum"
    CREDIT_TRANSACTIONS_VOLUME = "credit-transactions__volume"
    CREDIT_TRANSACTIONS_SUM = "credit-transactions__sum"


class RowType(Enum):
    WHITE_ROW = "WHITE_ROW"
    BLACK_ROW = "BLACK_ROW"


template_path = {
    RowType.WHITE_ROW: "account_statement/templates/_table_row.html",
    RowType.BLACK_ROW: "account_statement/templates/_table_row_black.html",
    "BASE": "account_statement/templates/_base.html",
    "INPUT_CSV_1": "inputs/sheet_1.csv",
    "INPUT_CSV_2": "inputs/sheet_2.csv",
}


class FixedValue(Enum):
    ITEM_DEPOSITED_RATE = "0.22"
    DEPOSITS_COUNTER_RATE = "2.50"
    PACKAGE_FEES = "2.60"
