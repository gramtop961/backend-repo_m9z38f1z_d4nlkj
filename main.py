import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from bson import ObjectId

from database import db, create_document, get_documents
from schemas import Product, Order

app = FastAPI(title="TNtrendz API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "TNtrendz backend running"}

@app.get("/test")
def test_database():
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }
    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
            response["database_name"] = getattr(db, 'name', None) or "✅ Connected"
            response["connection_status"] = "Connected"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"
    return response

# Seed example products (idempotent)
SAMPLE_PRODUCTS = [
    {
        "title": "AquaFlex Active Tee",
        "description": "Breathable performance tee in ocean teal",
        "price": 1299.0,
        "category": "Apparel",
        "image": "https://images.unsplash.com/photo-1520975922203-b7e8941ef6b6?auto=format&fit=crop&w=1200&q=60",
        "rating": 4.6,
        "in_stock": True,
    },
    {
        "title": "Coral Glide Sneakers",
        "description": "Lightweight everyday sneakers with coral accents",
        "price": 3499.0,
        "category": "Footwear",
        "image": "https://images.unsplash.com/photo-1542291026-7eec264c27ff?auto=format&fit=crop&w=1200&q=60",
        "rating": 4.7,
        "in_stock": True,
    },
    {
        "title": "Navy Atlas Backpack",
        "description": "Minimal daypack in deep navy, laptop sleeve",
        "price": 2799.0,
        "category": "Accessories",
        "image": "https://images.unsplash.com/photo-1501504905252-473c47e087f8?auto=format&fit=crop&w=1200&q=60",
        "rating": 4.5,
        "in_stock": True,
    },
]

@app.post("/seed")
def seed_products():
    if db is None:
        raise HTTPException(status_code=500, detail="Database not configured")
    inserted = 0
    for p in SAMPLE_PRODUCTS:
        exists = db["product"].find_one({"title": p["title"]})
        if not exists:
            create_document("product", p)
            inserted += 1
    return {"inserted": inserted}

@app.get("/products", response_model=List[Product])
def list_products():
    docs = get_documents("product")
    # Convert Mongo docs to Pydantic by stripping _id
    results = []
    for d in docs:
        d.pop("_id", None)
        results.append(Product(**d))
    return results

class CheckoutRequest(BaseModel):
    items: List[dict]

@app.post("/checkout")
def checkout(data: CheckoutRequest):
    if not data.items:
        raise HTTPException(status_code=400, detail="Cart is empty")
    subtotal = sum((item.get("price", 0) * item.get("quantity", 1)) for item in data.items)
    shipping = 0.0 if subtotal >= 999 else 99.0
    total = subtotal + shipping
    order = Order(
        items=[
            {
                "product_id": str(item.get("product_id", "")),
                "title": item.get("title", ""),
                "price": float(item.get("price", 0)),
                "quantity": int(item.get("quantity", 1)),
                "image": item.get("image"),
            }
            for item in data.items
        ],
        subtotal=subtotal,
        shipping=shipping,
        total=total,
    )
    order_id = create_document("order", order)
    return {"order_id": order_id, "subtotal": subtotal, "shipping": shipping, "total": total, "currency": "INR"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
