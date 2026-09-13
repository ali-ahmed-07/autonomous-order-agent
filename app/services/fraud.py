"""
Fraud / Risk assessment service
"""
import os

HIGH_RISK_THRESHOLD = int(os.getenv("HIGH_RISK_THRESHOLD", "70"))


def evaluate_risk(order_risk_score: int, customer_risk_score: int) -> bool:
    """
    Returns True if order should be flagged for manual audit.
    Uses max of order and customer risk scores.
    """
    effective_risk = max(order_risk_score or 0, customer_risk_score or 0)
    return effective_risk >= HIGH_RISK_THRESHOLD