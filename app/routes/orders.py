"""
Order routes - intake, triage, response
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Order, OrderItem, Product, Customer, Negotiation
from app.schemas import (
    OrderCreate, OrderOut, TriageResult,
    CustomerResponseInput, NegotiationOut,
)
from app.graph.workflow import triage_graph

router = APIRouter(prefix="/orders", tags=["Orders"])


@router.post("/", response_model=OrderOut, status_code=201)
def create_order(payload: OrderCreate, db: Session = Depends(get_db)):
    """Create a new order and its items"""
    customer = db.query(Customer).filter(Customer.id == payload.customer_id).first()
    if not customer:
        raise HTTPException(404, "Customer not found")

    order = Order(
        customer_id=payload.customer_id,
        status="new",
        risk_score=customer.risk_score or 0,
        total_amount=0,
    )
    db.add(order)
    db.flush()  # get order.id

    total = 0.0
    for item in payload.items:
        product = db.query(Product).filter(Product.id == item.product_id).first()
        if not product:
            raise HTTPException(404, f"Product {item.product_id} not found")

        line_price = float(product.price) * item.quantity
        total += line_price

        db.add(OrderItem(
            order_id=order.id,
            product_id=product.id,
            quantity=item.quantity,
            price=product.price,
        ))

    order.total_amount = total
    db.commit()
    db.refresh(order)
    return order


@router.get("/{order_id}", response_model=OrderOut)
def get_order(order_id: int, db: Session = Depends(get_db)):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(404, "Order not found")
    return order


@router.post("/{order_id}/triage", response_model=TriageResult)
def triage_order(order_id: int, db: Session = Depends(get_db)):
    """
    Run the LangGraph triage workflow on an order.
    """
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(404, "Order not found")

    initial_state = {"order_id": order_id}
    final_state = triage_graph.invoke(initial_state)

    negotiation_out = None
    neg_id = final_state.get("negotiation_id")
    if neg_id:
        neg = db.query(Negotiation).filter(Negotiation.id == neg_id).first()
        if neg:
            negotiation_out = NegotiationOut.model_validate(neg)

    return TriageResult(
        order_id=order_id,
        status=final_state.get("final_status", "unknown"),
        message=final_state.get("message", ""),
        negotiation=negotiation_out,
    )


@router.post("/negotiations/{negotiation_id}/respond", response_model=NegotiationOut)
def respond_to_negotiation(
    negotiation_id: int,
    payload: CustomerResponseInput,
    db: Session = Depends(get_db),
):
    """
    Customer accepts or rejects the alternative product offer.
    """
    from app.services.negotiation import handle_customer_response

    try:
        neg = handle_customer_response(db, negotiation_id, payload.response)
    except ValueError as e:
        raise HTTPException(400, str(e))

    return neg


@router.get("/negotiations/{negotiation_id}", response_model=NegotiationOut)
def get_negotiation(negotiation_id: int, db: Session = Depends(get_db)):
    neg = db.query(Negotiation).filter(Negotiation.id == negotiation_id).first()
    if not neg:
        raise HTTPException(404, "Negotiation not found")
    return neg