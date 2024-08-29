import io
import csv
import re

def validate_csv(file_data):
    csv_file = io.StringIO(file_data.decode('utf-8'))
    reader = csv.reader(csv_file, delimiter=',')
    rows = list(reader)

    if len(rows[0]) != 3:
        return [], "Headers are incorrect"

    for row in rows[1:]:
        if len(row) < 3:
            return [], f"Row with insufficient columns found: {row}"
        serial_number = row[0].strip()
        product_name = row[1].strip()
        input_image_urls = ','.join(row[2:]).strip() 

        if not serial_number:
            return [], f"Missing Serial Number: {row}"
        if not product_name:
            return [], f"Missing Product Name: {row}"
        if not input_image_urls:
            return [], f"Missing Input Image URL's"

        if re.search(r'://', serial_number) or re.search(r'://', product_name):
            return [], f"Wrong Formatted row Found: {row}"

    return rows, None
