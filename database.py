import os
import json
import threading
from dotenv import load_dotenv

# Load env variables from the root folder
dotenv_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env")
load_dotenv(dotenv_path)

# Initialize Firebase Admin & Firestore
db = None
auth_initialized = False

# Try initializing Firebase Admin
service_account_path = os.getenv("FIREBASE_SERVICE_ACCOUNT_JSON")
project_id = os.getenv("FIREBASE_PROJECT_ID", "active-anchor-k8gvj")

# Seed Data definition matching frontend/src/data.ts exactly
INITIAL_PRODUCTS = [
    {
        "id": "p1",
        "name": "Orbital Desk Lamp",
        "description": "Minimalist desk lamp with a warm natural oak base and ambient circular LED glow.",
        "price": 129.00,
        "category": "Soft Home",
        "tag": "NEW ARRIVAL",
        "imageUrl": "https://images.unsplash.com/photo-1507473885765-e6ed057f782c?auto=format&fit=crop&q=80&w=600",
        "style": "Minimal",
        "sustainabilityScore": 9,
        "sku": "OL-MIN-02",
        "stockLevel": 42,
    },
    {
        "id": "p2",
        "name": "Cloud9 ANC Headphones",
        "description": "Over-ear active noise canceling headphones in a custom desaturated steel-blue finish.",
        "price": 299.00,
        "category": "Audiophile",
        "tag": "AI MATCH",
        "imageUrl": "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?auto=format&fit=crop&q=80&w=600",
        "style": "Audiophile",
        "sustainabilityScore": 8,
        "sku": "C9-ANC-BLU",
        "stockLevel": 112,
    },
    {
        "id": "p3",
        "name": "Puffy Brew Espresso",
        "description": "Compact retro-inspired pump espresso machine in a gorgeous pastel sage green finish.",
        "price": 185.50,
        "category": "Soft Home",
        "tag": "TOP SELLER",
        "imageUrl": "https://images.unsplash.com/photo-1517701604599-bb29b565090c?auto=format&fit=crop&q=80&w=600",
        "style": "Craftsman",
        "sustainabilityScore": 8,
        "sku": "PB-ESP-SGE",
        "stockLevel": 15,
    },
    {
        "id": "p4",
        "name": "Tactile Mug Set",
        "description": "Set of four stackable ceramic mugs in soft, double-dipped lavender and sand glaze finishes.",
        "price": 45.00,
        "category": "Creative Art",
        "tag": "FOR YOU",
        "imageUrl": "https://images.unsplash.com/photo-1514228742587-6b1558fcca3d?auto=format&fit=crop&q=80&w=600",
        "style": "Craftsman",
        "sustainabilityScore": 10,
        "sku": "TM-STK-04",
        "stockLevel": 142,
    },
    {
        "id": "p5",
        "name": "Minimalist Ceramic Mug",
        "description": "Hand-thrown sand-colored ceramic mug with an unglazed raw textured bottom.",
        "price": 24.00,
        "category": "Creative Art",
        "tag": "POPULAR",
        "imageUrl": "https://images.unsplash.com/photo-1514228742587-6b1558fcca3d?auto=format&fit=crop&q=80&w=600",
        "style": "Craftsman",
        "sustainabilityScore": 9,
        "sku": "CP-MOSS-01",
        "stockLevel": 12,
    },
    {
        "id": "p6",
        "name": "Linen Art Tote",
        "description": "Heavy-duty organic linen tote bag with natural dye accents and inner pockets.",
        "price": 45.00,
        "category": "Streetwear",
        "tag": "ECO-FRIENDLY",
        "imageUrl": "https://images.unsplash.com/photo-1544816155-12df9643f363?auto=format&fit=crop&q=80&w=600",
        "style": "Minimal",
        "sustainabilityScore": 10,
        "sku": "TR-CTN-NAT",
        "stockLevel": 85,
    },
    {
        "id": "p7",
        "name": "Organic Wood Spoons",
        "description": "Set of three hand-carved cherry wood kitchen utensils finished with organic beeswax.",
        "price": 18.50,
        "category": "Soft Home",
        "tag": "HANDMADE",
        "imageUrl": "https://images.unsplash.com/photo-1588854337236-6889d631faa8?auto=format&fit=crop&q=80&w=600",
        "style": "Craftsman",
        "sustainabilityScore": 10,
        "sku": "WF-MIX-PRM",
        "stockLevel": 45,
    },
    {
        "id": "p8",
        "name": "Pure Beeswax Pillar",
        "description": "Slow-burning soy wax candle in a reusable recycled glass jar, scented with vetiver.",
        "price": 22.00,
        "category": "Soft Home",
        "tag": "ECO-LUXE",
        "imageUrl": "https://images.unsplash.com/photo-1603006905003-be475563bc59?auto=format&fit=crop&q=80&w=600",
        "style": "Bohemian",
        "sustainabilityScore": 9,
        "sku": "BW-PIL-SM",
        "stockLevel": 88,
    },
    {
        "id": "p9",
        "name": "Hand-Knit Wool Throw",
        "description": "Luxuriously thick throw hand-knit from undyed, organic Merino wool by a women's cooperative.",
        "price": 145.00,
        "category": "Soft Home",
        "tag": "COZY ESSENTIAL",
        "imageUrl": "https://images.unsplash.com/photo-1580301762395-21ce84d00bc6?auto=format&fit=crop&q=80&w=600",
        "style": "Bohemian",
        "sustainabilityScore": 9,
        "sku": "HW-THR-WOL",
        "stockLevel": 35,
    },
    {
        "id": "p10",
        "name": "Artisan Stone Mortar",
        "description": "Hand-carved from solid volcanic basalt stone, perfect for grinding organic spices and herbs.",
        "price": 58.00,
        "category": "Creative Art",
        "tag": "ARTISAN TOOLS",
        "imageUrl": "https://images.unsplash.com/photo-1595981267035-7b04ec82a89f?auto=format&fit=crop&q=80&w=600",
        "style": "Craftsman",
        "sustainabilityScore": 10,
        "sku": "MP-STN-GRN",
        "stockLevel": 18,
    },
    {
        "id": "p11",
        "name": "Grounded Cork Yoga Mat",
        "description": "Premium non-slip yoga mat crafted from organic cork and natural tree rubber backing.",
        "price": 85.00,
        "category": "Soft Home",
        "tag": "WELLNESS",
        "imageUrl": "https://images.unsplash.com/photo-1601925260368-ae2f83cf8b7f?auto=format&fit=crop&q=80&w=600",
        "style": "Minimal",
        "sustainabilityScore": 9,
        "sku": "YM-CRK-NAT",
        "stockLevel": 50,
    },
    {
        "id": "p12",
        "name": "Recycled Glass Carafe",
        "description": "Elegant hand-blown carafe with two matching tumblers, crafted entirely from recycled sea-glass.",
        "price": 65.00,
        "category": "Creative Art",
        "tag": "POPULAR",
        "imageUrl": "https://images.unsplash.com/photo-1608270586620-248524c67de9?auto=format&fit=crop&q=80&w=600",
        "style": "Minimal",
        "sustainabilityScore": 10,
        "sku": "CR-GLS-REC",
        "stockLevel": 22,
    },
    {
        "id": "p13",
        "name": "Sleek Bamboo Water Bottle",
        "description": "Vacuum-insulated double-wall stainless steel bottle with a hand-polished organic bamboo exterior.",
        "price": 38.00,
        "category": "Soft Home",
        "tag": "ECO-FRIENDLY",
        "imageUrl": "https://images.unsplash.com/photo-1602143407151-7111542de6e8?auto=format&fit=crop&q=80&w=600",
        "style": "Minimal",
        "sustainabilityScore": 10,
        "sku": "WB-BMB-01",
        "stockLevel": 75,
    },
    {
        "id": "p14",
        "name": "Terracotta Clay Pendant Light",
        "description": "Warm terracotta clay shade cast by local artisans, emitting a soft downlight.",
        "price": 165.00,
        "category": "Soft Home",
        "tag": "ARTISAN MADE",
        "imageUrl": "https://images.unsplash.com/photo-1513506003901-1e6a229e2d15?auto=format&fit=crop&q=80&w=600",
        "style": "Craftsman",
        "sustainabilityScore": 9,
        "sku": "PL-CLY-TER",
        "stockLevel": 18,
    },
    {
        "id": "p15",
        "name": "Organic Hemp Denim Jacket",
        "description": "Unisex classic fit jacket woven from durable hemp and organic cotton fibers, naturally dyed.",
        "price": 140.00,
        "category": "Streetwear",
        "tag": "SUSTAINABLE FASHION",
        "imageUrl": "https://images.unsplash.com/photo-1576995853123-5a10305d93c0?auto=format&fit=crop&q=80&w=600",
        "style": "Minimal",
        "sustainabilityScore": 9,
        "sku": "JK-HMP-NAT",
        "stockLevel": 30,
    },
    {
        "id": "p16",
        "name": "Recycled Felt Laptop Sleeve",
        "description": "Slim protective sleeve made from 100% post-consumer recycled plastic felt with a vegetable-tanned leather accent.",
        "price": 49.00,
        "category": "Soft Home",
        "tag": "UPCYCLED",
        "imageUrl": "https://images.unsplash.com/photo-1581557991964-125469da3b8a?auto=format&fit=crop&q=80&w=600",
        "style": "Minimal",
        "sustainabilityScore": 10,
        "sku": "LS-FLT-REC",
        "stockLevel": 60,
    }
]

