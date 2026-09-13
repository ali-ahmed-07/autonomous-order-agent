"""
Find best alternative product (same category, in-stock, cheaper or equal)
"""
from sqlalchemy.orm import Session
from app.models import Product


def find_alternative(db: Session, product_id: int):
    """
    Returns best alternative Product or None.
    Strategy:
      1. Same category
      2. In stock
      3. Price <= original price (customer-friendly)
      4. Order by closest price to original (descending)
    """
    original = db.query(Product).filter(Product.id == product_id).first()
    if not original:
        return None

    candidates = (
        db.query(Product)
        .filter(
            Product.id != original.id,
            Product.category == original.category,
            Product.stock > 0,
            Product.price <= original.price,
        )
        .order_by(Product.price.desc())
        .all()
    )

    if candidates:
        return candidates[0]

    # Fallback: any in-stock product in same category
    fallback = (
        db.query(Product)
        .filter(
            Product.id != original.id,
            Product.category == original.category,
            Product.stock > 0,
        )
        .order_by(Product.price.asc())
        .first()
    )
    return fallback