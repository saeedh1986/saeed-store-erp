"""
Zoho Books CSV Import Script for Saeed Store ERP V2
Imports: Products (Items), Customers (Contacts), Vendors
"""
import csv
import re
import httpx
from pathlib import Path

# Configuration
ERP_API_URL = "http://erp.s3eed.ae/api/v1"  # Change to localhost:8000 for local testing
ZOHO_FOLDER = Path("/Volumes/SaeedCloud/Saeed'sCloud/workspaceAG/zoho book ")

def parse_price(price_str: str) -> int:
    """Convert 'AED 187.80' to cents (18780)"""
    if not price_str:
        return 0
    match = re.search(r'[\d.]+', price_str.replace(',', ''))
    if match:
        return int(float(match.group()) * 100)
    return 0

def parse_stock(stock_str: str) -> float:
    """Parse stock value"""
    try:
        return float(stock_str) if stock_str else 0.0
    except:
        return 0.0

def import_products():
    """Import Items from Zoho Books"""
    print("📦 Importing Products...")
    
    with open(ZOHO_FOLDER / "Item.csv", encoding='utf-8') as f:
        reader = csv.DictReader(f)
        products = []
        
        for row in reader:
            sku = row.get('SKU', '').strip()
            if not sku or sku == 'Total':
                continue
                
            product = {
                "sku": sku,
                "name": row.get('Item Name', 'Unknown'),
                "description": row.get('Description', ''),
                "price": parse_price(row.get('Rate', '0')) / 100.0,  # API expects float
                "cost_price": parse_price(row.get('Purchase Rate', '0')) / 100.0,
                "tax_rate": 0.05,  # Default 5% UAE VAT
                "is_active": row.get('Status', 'Active') == 'Active',
                "opening_stock": parse_stock(row.get('Stock On Hand', '0'))
            }
            products.append(product)
    
    print(f"Found {len(products)} products to import")
    
    # Send to ERP
    with httpx.Client(timeout=30) as client:
        for p in products:
            try:
                # Create Product
                resp = client.post(f"{ERP_API_URL}/inventory/products", json={
                    "sku": p['sku'],
                    "name": p['name'],
                    "description": p['description'],
                    "price": p['price'],
                    "cost_price": p['cost_price'],
                    "tax_rate": p['tax_rate'],
                    "is_active": p['is_active']
                })
                
                if resp.status_code in [200, 201]:
                    print(f"  ✅ {p['sku']} - {p['name']}")
                    
                    # Add opening stock if > 0
                    if p['opening_stock'] > 0:
                        # First get product ID
                        product_data = resp.json()
                        product_id = product_data.get('id')
                        
                        if product_id:
                            client.post(f"{ERP_API_URL}/inventory/moves", json={
                                "product_id": product_id,
                                "quantity": p['opening_stock'],
                                "type": "adjustment",
                                "reference": "ZOHO-IMPORT",
                                "description": "Opening stock from Zoho Books"
                            })
                else:
                    print(f"  ⚠️ {p['sku']} - {resp.text}")
                    
            except Exception as e:
                print(f"  ❌ {p['sku']} - Error: {e}")
    
    return len(products)

def import_contacts():
    """Import Customers from Zoho Books"""
    print("\n👥 Importing Customers...")
    
    with open(ZOHO_FOLDER / "Contacts.csv", encoding='utf-8') as f:
        reader = csv.DictReader(f)
        customers = []
        
        for row in reader:
            name = row.get('Display Name', '').strip()
            email = row.get('EmailID', '').strip()
            
            if not name:
                continue
            
            # Generate email if missing
            if not email:
                email = f"{name.lower().replace(' ', '.')}@imported.local"
            
            customers.append({
                "email": email,
                "full_name": name
            })
    
    print(f"Found {len(customers)} customers to import")
    
    with httpx.Client(timeout=30) as client:
        for c in customers:
            try:
                resp = client.post(f"{ERP_API_URL}/customers", json=c)
                if resp.status_code in [200, 201]:
                    print(f"  ✅ {c['full_name']}")
                else:
                    print(f"  ⚠️ {c['full_name']} - {resp.text}")
            except Exception as e:
                print(f"  ❌ {c['full_name']} - Error: {e}")
    
    return len(customers)

def import_vendors():
    """Import Vendors from Zoho Books"""
    print("\n🏭 Importing Vendors...")
    
    with open(ZOHO_FOLDER / "Vendors.csv", encoding='utf-8') as f:
        reader = csv.DictReader(f)
        vendors = []
        
        for row in reader:
            name = row.get('Display Name', '').strip()
            email = row.get('EmailID', '').strip()
            
            if not name:
                continue
            
            if not email:
                email = f"{name.lower().replace(' ', '.').replace(',', '')}@vendor.local"
            
            vendors.append({
                "email": email,
                "full_name": name,
                "is_vendor": True
            })
    
    print(f"Found {len(vendors)} vendors to import")
    # Note: Vendor import would need a dedicated endpoint - for now they go as customers
    
    return len(vendors)

if __name__ == "__main__":
    print("=" * 50)
    print("🚀 Zoho Books Data Import")
    print("=" * 50)
    
    products_count = import_products()
    customers_count = import_contacts()
    vendors_count = import_vendors()
    
    print("\n" + "=" * 50)
    print(f"✅ Import Complete!")
    print(f"   Products: {products_count}")
    print(f"   Customers: {customers_count}")
    print(f"   Vendors: {vendors_count} (pending dedicated endpoint)")
    print("=" * 50)
