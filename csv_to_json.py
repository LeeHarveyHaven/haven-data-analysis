import csv
import json
import os
import re

def csv_to_json(csv_file_path, output_dir):
    data = []
    with open(csv_file_path, 'r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            clean_row = {}
            for key, value in row.items():
                clean_key = re.sub(r'[^\x00-\x7F]', '', key)
                clean_value = re.sub(r'[^\x00-\x7F]', '', value) if value else value
                if clean_key in ['OutletId', 'ProductId', 'UnitOfMeasureId', 'OpeningQuantity', 'DeliveryQuantity', 'SoldQuantity']:
                    clean_row[clean_key] = int(clean_value) if clean_value.isdigit() else 0
                else:
                    clean_row[clean_key] = clean_value
            data.append(clean_row)
    
    csv_filename = os.path.basename(csv_file_path)
    json_filename = csv_filename.replace('.csv', '.json')
    json_file_path = os.path.join(output_dir, json_filename)
    
    os.makedirs(output_dir, exist_ok=True)
    
    with open(json_file_path, 'w', encoding='utf-8') as jsonfile:
        json.dump(data, jsonfile, indent=2, ensure_ascii=True)
    
    print(f"CSV converted to JSON: {json_file_path}")
    return json_file_path

if __name__ == "__main__":
    csv_file = "/Users/leeharvey/Development/haven/haven-data-analysis/input/kappture-haven-stock-position.csv"
    output_directory = "/Users/leeharvey/Development/haven/haven-data-analysis/input"
    
    csv_to_json(csv_file, output_directory)