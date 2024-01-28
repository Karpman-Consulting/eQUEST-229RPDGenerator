import re
from itertools import islice
from openpyxl import Workbook


# This is the path to the NHRList.txt file in the DOE2.3 v50e directory. Update as needed.
NHR_LIST_PATH = r'C:\doe23\EXE50e\NHRList.txt'
OUTPUT_EXCEL_PATH = 'NHRList.xlsx'

HEADER_REGEX = r'\d{4}\s{3}[A-Z]{2,}'
LINE_ITEM_REGEX = r'^\s{5}\d{7},\s{2}'


def parse_header(line):
    id_front4 = line[4:9]
    report_name = line[11:15]
    # Split the remainder of the line by 2 or more spaces, handling situationally
    line_remainder = re.split(r'\s{2,}', line[17:].strip("; \n"))

    # Determine report_desc and prim_report_id based on conditions
    if len(line_remainder) > 1:
        report_desc = line_remainder[0]
        prim_report_id = line_remainder[2] if "like " in line or "FOR METER" in line else line_remainder[1]
    else:
        report_desc = line_remainder[0][:-2]
        prim_report_id = line_remainder[0][-2:]

    return [id_front4, report_name, report_desc, prim_report_id]


def parse_line_item(line, current_header):
    entry_id = line[5:12]
    n_i = line[35:37]
    report_name = line[78:].strip(" \n")

    return [entry_id, int(n_i), report_name, current_header]


def process_file(file_path, header_regex, line_item_regex):
    wb = Workbook()
    ws = wb.active

    current_header = None

    with open(file_path, 'r') as file:
        for line in islice(file, 192, None):  # Skip first 192 lines
            # Check if line is a header
            if re.search(header_regex, line):
                current_header = parse_header(line)

            # Check if line is a line item
            elif re.search(line_item_regex, line) and current_header is not None:
                parsed_data = parse_line_item(line, current_header[1])
                ws.append(parsed_data)

    # Save to Excel
    wb.save(OUTPUT_EXCEL_PATH)


process_file(NHR_LIST_PATH, HEADER_REGEX, LINE_ITEM_REGEX)

