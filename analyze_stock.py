#!/usr/bin/env python3
import csv
import json
import os
from collections import defaultdict

def analyze_csv(file_path):
    # Data structures to store results
    outlets = {}
    all_product_ids_to_delete = set()
    
    # Read CSV file
    with open(file_path, 'r', encoding='utf-8-sig') as file:
        reader = csv.DictReader(file)
        
        for row in reader:
            outlet = row['Outlet']
            barcode_field = row['Barcode']
            
            # Initialize outlet if not exists
            if outlet not in outlets:
                outlets[outlet] = {}
            
            # Split barcodes by comma and process each
            barcodes = [bc.strip() for bc in barcode_field.split(',') if bc.strip()]
            
            for barcode in barcodes:
                if barcode not in outlets[outlet]:
                    outlets[outlet][barcode] = []
                
                # Create product object
                product = {
                    'Name': row['Name'],
                    'ProductId': int(row['ProductId']),
                    'OpeningQuantity': float(row['OpeningQuantity']),
                    'DeliveryQuantity': float(row['DeliveryQuantity']),
                    'SoldQuantity': float(row['SoldQuantity']),
                    'IsCorrect': 'x' in row['Name'].lower() and '*' in row['Name']
                }
                
                outlets[outlet][barcode].append(product)
    
    # Process each outlet
    for outlet_name, barcodes in outlets.items():
        # Find duplicated barcodes (more than one product)
        duplicated_barcodes = {bc: products for bc, products in barcodes.items() if len(products) > 1}
        
        # Sort products by ProductId (highest first)
        for barcode, products in duplicated_barcodes.items():
            products.sort(key=lambda x: x['ProductId'], reverse=True)
        
        # Update IsCorrect flags - only highest ProductId should be True if multiple are True
        for barcode, products in duplicated_barcodes.items():
            correct_products = [p for p in products if p['IsCorrect']]
            if len(correct_products) > 1:
                # Set all to False except the one with highest ProductId
                highest_id = max(p['ProductId'] for p in correct_products)
                for product in products:
                    if product['IsCorrect'] and product['ProductId'] != highest_id:
                        product['IsCorrect'] = False
        
        # Calculate correct totals for products where IsCorrect=True
        for barcode, products in duplicated_barcodes.items():
            correct_products = [p for p in products if p['IsCorrect']]
            if correct_products:
                # Should only be one correct product per barcode now
                correct_product = correct_products[0]
                correct_product['CorrectOpeningQuantity'] = sum(p['OpeningQuantity'] for p in products)
                correct_product['CorrectDeliveryQuantity'] = sum(p['DeliveryQuantity'] for p in products)
                correct_product['CorrectSoldQuantity'] = sum(p['SoldQuantity'] for p in products)
        
        # Collect ProductIds to delete (where IsCorrect=False)
        for barcode, products in duplicated_barcodes.items():
            for product in products:
                if not product['IsCorrect']:
                    all_product_ids_to_delete.add(product['ProductId'])
        
        # Save outlet JSON file
        os.makedirs('output', exist_ok=True)
        outlet_filename = f"output/{outlet_name.replace(' ', '_').replace('/', '_')}.json"
        with open(outlet_filename, 'w') as f:
            json.dump(duplicated_barcodes, f, indent=2, default=str)
    
    # Generate list of ProductIds to delete
    delete_list_file = 'output/products_to_delete.json'
    with open(delete_list_file, 'w') as f:
        json.dump(sorted(list(all_product_ids_to_delete)), f, indent=2)
    
    # Generate CSV file with correct products only
    csv_output_file = 'output/correct_products.csv'
    with open(csv_output_file, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['ProductId', 'Outlet', 'CorrectOpeningQuantity', 'CorrectSoldQuantity', 'CorrectDeliveryQuantity', 'IncorrectProductIds'])
        
        for outlet_name, barcodes in outlets.items():
            for barcode, products in barcodes.items():
                if len(products) > 1:  # Only duplicated barcodes
                    incorrect_ids = [str(p['ProductId']) for p in products if not p['IsCorrect']]
                    for product in products:
                        if product['IsCorrect']:
                            writer.writerow([
                                product['ProductId'],
                                outlet_name,
                                product.get('CorrectOpeningQuantity', product['OpeningQuantity']),
                                product.get('CorrectSoldQuantity', product['SoldQuantity']),
                                product.get('CorrectDeliveryQuantity', product['DeliveryQuantity']),
                                '|'.join(incorrect_ids)
                            ])

if __name__ == "__main__":
    analyze_csv('input/kappture-haven-stock-position.csv')
    print("Analysis complete. Check the 'output' directory for results.")