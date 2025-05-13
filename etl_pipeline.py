import requests
import boto3
import uuid

# --- CONFIG ---
RAPID_API_KEY = "33c24667c8msh7d540b55c83366ap153281jsn8da59a3f892c"  # Your key
PLAYER_ID = "28003"  # Lionel Messi
URL = f"https://transfermarkt6.p.rapidapi.com/players/market-value-progress?id={PLAYER_ID}"

HEADERS = {
    "x-rapidapi-host": "transfermarkt6.p.rapidapi.com",
    "x-rapidapi-key": RAPID_API_KEY
}

# DynamoDB Setup
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('PlayerMarketValue')

# --- EXTRACT ---
def extract():
    response = requests.get(URL, headers=HEADERS)
    if response.status_code == 200:
        print("✅ API call successful.")
        return response.json()
    else:
        raise Exception(f"API failed: {response.status_code} {response.text}")

# --- TRANSFORM ---
def transform(data):
    share = data.get("data", {}).get("share", {})
    values = data.get("data", {}).get("marketValueDevelopment", [])

    player_name = share.get("title", "Unknown Player")
    profile_url = share.get("url", "")
    description = share.get("description", "")

    transformed_items = []
    for entry in values:
        transformed_items.append({
            "id": str(uuid.uuid4()),
            "playerName": player_name,
            "profileUrl": profile_url,
            "description": description,
            "date": entry.get("date", "Unknown"),
            "marketValue": entry.get("value", "N/A")
        })

    return transformed_items

# --- LOAD ---
def load(items):
    if not items:
        print("⚠️ No data to load.")
        return
    for item in items:
        table.put_item(Item=item)
    print(f"✅ Loaded {len(items)} entries into DynamoDB.")

# --- DISPLAY ---
def print_table():
    items = table.scan().get('Items', [])
    if not items:
        print("ℹ️ Table is empty.")
        return
    print("\n📈 Player Market Value History:")
    for item in sorted(items, key=lambda x: x['date']):
        print(f"{item['date']} - {item['playerName']}: {item['marketValue']}")

# --- RUN ---
def run():
    raw = extract()
    cleaned = transform(raw)
    load(cleaned)
    print_table()

if __name__ == "__main__":
    run()

