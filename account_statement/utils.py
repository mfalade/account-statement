import csv
from datetime import datetime
from typing import List, OrderedDict, Tuple
from bs4 import BeautifulSoup

import constants


def read_file_content(file_path: str, delimiter: str = "") -> List[OrderedDict]:
    with open(file_path) as csv_file:
        file_content = csv.DictReader(csv_file, delimiter=delimiter)
        return [line for line in file_content]


def get_month_and_day(record: OrderedDict) -> Tuple[str]:
    date_str = record.get("date")
    [month, day, _] = date_str.split("/")
    return month, day


def write_to_file(file_path: str, content: str) -> None:
    with open(file_path, "w") as output_file:
        output_file.write(content)


def get_month_name(month_digit: str, output_format: str = "%B") -> str:
    return datetime.strptime(str(month_digit), "%m").strftime(output_format)


def get_empty_row(row_type: constants.RowType):
    COLUMNS = ["month", "day", "description", "debit", "credit", "balance"]
    template_path = constants.template_path[row_type]
    row_template = BeautifulSoup(open(template_path), "html.parser")
    for column in COLUMNS:
        row_template.find(attrs={"name": column}).string.replace_with("")

    return row_template


def get_extra_rows_for_table_padding(batch_size: int):
    rows = [
        get_empty_row(row_type=constants.RowType.WHITE_ROW),
        get_empty_row(row_type=constants.RowType.BLACK_ROW),
        get_empty_row(row_type=constants.RowType.WHITE_ROW),
        get_empty_row(row_type=constants.RowType.BLACK_ROW),
    ]
    if batch_size % 2 != 0:
        return rows[1:]
    return rows


def build_balance_sheet_row(record: OrderedDict, row_type: constants.RowType):
    template_path = constants.template_path[row_type]
    row_template = BeautifulSoup(open(template_path), "html.parser")

    month, day = get_month_and_day(record)
    row_template.find(attrs={"name": "month"}).string.replace_with(month)
    row_template.find(attrs={"name": "day"}).string.replace_with(day)
    row_template.find(attrs={"name": "description"}).string.replace_with(
        record.get("description")
    )
    row_template.find(attrs={"name": "debit"}).string.replace_with(
        record.get("NEW DEBITS")
    )
    row_template.find(attrs={"name": "credit"}).string.replace_with(
        record.get("NEW CREDITS")
    )
    row_template.find(attrs={"name": "balance"}).string.replace_with(
        record.get("NEW BALANCE")
    )

    return row_template
