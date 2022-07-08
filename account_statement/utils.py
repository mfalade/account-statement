import csv
from datetime import datetime
from typing import List, OrderedDict, Tuple


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