INITIAL_ORDERS = [
    {
        "id": "TR-9821",
        "customerName": "Julianna Vane",
        "value": 84.50,
        "date": "2 hours ago",
        "status": "Pending",
        "productName": "Tactile Mug Set",
        "sku": "TM-STK-04",
        "avatarUrl": "https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&q=80&w=150",
    },
    {
        "id": "TR-9818",
        "customerName": "Marcus Sterling",
        "value": 210.00,
        "date": "Yesterday",
        "status": "Shipped",
        "productName": "Orbital Desk Lamp",
        "sku": "OL-MIN-02",
        "trackingNumber": "TH980211X",
        "avatarUrl": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?auto=format&fit=crop&q=80&w=150",
    },
    {
        "id": "TR-9815",
        "customerName": "Elise Morel",
        "value": 45.00,
        "date": "Yesterday",
        "status": "Delivered",
        "productName": "Linen Art Tote",
        "sku": "TR-CTN-NAT",
        "avatarUrl": "https://images.unsplash.com/photo-1494790108377-be9c29b29330?auto=format&fit=crop&q=80&w=150",
    },
]

INITIAL_CARDS = [
    {
        "id": "card-1",
        "cardholderName": "Gnanavel",
        "cardNumber": "•••• •••• •••• 4242",
        "expiryDate": "12/28",
        "cvv": "•••",
        "brand": "Visa",
        "uid": "demo-buyer-uid"
    },
    {
        "id": "card-2",
        "cardholderName": "Gnanavel",
        "cardNumber": "•••• •••• •••• 5555",
        "expiryDate": "08/29",
        "cvv": "•••",
        "brand": "Mastercard",
        "uid": "demo-buyer-uid"
    }
]

