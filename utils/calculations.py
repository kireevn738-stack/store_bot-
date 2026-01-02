from datetime import datetime, timedelta
from typing import List, Tuple
from database import Product, Transaction, TransactionType


def calculate_profit(products: List[Product]) -> float:
    """Calculate total potential profit from products"""
    return sum((p.sale_price - p.purchase_price) * p.quantity for p in products)


def calculate_turnover(transactions: List[Transaction]) -> Tuple[float, float]:
    """Calculate total purchases and sales"""
    purchases = sum(t.total_amount for t in transactions if t.transaction_type == TransactionType.PURCHASE)
    sales = sum(t.total_amount for t in transactions if t.transaction_type == TransactionType.SALE)
    return purchases, sales


def calculate_inventory_value(products: List[Product]) -> float:
    """Calculate total inventory value at purchase price"""
    return sum(p.purchase_price * p.quantity for p in products)


def get_date_range(period: str) -> Tuple[datetime, datetime]:
    """Get start and end dates for different periods"""
    now = datetime.utcnow()
    
    if period == "day":
        start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        return start, now
    elif period == "week":
        start = now - timedelta(days=now.weekday())
        start = start.replace(hour=0, minute=0, second=0, microsecond=0)
        return start, now
    elif period == "month":
        start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        return start, now
    elif period == "year":
        start = now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
        return start, now
    else:  # all time
        return datetime(2000, 1, 1), now
