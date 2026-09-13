"""
LangGraph StateGraph with conditional edges
Compatible with langgraph >= 1.0 (Python 3.14)
"""
from langgraph.graph import StateGraph, START, END
from app.graph.state import OrderTriageState
from app.graph.nodes import (
    load_order_node,
    fraud_check_node,
    inventory_check_node,
    create_offer_node,
    wait_for_customer_node,
)


def route_after_fraud(state: OrderTriageState) -> str:
    if state.get("error"):
        return "end"
    if state.get("is_high_risk"):
        return "end"
    return "inventory"


def route_after_inventory(state: OrderTriageState) -> str:
    if state.get("error"):
        return "end"
    if state.get("all_in_stock"):
        return "end"
    return "create_offer"


def route_after_offer(state: OrderTriageState) -> str:
    if state.get("negotiation_id"):
        return "wait_customer"
    return "end"


def build_graph():
    graph = StateGraph(OrderTriageState)

    graph.add_node("load_order", load_order_node)
    graph.add_node("fraud_check", fraud_check_node)
    graph.add_node("inventory", inventory_check_node)
    graph.add_node("create_offer", create_offer_node)
    graph.add_node("wait_customer", wait_for_customer_node)

    # Entry point (naya API — START constant use karein)
    graph.add_edge(START, "load_order")
    graph.add_edge("load_order", "fraud_check")

    graph.add_conditional_edges(
        "fraud_check",
        route_after_fraud,
        {"inventory": "inventory", "end": END},
    )

    graph.add_conditional_edges(
        "inventory",
        route_after_inventory,
        {"create_offer": "create_offer", "end": END},
    )

    graph.add_conditional_edges(
        "create_offer",
        route_after_offer,
        {"wait_customer": "wait_customer", "end": END},
    )

    graph.add_edge("wait_customer", END)

    return graph.compile()


# Compiled graph singleton
triage_graph = build_graph()