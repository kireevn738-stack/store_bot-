from typing import Optional, List
from pydantic import BaseModel, EmailStr, validator, field_validator
from datetime import datetime

class UserCreate(BaseModel):
    telegram_id: int
    email: EmailStr
    language: str = "ru"

class UserUpdate(BaseModel):
    language: Optional[str] = None
    store_name: Optional[str] = None
    
class CategoryCreate(BaseModel):
    name: str
    
class CategoryUpdate(BaseModel):
    name: str

class ProductCreate(BaseModel):
    name: str
    quantity: int
    purchase_price: float
    sale_price: float
    category_id: Optional[int] = None
    
    @field_validator('sale_price')
    @classmethod
    def validate_sale_price(cls, v, info):
        purchase_price = info.data.get('purchase_price')
        if purchase_price is not None and v < purchase_price:
            raise ValueError('Sale price must be greater than or equal to purchase price')
        return v
    
    @field_validator('quantity')
    @classmethod
    def validate_quantity(cls, v):
        if v < 0:
            raise ValueError('Quantity must be non-negative')
        return v
    
    @property
    def profit(self) -> float:
        return self.sale_price - self.purchase_price

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    quantity: Optional[int] = None
    purchase_price: Optional[float] = None
    sale_price: Optional[float] = None
    category_id: Optional[int] = None
    
    @field_validator('quantity')
    @classmethod
    def validate_quantity(cls, v):
        if v is not None and v < 0:
            raise ValueError('Quantity must be non-negative')
        return v
    
    @field_validator('sale_price')
    @classmethod
    def validate_sale_price(cls, v, info):
        if v is not None:
            purchase_price = info.data.get('purchase_price')
            if purchase_price is not None and v < purchase_price:
                raise ValueError('Sale price must be greater than or equal to purchase price')
        return v

class OrderItemCreate(BaseModel):
    product_id: int
    quantity: int
    
    @field_validator('quantity')
    @classmethod
    def validate_quantity(cls, v):
        if v <= 0:
            raise ValueError('Quantity must be positive')
        return v

class OrderCreate(BaseModel):
    items: List[OrderItemCreate]
    
    @field_validator('items')
    @classmethod
    def validate_items(cls, v):
        if not v:
            raise ValueError('Order must contain at least one item')
        return v

class AnalyticsRequest(BaseModel):
    period: str
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    
    @field_validator('period')
    @classmethod
    def validate_period(cls, v):
        valid_periods = ['day', 'week', 'month', 'year', 'all', 'custom']
        if v not in valid_periods:
            raise ValueError(f'Period must be one of: {", ".join(valid_periods)}')
        return v
