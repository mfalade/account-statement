from enum import Enum


class Selectors(Enum):
    BALANCE_SHEET = "balance-sheet"


class RowType(Enum):
    WHITE_ROW = "WHITE_ROW"
    BLACK_ROW = "BLACK_ROW"


template_path = {
    RowType.WHITE_ROW: "account_statement/templates/_table_row.html",
    RowType.BLACK_ROW: "account_statement/templates/_table_row_black.html",
}
