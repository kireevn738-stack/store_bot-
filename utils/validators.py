import re
from datetime import datetime
from email_validator import validate_email, EmailNotValidError

def is_valid_email(email: str) -> bool:
    try:
        validate_email(email)
        return True
    except EmailNotValidError:
        return False

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
