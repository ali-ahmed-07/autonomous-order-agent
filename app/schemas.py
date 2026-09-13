"""
Pydantic schemas for request/response validation
"""
from datetime import datetime
from decimal import Decimal
from typing import Optional, List
from pydantic import BaseModel, EmailStr, ConfigDict


# ---------- Customer ----------
class CustomerBase(BaseModel):
    name: str
    email: EmailStr
    risk_score: int = 0


class CustomerCreate(CustomerBase):
    pass


class CustomerOut(CustomerBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    created_at: datetime


# ---------- Product ----------
class ProductBase(BaseModel):
    name: str
    price: Decimal
    stock: int = 0
    category: Optional[str] = None


class ProductOut(ProductBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    created_at: datetime


# ---------- Order Item ----------
class OrderItemCreate(BaseModel):
    product_id: int
    quantity: int = 1


class OrderItemOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    product_id: int
    quantity: int
    price: Decimal


# ---------- Order ----------
class OrderCreate(BaseModel):
    customer_id: int
    items: List[OrderItemCreate]


class OrderOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    customer_id: int
    status: str
    risk_score: int
    total_amount: Decimal
    created_at: datetime
    items: List[OrderItemOut] = []


# ---------- Negotiation ----------
class NegotiationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    order_id: int
    original_product_id: int
    alternative_product_id: Optional[int]
    discount_percentage: Decimal
    status: str
    customer_response: Optional[str]
    created_at: datetime


class CustomerResponseInput(BaseModel):
    """Customer accepts/rejects an offer"""
    response: str  # "accepted" or "rejected"


# ---------- Agent Workflow Response ----------
class TriageResult(BaseModel):
    order_id: int
    status: str
    message: str
    negotiation: Optional[NegotiationOut] = None