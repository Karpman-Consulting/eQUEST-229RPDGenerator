import json
import xlsxwriter


def extract_definitions_with_properties_from_schema(file_path):
    # Open and read the JSON file
    with open(file_path, 'r') as file:
        json_data = json.load(file)

    data = {}
    for definition, details in json_data["definitions"].items():
        if "properties" in details:
            data[definition] = list(details["properties"].keys())
    return data


def write_dict_to_excel(data, excel_file_path="schema_definitions.xlsx"):
    # Create a workbook and add a worksheet
    workbook = xlsxwriter.Workbook(excel_file_path)
    worksheet = workbook.add_worksheet()

    # Create a bold format for the first column
    bold = workbook.add_format({'bold': True})

    # Start from the first cell
    row = 0
    col = 0

    # Dictionary to track the maximum width of content in each column
    col_widths = {}

    # Iterate over the data and write it out row by row
    for definition, properties in data.items():
        # Write the definition in bold
        worksheet.write(row, col, definition, bold)

        # Update the column width tracker for the first column
        col_widths[col] = max(col_widths.get(col, 0), len(definition))

        for i, prop in enumerate(properties):
            worksheet.write(row, col + 1 + i, prop)

            # Update column width tracker for each property column
            col_widths[col + 1 + i] = max(col_widths.get(col + 1 + i, 0), len(prop))

        row += 1

    # Auto-adjust columns based on their maximum content width
    for col_num, width in col_widths.items():
        # Add a little extra space to the width
        worksheet.set_column(col_num, col_num, width + 1)

    # Close the workbook
    workbook.close()


if __name__ == "__main__":
    schema_file_path = "../rpd_generator/schema/ASHRAE229.schema.json"
    extracted_data = extract_definitions_with_properties_from_schema(schema_file_path)
    write_dict_to_excel(extracted_data)
