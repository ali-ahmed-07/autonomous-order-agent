"""
Negotiation service - create offers, send notifications, handle responses
"""
import os
from decimal import Decimal
from sqlalchemy.orm import Session
from app.models import Negotiation, Order, OrderItem, Product

DEFAULT_DISCOUNT = float(os.getenv("DEFAULT_DISCOUNT_PERCENTAGE", "10.0"))


def create_negotiation(
    db: Session,
    order_id: int,
    original_product_id: int,
    alternative_product_id: int,
    discount_percentage: float = DEFAULT_DISCOUNT,
) -> Negotiation:
    """Create a pending negotiation record"""
    neg = Negotiation(
        order_id=order_id,
        original_product_id=original_product_id,
        alternative_product_id=alternative_product_id,
        discount_percentage=Decimal(str(discount_percentage)),
        status="pending",
    )
    db.add(neg)
    db.commit()
    db.refresh(neg)
    return neg


def send_offer_notification(customer_email: str, negotiation: Negotiation, alt_product: Product):
    """
    Placeholder for email/SMS sending.
    In production: integrate SendGrid / Twilio / SMTP.
    """
    print(
        f"[NOTIFICATION] To: {customer_email}\n"
        f"  Offer: {alt_product.name} at "
        f"{float(alt_product.price) * (1 - float(negotiation.discount_percentage)/100):.2f} "
        f"({negotiation.discount_percentage}% off)\n"
        f"  Negotiation ID: {negotiation.id}\n"
    )
    # TODO: actually send via SMTP / Twilio


def handle_customer_response(db: Session, negotiation_id: int, response: str) -> Negotiation:
    """
    response: 'accepted' or 'rejected'
    Updates negotiation + order accordingly.
    """
    neg = db.query(Negotiation).filter(Negotiation.id == negotiation_id).first()
    if not neg:
        raise ValueError(f"Negotiation {negotiation_id} not found")

    response = response.lower()
    if response not in ("accepted", "rejected"):
        raise ValueError("response must be 'accepted' or 'rejected'")

    neg.customer_response = response
    order = db.query(Order).filter(Order.id == neg.order_id).first()

    if response == "accepted":
        neg.status = "accepted"
        # Swap product in order_items
        order_item = (
            db.query(OrderItem)
            .filter(
                OrderItem.order_id == neg.order_id,
                OrderItem.product_id == neg.original_product_id,
            )
            .first()
        )
        alt_product = (
            db.query(Product)
            .filter(Product.id == neg.alternative_product_id)
            .first()
        )

        if order_item and alt_product:
            # Apply discount
            discounted_price = float(alt_product.price) * (
                1 - float(neg.discount_percentage) / 100
            )
            order_item.product_id = alt_product.id
            order_item.price = Decimal(str(round(discounted_price, 2)))

            # Reduce stock
            alt_product.stock -= order_item.quantity

            # Recalculate order total
            items = db.query(OrderItem).filter(OrderItem.order_id == order.id).all()
            order.total_amount = sum(float(i.price) * i.quantity for i in items)

        order.status = "resolved"
    else:
        neg.status = "rejected"
        order.status = "refunded"

    db.commit()
    db.refresh(neg)
    return neg