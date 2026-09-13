"""
LangGraph nodes - each function is one step in the workflow
"""
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import Order, Customer, Negotiation
from app.services.inventory import check_inventory
from app.services.fraud import evaluate_risk
from app.services.alternative import find_alternative
from app.services.negotiation import (
    create_negotiation, send_offer_notification
)
from app.graph.state import OrderTriageState


def load_order_node(state: OrderTriageState) -> OrderTriageState:
    """Load order + customer from DB"""
    db: Session = SessionLocal()
    try:
        order = db.query(Order).filter(Order.id == state["order_id"]).first()
        if not order:
            state["error"] = f"Order {state['order_id']} not found"
            state["final_status"] = "error"
            return state

        customer = db.query(Customer).filter(Customer.id == order.customer_id).first()

        state["customer_id"] = order.customer_id
        state["customer_email"] = customer.email if customer else ""
        state["customer_risk_score"] = customer.risk_score if customer else 0
        state["order_risk_score"] = order.risk_score or 0
        state["order_total"] = float(order.total_amount)
        state["message"] = "Order loaded"
        return state
    finally:
        db.close()


def fraud_check_node(state: OrderTriageState) -> OrderTriageState:
    """Evaluate risk score -> flag if high risk"""
    is_high = evaluate_risk(
        state.get("order_risk_score", 0),
        state.get("customer_risk_score", 0),
    )
    state["is_high_risk"] = is_high
    if is_high:
        state["final_status"] = "flagged"
        state["message"] = "High risk order flagged for manual audit"
    else:
        state["message"] = "Risk check passed"
    return state


def inventory_check_node(state: OrderTriageState) -> OrderTriageState:
    """Check stock for all items"""
    db: Session = SessionLocal()
    try:
        items, out_of_stock = check_inventory(db, state["order_id"])
        state["items"] = items
        state["out_of_stock_items"] = out_of_stock
        state["all_in_stock"] = len(out_of_stock) == 0

        if state["all_in_stock"]:
            state["final_status"] = "processing"
            state["message"] = "All items in stock - proceeding to fulfillment"
        else:
            state["message"] = f"{len(out_of_stock)} item(s) out of stock"
        return state
    finally:
        db.close()


def create_offer_node(state: OrderTriageState) -> OrderTriageState:
    """
    For first out-of-stock item, find alternative and create negotiation.
    """
    db: Session = SessionLocal()
    try:
        if not state.get("out_of_stock_items"):
            state["final_status"] = "cancelled"
            state["message"] = "No out-of-stock items to negotiate"
            return state

        oos = state["out_of_stock_items"][0]
        alt = find_alternative(db, oos["product_id"])

        if not alt:
            state["final_status"] = "cancelled"
            state["message"] = f"No alternative found for {oos['product_name']}"
            return state

        neg = create_negotiation(
            db,
            order_id=state["order_id"],
            original_product_id=oos["product_id"],
            alternative_product_id=alt.id,
        )

        # Update order status
        order = db.query(Order).filter(Order.id == state["order_id"]).first()
        order.status = "awaiting_customer"
        db.commit()

        # Send notification
        send_offer_notification(state["customer_email"], neg, alt)

        state["negotiation_id"] = neg.id
        state["alternative_product_id"] = alt.id
        state["discount_percentage"] = float(neg.discount_percentage)
        state["negotiation_status"] = "pending"
        state["final_status"] = "awaiting_customer"
        state["message"] = f"Offer sent for {oos['product_name']} -> {alt.name}"
        return state
    finally:
        db.close()


def wait_for_customer_node(state: OrderTriageState) -> OrderTriageState:
    """
    Placeholder node - customer response comes via API.
    Graph ends here in 'awaiting_customer' state.
    """
    state["message"] = "Waiting for customer response (handled via API)"
    return state