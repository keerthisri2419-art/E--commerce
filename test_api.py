import sys
import time
import requests

BASE_URL = "http://127.0.0.1:8000"

def run_tests():
    print("Starting automated API verification tests...")
    
    # Wait for server to boot if needed
    try:
        r = requests.get(f"{BASE_URL}/")
        r.raise_for_status()
    except Exception:
        print("API server is not running on port 8000. Please start uvicorn first.")
        sys.exit(1)
        
    print("\n--- 1. Testing Root Endpoint ---")
    r = requests.get(f"{BASE_URL}/")
    print(f"Status: {r.status_code}, Body: {r.json()}")
    assert r.status_code == 200
    
    print("\n--- 2. Testing Fetch Products ---")
    r = requests.get(f"{BASE_URL}/api/products")
    products = r.json()
    print(f"Status: {r.status_code}, Count: {len(products)}")
    assert r.status_code == 200
    assert len(products) > 0
    print(f"Sample Product [0]: ID={products[0]['id']}, Name='{products[0]['name']}', Stock={products[0]['stockLevel']}")
    
    print("\n--- 3. Testing Create Product (Anonymous -> Should Fail) ---")
    test_prod = {
        "name": "Handmade Clay Vase",
        "description": "Artisanal hand-glazed terra-cotta vase.",
        "price": 75.0,
        "category": "Soft Home",
        "style": "Craftsman",
        "sustainabilityScore": 10,
        "stockLevel": 25
    }
    r = requests.post(f"{BASE_URL}/api/products", json=test_prod)
    print(f"Status (Unauthenticated): {r.status_code}")
    assert r.status_code in [401, 403]
    
    print("\n--- 4. Testing Create Product (Seller Token -> Should Pass) ---")
    headers = {"Authorization": "Bearer demo-seller"}
    r = requests.post(f"{BASE_URL}/api/products", json=test_prod, headers=headers)
    new_prod = r.json()
    print(f"Status (Authenticated): {r.status_code}, Saved ID: {new_prod.get('id')}")
    assert r.status_code == 201
    assert new_prod["name"] == "Handmade Clay Vase"
    
    print("\n--- 5. Testing Fetch Orders (Buyer -> Should Fail 403) ---")
    buyer_headers = {"Authorization": "Bearer demo-buyer"}
    r = requests.get(f"{BASE_URL}/api/orders", headers=buyer_headers)
    print(f"Status: {r.status_code}")
    assert r.status_code == 403
    
    print("\n--- 6. Testing Fetch Orders (Seller -> Should Pass) ---")
    r = requests.get(f"{BASE_URL}/api/orders", headers=headers)
    orders = r.json()
    print(f"Status: {r.status_code}, Orders Count: {len(orders)}")
    assert r.status_code == 200
    
    print("\n--- 7. Testing Place Order ---")
    # Place order for products
    order_payload = {
        "customerName": "Julianna Vane",
        "items": [
            {
                "id": "p1",
                "name": "Orbital Desk Lamp",
                "price": 129.0,
                "quantity": 1,
                "sku": "OL-MIN-02",
                "imageUrl": "https://images.unsplash.com/photo-1507473885765-e6ed057f782c"
            }
        ],
        "value": 129.0
    }
    r = requests.post(f"{BASE_URL}/api/orders", json=order_payload)
    new_order = r.json()
    print(f"Status: {r.status_code}, Order ID: {new_order.get('id')}, Status: {new_order.get('status')}")
    assert r.status_code == 201
    assert new_order["customerName"] == "Julianna Vane"
    
    print("\n--- 8. Testing Fulfill Order ---")
    order_id = new_order["id"]
    r = requests.put(f"{BASE_URL}/api/orders/{order_id}/fulfill", headers=headers)
    fulfilled = r.json()
    print(f"Status: {r.status_code}, Fulfill Status: {fulfilled.get('status')}, Tracking: {fulfilled.get('trackingNumber')}")
    assert r.status_code == 200
    assert fulfilled["status"] == "Delivered"
    
    print("\n--- 9. Testing Payments & Wallet ---")
    headers = {"Authorization": "Bearer demo-buyer"}
    r = requests.get(f"{BASE_URL}/api/payments/wallet", headers=headers)
    wallet = r.json()
    print(f"Status (Wallet GET): {r.status_code}, Balance: {wallet.get('balance')}, CO2: {wallet.get('totalOffsetCo2')}")
    assert r.status_code == 200
    assert wallet["balance"] == 250.0

    r = requests.post(f"{BASE_URL}/api/payments/wallet/settings", json={"autoOffset": False}, headers=headers)
    wallet = r.json()
    print(f"Status (Wallet Settings): {r.status_code}, autoOffset: {wallet.get('autoOffset')}")
    assert r.status_code == 200
    assert wallet["autoOffset"] is False

    r = requests.post(f"{BASE_URL}/api/payments/wallet/settings", json={"autoOffset": True}, headers=headers)
    assert r.status_code == 200

    r = requests.get(f"{BASE_URL}/api/payments/cards", headers=headers)
    cards = r.json()
    print(f"Status (Cards list): {r.status_code}, Cards Count: {len(cards)}")
    assert r.status_code == 200
    assert len(cards) >= 2

    new_card_data = {
        "cardholderName": "Alex Rivers",
        "cardNumber": "4222 2222 2222 2222",
        "expiryDate": "11/30",
        "cvv": "123",
        "brand": "Visa"
    }
    r = requests.post(f"{BASE_URL}/api/payments/cards", json=new_card_data, headers=headers)
    new_card = r.json()
    print(f"Status (Add Card): {r.status_code}, Card ID: {new_card.get('id')}, Brand: {new_card.get('brand')}")
    assert r.status_code == 201
    assert "card-1" != new_card["id"]

    card_id = new_card["id"]
    r = requests.delete(f"{BASE_URL}/api/payments/cards/{card_id}", headers=headers)
    print(f"Status (Delete Card): {r.status_code}")
    assert r.status_code == 204

    topup_payload = {
        "amount": 50.0,
        "brand": "Visa",
        "cardNumber": "•••• 4242"
    }
    r = requests.post(f"{BASE_URL}/api/payments/wallet/topup", json=topup_payload, headers=headers)
    wallet = r.json()
    print(f"Status (Top Up): {r.status_code}, New Balance: {wallet.get('balance')}")
    assert r.status_code == 200
    assert wallet["balance"] == 300.0

    r = requests.get(f"{BASE_URL}/api/payments/transactions", headers=headers)
    txs = r.json()
    print(f"Status (Transactions list): {r.status_code}, Count: {len(txs)}")
    assert r.status_code == 200
    assert len(txs) > 0

    print("\n--- 10. Testing AI Chat Concierge ---")
    chat_payload = {
        "messages": [
            {"content": "Tell me about the tactile mug set."}
        ]
    }
    r = requests.post(f"{BASE_URL}/api/chat", json=chat_payload)
    chat_resp = r.json()
    print(f"Status: {r.status_code}, Reply: {chat_resp.get('reply')[:80]}...")
    assert r.status_code == 200
    
    print("\n--- 11. Testing AI Aesthetic Search ---")
    search_payload = {
        "query": "I need some organic wooden accessories"
    }
    r = requests.post(f"{BASE_URL}/api/search", json=search_payload)
    search_resp = r.json()
    print(f"Status: {r.status_code}, Style: {search_resp.get('style')}, Explanation: {search_resp.get('explanation')}")
    assert r.status_code == 200
    assert "style" in search_resp
    
    print("\n==============================")
    print("ALL API VERIFICATION TESTS PASSED SUCCESSFULLY!")
    print("==============================")

if __name__ == "__main__":
    run_tests()
