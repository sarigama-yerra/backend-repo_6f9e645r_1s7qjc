import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from datetime import date

from database import db, create_document, get_documents

app = FastAPI(title="Spiritual Gratitude Journal API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return {"message": "Spiritual Gratitude Journal Backend"}


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
            response["database_name"] = "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set"
            response["connection_status"] = "Connected"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"

    return response


# ====== Schemas for request bodies (simple proxies) ======
class HandwritingIn(BaseModel):
    user_id: Optional[str] = None
    name: str
    image_url: str
    notes: Optional[str] = None

class TemplateIn(BaseModel):
    title: str
    description: Optional[str] = None
    preview_url: str
    theme: str

class TierIn(BaseModel):
    name: str
    price_monthly: float
    perks: List[str] = []
    highlight: bool = False

class ProductIn(BaseModel):
    title: str
    kind: str
    description: Optional[str] = None
    download_url: Optional[str] = None
    free: bool = True

class JournalEntryIn(BaseModel):
    user_id: Optional[str] = None
    date: Optional[date] = None
    template_id: Optional[str] = None
    handwriting_id: Optional[str] = None
    content: Optional[str] = None
    strokes_data_url: Optional[str] = None
    mood: Optional[str] = None
    intention: Optional[str] = None


# ====== CRUD endpoints ======
@app.post("/api/handwritings")
def upload_handwriting(payload: HandwritingIn):
    _id = create_document("handwriting", payload.model_dump())
    return {"id": _id}

@app.get("/api/handwritings")
def list_handwritings():
    docs = get_documents("handwriting")
    return [{**{k: (str(v) if k == "_id" else v) for k, v in d.items()}} for d in docs]


@app.post("/api/templates")
def create_template(payload: TemplateIn):
    _id = create_document("template", payload.model_dump())
    return {"id": _id}

@app.get("/api/templates")
def list_templates():
    docs = get_documents("template")
    return [{**{k: (str(v) if k == "_id" else v) for k, v in d.items()}} for d in docs]


@app.post("/api/tiers")
def create_tier(payload: TierIn):
    _id = create_document("tier", payload.model_dump())
    return {"id": _id}

@app.get("/api/tiers")
def list_tiers():
    docs = get_documents("tier")
    return [{**{k: (str(v) if k == "_id" else v) for k, v in d.items()}} for d in docs]


@app.post("/api/products")
def create_product(payload: ProductIn):
    _id = create_document("product", payload.model_dump())
    return {"id": _id}

@app.get("/api/products")
def list_products():
    docs = get_documents("product")
    return [{**{k: (str(v) if k == "_id" else v) for k, v in d.items()}} for d in docs]


@app.post("/api/journal")
def create_entry(payload: JournalEntryIn):
    _id = create_document("journalentry", payload.model_dump())
    return {"id": _id}

@app.get("/api/journal")
def list_entries(user_id: Optional[str] = None):
    flt = {"user_id": user_id} if user_id else {}
    docs = get_documents("journalentry", flt)
    return [{**{k: (str(v) if k == "_id" else v) for k, v in d.items()}} for d in docs]


# ====== Seed endpoint to prefill templates/tiers/products ======
@app.post("/api/seed")
def seed_defaults():
    """Insert some defaults if collections are empty (idempotent)."""
    try:
        # Templates
        existing_templates = get_documents("template", limit=1)
        created_templates = 0
        if not existing_templates:
            templates = [
                {
                    "title": "Lunar Gratitude",
                    "description": "Moon phases • silver ink • soft navy",
                    "theme": "lunar",
                    "preview_url": "https://images.unsplash.com/photo-1534790566855-4cb788d389ec?q=80&w=1200&auto=format&fit=crop",
                },
                {
                    "title": "Zen Garden",
                    "description": "Muted sand • raked lines • bamboo accents",
                    "theme": "zen",
                    "preview_url": "https://images.unsplash.com/photo-1519681393784-d120267933ba?q=80&w=1200&auto=format&fit=crop",
                },
                {
                    "title": "Sunrise Bloom",
                    "description": "Rose gold • dawn gradient • floral corners",
                    "theme": "sunrise",
                    "preview_url": "https://images.unsplash.com/photo-1518709268805-4e9042af9f23?q=80&w=1200&auto=format&fit=crop",
                },
            ]
            for t in templates:
                create_document("template", t)
            created_templates = len(templates)

        # Tiers
        existing_tiers = get_documents("tier", limit=1)
        created_tiers = 0
        if not existing_tiers:
            tiers = [
                {
                    "name": "Seed",
                    "price_monthly": 0,
                    "perks": ["3 templates", "Basic canvas writing", "Daily intention prompts"],
                    "highlight": False,
                },
                {
                    "name": "Bloom",
                    "price_monthly": 7,
                    "perks": ["All templates", "Custom handwriting upload", "Mood tracking", "Export as images"],
                    "highlight": True,
                },
                {
                    "name": "Ascend",
                    "price_monthly": 19,
                    "perks": ["Everything in Bloom", "Guided rituals", "Audio meditations", "Priority blessings"],
                    "highlight": False,
                },
            ]
            for tier in tiers:
                create_document("tier", tier)
            created_tiers = len(tiers)

        # Products (freebies)
        existing_products = get_documents("product", limit=1)
        created_products = 0
        if not existing_products:
            products = [
                {
                    "title": "Digital Detox Pack",
                    "kind": "guide",
                    "description": "7-day phone-lite ritual with printable cards",
                    "download_url": "#",
                    "free": True,
                },
                {
                    "title": "Manifestation Mini eBook",
                    "kind": "ebook",
                    "description": "Scripting, affirmations, and a 3-step night ritual",
                    "download_url": "#",
                    "free": True,
                },
                {
                    "title": "Morning Mantra Audio",
                    "kind": "audio",
                    "description": "5-minute breath + blessing to start radiant",
                    "download_url": "#",
                    "free": True,
                },
                {
                    "title": "Evening Unplug Ritual",
                    "kind": "guide",
                    "description": "10-minute candle + journal flow for deep rest",
                    "download_url": "#",
                    "free": True,
                },
                {
                    "title": "Prosperity Script Pages",
                    "kind": "template-pack",
                    "description": "Printable abundance scripting sheets (PDF)",
                    "download_url": "#",
                    "free": True,
                },
            ]
            for p in products:
                create_document("product", p)
            created_products = len(products)

        return {
            "templates_created": created_templates,
            "tiers_created": created_tiers,
            "products_created": created_products,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
