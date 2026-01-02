import re
from email_validator import validate_email as validate_email_lib, EmailNotValidError


def validate_email(email: str) -> bool:
    """Validate email format"""
    try:
        validate_email_lib(email)
        return True
    except EmailNotValidError:
        return False


def validate_price(price_str: str) -> bool:
    """Validate price format"""
    try:
        price = float(price_str.replace(',', '.'))
        return price > 0
    except ValueError:
        return False


def validate_quantity(quantity_str: str) -> bool:
    """Validate quantity format"""
    try:
        quantity = int(quantity_str)
        return quantity >= 0
    except ValueError:
        return False


def generate_sku(product_name: str) -> str:
    """Generate SKU from product name"""
    # Simple SKU generation - in production use more robust method
    import hashlib
    sku_hash = hashlib.md5(product_name.encode()).hexdigest()[:8].upper()
    return f"SKU-{sku_hash}"
