"""
Inventory validation service
"""
from sqlalchemy.orm import Session
from app.models import Order, OrderItem, Product


def check_inventory(db: Session, order_id: int):
    """
    Returns (items_info, out_of_stock_items)
    items_info: list of dicts for each order item with stock info
    """
    order_items = db.query(OrderItem).filter(OrderItem.order_id == order_id).all()

    items_info = []
    out_of_stock = []

    for oi in order_items:
        product = db.query(Product).filter(Product.id == oi.product_id).first()
        stock = product.stock if product else 0

        info = {
            "order_item_id": oi.id,
            "product_id": oi.product_id,
            "product_name": product.name if product else "Unknown",
            "category": product.category if product else None,
            "quantity": oi.quantity,
            "price": float(oi.price),
            "stock": stock,
            "in_stock": stock >= oi.quantity,
        }
        items_info.append(info)

        if not info["in_stock"]:
            out_of_stock.append(info)

    return items_info, out_of_stock