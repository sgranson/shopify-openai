import requests
import openai
import datetime
import time

# === KONFIGURATION ===
SHOPIFY_API_TOKEN = os.getenv('SHOPIFY_API_TOKEN')
SHOPIFY_STORE = os.getenv('SHOPIFY_STORE')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
OPENAI_MODEL = 'gpt-4'

HEADERS_SHOPIFY = {
    'X-Shopify-Access-Token': SHOPIFY_API_TOKEN,
    'Content-Type': 'application/json'
}

openai.api_key = OPENAI_API_KEY

def get_products_without_description(limit=5):
    url = f'https://{SHOPIFY_STORE}/admin/api/2023-10/products.json?limit={limit}'
    response = requests.get(url, headers=HEADERS_SHOPIFY)
    products = response.json().get('products', [])
    return [p for p in products if not p.get('body_html')]

def generate_product_content(title):
    prompt = (
        f"Skriv en säljande och professionell produktbeskrivning för '{title}' på svenska och engelska.\n"
        f"Inkludera:\n"
        f"- En beskrivning på svenska\n"
        f"- En beskrivning på engelska\n"
        f"- Relevanta taggar (separerade med kommatecken)\n"
        f"- Ett konkurrenskraftigt prisförslag i SEK\n"
    )
    response = openai.ChatCompletion.create(
        model=OPENAI_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7
    )
    return response['choices'][0]['message']['content']

def update_product(product_id, description, tags, price):
    url = f'https://{SHOPIFY_STORE}/admin/api/2023-10/products/{product_id}.json'
    payload = {
        "product": {
            "id": product_id,
            "body_html": description,
            "tags": tags,
            "variants": [{
                "price": price
            }]
        }
    }
    response = requests.put(url, headers=HEADERS_SHOPIFY, json=payload)
    if response.status_code == 200:
        print(f"✅ Produkt {product_id} uppdaterad.")
    else:
        print(f"❌ Misslyckades att uppdatera produkt {product_id}.")
        print(response.text)

def analyze_best_sellers():
    url = f'https://{SHOPIFY_STORE}/admin/api/2023-10/orders.json?status=any&limit=250'
    response = requests.get(url, headers=HEADERS_SHOPIFY)
    orders = response.json().get('orders', [])
    product_sales = {}

    for order in orders:
        for item in order.get("line_items", []):
            title = item.get("title")
            quantity = item.get("quantity", 0)
            product_sales[title] = product_sales.get(title, 0) + quantity

    sorted_sales = sorted(product_sales.items(), key=lambda x: x[1], reverse=True)
    print("\n📈 Topp 5 bästsäljare:")
    for title, qty in sorted_sales[:5]:
        print(f"{title}: {qty} sålda")

def extract_tags_and_price(text):
    tags = []
    price = "199.00"
    for line in text.splitlines():
        if "taggar" in line.lower():
            tags_line = line.split(":")[-1]
            tags = [t.strip() for t in tags_line.split(",") if t.strip()]
        if "pris" in line.lower() and "SEK" in line:
            try:
                price = [word.replace(",", ".") for word in line.split() if word.replace(",", "").replace(".", "").isdigit()][0]
            except:
                price = "199.00"
    return tags, price

def run_ai_shopify_automation():
    print("🔁 Startar AI-batch", datetime.datetime.now())
    products = get_products_without_description(limit=10)

    for product in products:
        print(f"\n🔧 Bearbetar: {product['title']}")
        content = generate_product_content(product['title'])

        tags, price = extract_tags_and_price(content)
        description = content.strip()

        update_product(product['id'], description, ",".join(tags), price)
        time.sleep(3)

    analyze_best_sellers()

if __name__ == "__main__":
    run_ai_shopify_automation()
