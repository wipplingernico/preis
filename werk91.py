import requests
import json
from bs4 import BeautifulSoup

shop_url = "werk91.myshopify.com"
access_token = "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"
headers = {"X-Shopify-Access-Token": access_token}

# Kollektion finden
response = requests.get(f"https://{shop_url}/admin/api/2024-07/custom_collections.json", headers=headers)
collections = response.json()["custom_collections"]
collection_id = next(item["id"] for item in collections if item["title"] == "alle Felgen")

# Produkte in Kollektion auflisten
collects_response = requests.get(f"https://{shop_url}/admin/api/2024-07/collects.json?collection_id={collection_id}", headers=headers)
collects = collects_response.json()["collects"]

updated_variants = []

for collect in collects:
    product_id = collect["product_id"]
    product_response = requests.get(f"https://{shop_url}/admin/api/2024-07/products/{product_id}.json", headers=headers)
    product = product_response.json()["product"]
    
    for variant in product["variants"]:
        sku = variant["sku"]
        shopify_price = variant["price"]
        
        # Suche auf reifen-felgen.de
        search_url = f"https://www.reifen-felgen.de/search?query={sku}"
        search_response = requests.get(search_url)
        soup = BeautifulSoup(search_response.content, 'html.parser')
        
        price_element = soup.find("span", class_="price")  # Anpassen an tatsächliche HTML
        if price_element:
            external_price = float(price_element.text.replace("€", "").strip())
            if shopify_price >= external_price:
                # Preis aktualisieren
                update_url = f"https://{shop_url}/admin/api/2024-07/variants/{variant['id']}.json"
                update_data = {"variant": {"price": str(external_price)}}
                requests.put(update_url, headers=headers, json=update_data)
                
                # Protokollieren
                updated_variants.append({
                    "variant_id": variant["id"],
                    "old_price": shopify_price,
                    "new_price": external_price
                })

# Ausgabe der aktualisierten Varianten
for update in updated_variants:
    print(f"Updated Variant ID: {update['variant_id']}, Old Price: {update['old_price']}, New Price: {update['new_price']}")