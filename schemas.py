"""
Database Schemas for Spiritual Gratitude Journal

Each Pydantic model corresponds to one MongoDB collection (lowercased class name).
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date

class User(BaseModel):
    name: str = Field(..., description="Full name")
    email: str = Field(..., description="Email address")
    avatar_url: Optional[str] = Field(None)

class Handwriting(BaseModel):
    user_id: Optional[str] = Field(None, description="Owner user id (string)")
    name: str = Field(..., description="Display name for handwriting style")
    image_url: str = Field(..., description="Data URL or public URL of handwriting sample/image")
    notes: Optional[str] = None

class Template(BaseModel):
    title: str
    description: Optional[str] = None
    preview_url: str = Field(..., description="Preview image URL (can be data URL or public URL)")
    theme: str = Field(..., description="Theme name e.g. lunar, zen, sunrise")

class Tier(BaseModel):
    name: str
    price_monthly: float
    perks: List[str] = []
    highlight: bool = False

class Product(BaseModel):
    title: str
    kind: str = Field(..., description="ebook | audio | guide | template-pack")
    description: Optional[str] = None
    download_url: Optional[str] = None
    free: bool = True

class JournalEntry(BaseModel):
    user_id: Optional[str] = None
    date: Optional[date] = None
    template_id: Optional[str] = None
    handwriting_id: Optional[str] = None
    content: Optional[str] = Field(None, description="Text content")
    strokes_data_url: Optional[str] = Field(None, description="Canvas drawing as data URL image")
    mood: Optional[str] = None
    intention: Optional[str] = None
