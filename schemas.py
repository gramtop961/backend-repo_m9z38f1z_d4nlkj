"""
Database Schemas

Define your MongoDB collection schemas here using Pydantic models.
These schemas are used for data validation in your application.

Each Pydantic model represents a collection in your database.
Model name is converted to lowercase for the collection name:
- User -> "user" collection
- Product -> "product" collection
- BlogPost -> "blogs" collection
"""

from pydantic import BaseModel, Field
from typing import Optional, List

class User(BaseModel):
    """
    Users collection schema
    Collection name: "user" (lowercase of class name)
    """
    name: str = Field(..., description="Full name")
    email: str = Field(..., description="Email address")
    address: str = Field(..., description="Address")
    age: Optional[int] = Field(None, ge=0, le=120, description="Age in years")
    is_active: bool = Field(True, description="Whether user is active")

class Product(BaseModel):
    """
    Products collection schema
    Collection name: "product" (lowercase of class name)
    Prices are in INR (rupees). Store as float rupees for simplicity; UI must format with INR locale.
    """
    title: str = Field(..., description="Product title")
    description: Optional[str] = Field(None, description="Product description")
    price: float = Field(..., ge=0, description="Price in INR rupees")
    category: str = Field(..., description="Product category")
    image: Optional[str] = Field(None, description="Product image URL")
    rating: Optional[float] = Field(4.5, ge=0, le=5, description="Average rating")
    in_stock: bool = Field(True, description="Whether product is in stock")

class OrderItem(BaseModel):
    product_id: str
    title: str
    price: float = Field(..., ge=0, description="Unit price (INR)")
    quantity: int = Field(1, ge=1)
    image: Optional[str] = None

class Order(BaseModel):
    """Orders collection schema ("order")"""
    items: List[OrderItem]
    subtotal: float = Field(..., ge=0, description="Subtotal in INR")
    shipping: float = Field(0.0, ge=0, description="Shipping in INR")
    total: float = Field(..., ge=0, description="Total in INR")
    currency: str = Field("INR", description="Currency code")
    customer_name: Optional[str] = None
    customer_email: Optional[str] = None
    address: Optional[str] = None
