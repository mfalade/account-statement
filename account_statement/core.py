from decimal import DivisionByZero
import itertools
from typing import OrderedDict
from bs4 import BeautifulSoup

import constants
import utils


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


def inject_page_title(soup, group_key):
    start_month = utils.get_month_name(group_key, output_format="%b")
    end_digit = "01" if group_key == "12" else str(int(group_key) + 1)
    end_year = "2021" if group_key == "12" else "2020"
    end_month = utils.get_month_name(end_digit, output_format="%b")

    new_title = f"{start_month}2020-{end_month}{end_year}"
    soup.find("title").string.replace_with(new_title)

    return soup


def inject_itemized_billing(soup, month_breakdown):
    selector = constants.Selector
    itemized_billing_map = [
        dict(
            selector=selector.ITEM_DEPOSITED_VOLUME,
            breakdown_value=month_breakdown.get("ITEM DEPOSITED"),
        ),
        dict(
            selector=selector.ITEM_DEPOSITED_FEES,
            breakdown_value=month_breakdown.get("ID FEES"),
        ),
        dict(
            selector=selector.ITEM_DEPOSITED_RATE,
            breakdown_value=constants.FixedValue.ITEM_DEPOSITED_RATE.value,
        ),
        dict(
            selector=selector.DEPOSITS_COUNTER_VOLUME,
            breakdown_value=month_breakdown.get("DEPOSITS COUNTER"),
        ),
        dict(
            selector=selector.DEPOSITS_COUNTER_FEES,
            breakdown_value=month_breakdown.get("DC FEES"),
        ),
        dict(
            selector=selector.DEPOSITS_COUNTER_RATE,
            breakdown_value=constants.FixedValue.DEPOSITS_COUNTER_RATE.value,
        ),
        dict(
            selector=selector.TOTAL_FEES, breakdown_value=month_breakdown.get("TOTALS")
        ),
        dict(
            selector=selector.DEBIT_TRANSACTIONS_VOLUME,
            breakdown_value=month_breakdown.get("TOTAL DEBIT"),
        ),
        dict(
            selector=selector.DEBIT_TRANSACTIONS_SUM,
            breakdown_value=month_breakdown.get("SUM DEBIT"),
        ),
        dict(
            selector=selector.CREDIT_TRANSACTIONS_VOLUME,
            breakdown_value=month_breakdown.get("TOTAL CREDIT"),
        ),
        dict(
            selector=selector.CREDIT_TRANSACTIONS_SUM,
            breakdown_value=month_breakdown.get("SUM CREDIT"),
        ),
        dict(
            selector=selector.PACKAGE_FEES,
            breakdown_value=constants.FixedValue.PACKAGE_FEES.value,
        ),
    ]

    for item in itemized_billing_map:
        soup.find(attrs={"name": item["selector"].value}).string.replace_with(
            item["breakdown_value"]
        )

    return soup


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


if __name__ == "__main__":
    records = utils.read_file_content(
        file_path=constants.template_path["INPUT_CSV_1"], delimiter=","
    )
    months_breakdown = utils.read_file_content(
        file_path=constants.template_path["INPUT_CSV_2"], delimiter="|"
    )
    records.reverse()
    months_breakdown.reverse()

    grouped_records = itertools.groupby(records, lambda x: x.get("date").split("/")[0])

    for index, item in enumerate(grouped_records):
        group_key, group = item
        month_breakdown = months_breakdown[index]
        soup = BeautifulSoup(open(constants.template_path["BASE"]), "html.parser")

        soup = inject_page_title(soup, group_key)
        soup = inject_itemized_billing(soup, month_breakdown)

        balance_sheet_table = soup.find(id=constants.Selector.BALANCE_SHEET.value)
        month_name = utils.get_month_name(group_key)
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
            file_path=f"results/{month_name}.html", content=soup.prettify()
        )
