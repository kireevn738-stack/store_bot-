import re
from datetime import datetime

def is_valid_email(email: str) -> bool:
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def is_valid_price(price: str) -> bool:
    try:
        price_float = float(price)
        return price_float >= 0
    except ValueError:
        return False

def is_valid_quantity(quantity: str) -> bool:
    try:
        qty_int = int(quantity)
        return qty_int >= 0
    except ValueError:
        return False

def parse_date(date_str: str) -> datetime:
    formats = ['%Y-%m-%d', '%d.%m.%Y', '%d/%m/%Y']
    
    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue
    
    raise ValueError("Invalid date format")