INITIAL_TRANSACTIONS = [
    {
        "id": "TX-001",
        "date": "2026-07-13 14:30",
        "description": "Wallet Top-up",
        "value": 150.00,
        "type": "topup",
        "method": "Visa •••• 4242",
        "offsetCo2": 0.0,
        "status": "Succeeded",
        "uid": "demo-buyer-uid"
    },
    {
        "id": "TX-002",
        "date": "2026-07-14 10:15",
        "description": "Purchased Tactile Mug Set",
        "value": 45.00,
        "type": "purchase",
        "method": "Eco-Wallet",
        "offsetCo2": 1.5,
        "status": "Succeeded",
        "uid": "demo-buyer-uid"
    },
    {
        "id": "TX-003",
        "date": "2026-07-15 05:40",
        "description": "Purchased Organic Wood Spoons",
        "value": 18.50,
        "type": "purchase",
        "method": "Mastercard •••• 5555",
        "offsetCo2": 0.8,
        "status": "Succeeded",
        "uid": "demo-buyer-uid"
    }
]

# Thread-safe Mock Firestore Class for zero-config fallback
class MockDocumentSnapshot:
    def __init__(self, doc_id, data):
        self.id = doc_id
        self._data = data
        self.exists = data is not None

    def to_dict(self):
        return self._data

class MockDocumentReference:
    def __init__(self, collection_name, doc_id, db_instance):
        self.collection_name = collection_name
        self.id = doc_id
        self.db = db_instance

    def get(self):
        data = self.db._get_data(self.collection_name, self.id)
        return MockDocumentSnapshot(self.id, data)

    def set(self, data, merge=True):
        self.db._set_data(self.collection_name, self.id, data, merge)
        return self

    def update(self, data):
        self.db._update_data(self.collection_name, self.id, data)
        return self

    def delete(self):
        self.db._delete_data(self.collection_name, self.id)
        return self

class MockCollectionReference:
    def __init__(self, collection_name, db_instance):
        self.collection_name = collection_name
        self.db = db_instance

    def document(self, doc_id=None):
        if not doc_id:
            import uuid
            doc_id = str(uuid.uuid4())
        return MockDocumentReference(self.collection_name, doc_id, self.db)

    def add(self, data, document_id=None):
        if not document_id:
            import uuid
            document_id = str(uuid.uuid4())
        doc_ref = self.document(document_id)
        doc_ref.set(data)
        return doc_ref, doc_ref

    def stream(self):
        docs = self.db._get_collection(self.collection_name)
        return [MockDocumentSnapshot(k, v) for k, v in docs.items()]

