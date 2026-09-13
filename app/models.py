"""
SQLAlchemy models mapped to existing phpMyAdmin tables:
customers, orders, order_items, products, negotiations
"""
from sqlalchemy import (
    Column, Integer, String, Numeric, DateTime, ForeignKey, func
)
from sqlalchemy.orm import relationship
from app.database import Base


class Customer(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    email = Column(String(150), nullable=False)
    risk_score = Column(Integer, default=0)
    created_at = Column(DateTime, server_default=func.now())

    orders = relationship("Order", back_populates="customer")


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(150), nullable=False)
    price = Column(Numeric(10, 2), nullable=False)
    stock = Column(Integer, default=0)
    category = Column(String(100), nullable=True)
    created_at = Column(DateTime, server_default=func.now())


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    status = Column(String(50), default="new")
    # statuses: new, flagged, processing, awaiting_customer, resolved, cancelled, refunded
    risk_score = Column(Integer, default=0)
    total_amount = Column(Numeric(10, 2), default=0.00)
    created_at = Column(DateTime, server_default=func.now())

    customer = relationship("Customer", back_populates="orders")
    items = relationship("OrderItem", back_populates="order")
    negotiations = relationship("Negotiation", back_populates="order")


class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    quantity = Column(Integer, default=1)
    price = Column(Numeric(10, 2), nullable=False)

    order = relationship("Order", back_populates="items")
    product = relationship("Product")


class Negotiation(Base):
    __tablename__ = "negotiations"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    original_product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    alternative_product_id = Column(Integer, ForeignKey("products.id"), nullable=True)
    discount_percentage = Column(Numeric(5, 2), default=0.00)
    status = Column(String(50), default="pending")
    # statuses: pending, accepted, rejected, expired
    customer_response = Column(String(50), nullable=True)
    created_at = Column(DateTime, server_default=func.now())

    order = relationship("Order", back_populates="negotiations")
    original_product = relationship("Product", foreign_keys=[original_product_id])
    alternative_product = relationship("Product", foreign_keys=[alternative_product_id])