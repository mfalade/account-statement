import itertools
from typing import OrderedDict
from bs4 import BeautifulSoup

import constants
import utils


INPUT_CSV_FILE = "input.csv"


def build_balance_sheet_row(record: OrderedDict, row_type: constants.RowType):
    template_path = constants.template_path[row_type]
    row_template = BeautifulSoup(open(template_path), "html.parser")

    month, day = utils.get_month_and_day(record)
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


def get_empty_row(row_type: constants.RowType):
    template_path = constants.template_path[row_type]
    row_template = BeautifulSoup(open(template_path), "html.parser")
    row_template.find(attrs={"name": "month"}).string.replace_with("")
    row_template.find(attrs={"name": "day"}).string.replace_with("")
    row_template.find(attrs={"name": "description"}).string.replace_with("")
    row_template.find(attrs={"name": "debit"}).string.replace_with("")
    row_template.find(attrs={"name": "credit"}).string.replace_with("")
    row_template.find(attrs={"name": "balance"}).string.replace_with("")
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


if __name__ == "__main__":
    records = utils.read_file_content(file_path=INPUT_CSV_FILE)
    records.reverse()

    grouped_records = itertools.groupby(records, lambda x: x.get("date").split("/")[0])

    for group_key, group in grouped_records:
        soup = BeautifulSoup(
            open("account_statement/templates/base.html"), "html.parser"
        )
        balance_sheet_table = soup.find(id=constants.Selectors.BALANCE_SHEET.value)
        month_str = utils.get_month_name(group_key)
        batch = [item for item in group]
        for index, record in enumerate(batch):
            row_type = (
                constants.RowType.WHITE_ROW
                if index % 2 == 0
                else constants.RowType.BLACK_ROW
            )
            row = build_balance_sheet_row(record, row_type=row_type)
            balance_sheet_table.append(row)

        for extra_row in get_extra_rows_for_table_padding(batch_size=len(batch)):
            balance_sheet_table.append(extra_row)

        utils.write_to_file(
            file_path=f"results/{month_str}.html", content=soup.prettify()
        )