class MockFirestore:
    def __init__(self):
        self._store = {}
        self._lock = threading.Lock()

    def collection(self, name):
        return MockCollectionReference(name, self)

    def _get_collection(self, collection_name):
        with self._lock:
            if collection_name not in self._store:
                self._store[collection_name] = {}
            return dict(self._store[collection_name])

    def _get_data(self, collection_name, doc_id):
        with self._lock:
            col = self._store.get(collection_name, {})
            return col.get(doc_id)

    def _set_data(self, collection_name, doc_id, data, merge=True):
        with self._lock:
            if collection_name not in self._store:
                self._store[collection_name] = {}
            if merge and doc_id in self._store[collection_name]:
                self._store[collection_name][doc_id].update(data)
            else:
                self._store[collection_name][doc_id] = dict(data)

    def _update_data(self, collection_name, doc_id, data):
        with self._lock:
            if collection_name in self._store and doc_id in self._store[collection_name]:
                self._store[collection_name][doc_id].update(data)

    def _delete_data(self, collection_name, doc_id):
        with self._lock:
            if collection_name in self._store and doc_id in self._store[collection_name]:
                self._store[collection_name].pop(doc_id)

try:
    import firebase_admin
    from firebase_admin import credentials, firestore

    # Helper function to initialize app safely without duplicate app errors on reload
    def get_or_initialize_app(cred=None, options=None):
        try:
            return firebase_admin.get_app()
        except ValueError:
            return firebase_admin.initialize_app(cred, options)

    if service_account_path and os.path.exists(service_account_path):
        cred = credentials.Certificate(service_account_path)
        get_or_initialize_app(cred)
        db = firestore.client()
        auth_initialized = True
        print("Firebase Admin initialized via service account json file.")
    elif os.getenv("FIREBASE_SERVICE_ACCOUNT_CONTENT"):
        cred_dict = json.loads(os.getenv("FIREBASE_SERVICE_ACCOUNT_CONTENT"))
        cred = credentials.Certificate(cred_dict)
        get_or_initialize_app(cred)
        db = firestore.client()
        auth_initialized = True
        print("Firebase Admin initialized via service account raw content.")
    else:
        # Check if running in GCP environment with App Default Credentials
        try:
            try:
                firebase_admin.get_app()
            except ValueError:
                firebase_admin.initialize_app()
            db = firestore.client()
            auth_initialized = True
            print("Firebase Admin initialized via Application Default Credentials.")
        except Exception:
            # Fall back to auth-only initialization (validates ID tokens from public certificates)
            try:
                firebase_admin.get_app()
            except ValueError:
                firebase_admin.initialize_app(options={"projectId": project_id})
            auth_initialized = True
            print(f"Firebase Admin initialized for Auth only (Project: {project_id}).")
except Exception as e:
    print(f"Firebase Admin SDK initialization skipped or failed: {e}. Defaulting to Auth/DB mocks.")

# Fallback to local thread-safe mock Firestore client if Firestore could not be initialized
if db is None:
    db = MockFirestore()
    print("Firestore mock client initialized.")

def get_db():
    return db

def is_auth_initialized():
    return auth_initialized

# Dynamic Seeding function to initialize database with items
def seed_database():
    try:
        # Seed Products
        products_col = db.collection("products")
        existing_products = products_col.stream()
        if len(existing_products) == 0:
            print("Seeding initial products into the database...")
            for prod in INITIAL_PRODUCTS:
                products_col.document(prod["id"]).set(prod)
        
        # Seed Orders
        orders_col = db.collection("orders")
        existing_orders = orders_col.stream()
        if len(existing_orders) == 0:
            print("Seeding initial orders into the database...")
            for ord_data in INITIAL_ORDERS:
                orders_col.document(ord_data["id"]).set(ord_data)

        # Seed default buyer wallet
        wallets_col = db.collection("wallets")
        existing_wallets = wallets_col.stream()
        if len(existing_wallets) == 0:
            print("Seeding initial wallets into the database...")
            wallets_col.document("demo-buyer-uid").set({
                "balance": 250.0,
                "autoOffset": True,
                "totalOffsetCo2": 14.2,
                "uid": "demo-buyer-uid"
            })

        # Seed Cards
        cards_col = db.collection("cards")
        existing_cards = cards_col.stream()
        if len(existing_cards) == 0:
            print("Seeding initial cards into the database...")
            for card in INITIAL_CARDS:
                cards_col.document(card["id"]).set(card)

        # Seed Transactions
        txs_col = db.collection("transactions")
        existing_txs = txs_col.stream()
        if len(existing_txs) == 0:
            print("Seeding initial transactions into the database...")
            for tx in INITIAL_TRANSACTIONS:
                txs_col.document(tx["id"]).set(tx)
    except Exception as e:
        print(f"Failed to seed database: {e}")
