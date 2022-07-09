import itertools

import pdfkit
from tqdm import tqdm
from bs4 import BeautifulSoup

import constants
import utils


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


def inject_balance_sheet(soup, group):
    balance_sheet_table = soup.find(id=constants.Selector.BALANCE_SHEET.value)
    batch = [item for item in group]
    for index, record in enumerate(batch):
        row_type = (
            constants.RowType.WHITE_ROW
            if index % 2 == 0
            else constants.RowType.BLACK_ROW
        )
        row = utils.build_balance_sheet_row(record, row_type=row_type)
        balance_sheet_table.append(row)

    for extra_row in utils.get_extra_rows_for_table_padding(batch_size=len(batch)):
        balance_sheet_table.append(extra_row)

    return soup


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

    with tqdm(total=12) as progress_bar:
        for index, item in enumerate(grouped_records):
            group_key, group = item
            month_name = utils.get_month_name(group_key)
            month_breakdown = months_breakdown[index]

            soup = BeautifulSoup(open(constants.template_path["BASE"]), "html.parser")
            soup = inject_page_title(soup, group_key)
            soup = inject_balance_sheet(soup, group)
            soup = inject_itemized_billing(soup, month_breakdown)

            utils.write_to_file(
                file_path=f"results/html/{month_name}.html", content=soup.prettify()
            )
            pdfkit.from_file(
                input=f"results/html/{month_name}.html",
                output_path=f"results/pdf/{month_name}.pdf",
                options={
                    "dpi": 350,
                    "page-size": "Letter",
                },
            )
            progress_bar.update()
