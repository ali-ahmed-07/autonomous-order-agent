"""
LangGraph State definition - the shared memory across nodes
"""
from typing import TypedDict, Optional, List, Dict, Any


class OrderTriageState(TypedDict, total=False):
    # Input
    order_id: int

    # Loaded data
    customer_id: int
    customer_email: str
    customer_risk_score: int
    order_risk_score: int
    order_total: float

    # Items & inventory
    items: List[Dict[str, Any]]          # [{order_item_id, product_id, quantity, price, stock}]
    out_of_stock_items: List[Dict[str, Any]]

    # Decision flags
    is_high_risk: bool
    all_in_stock: bool

    # Negotiation
    negotiation_id: Optional[int]
    alternative_product_id: Optional[int]
    discount_percentage: float
    negotiation_status: Optional[str]

    # Final
    final_status: str
    message: str
    error: Optional[str]