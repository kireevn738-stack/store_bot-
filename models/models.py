from typing import Optional, List
from pydantic import BaseModel, EmailStr, validator
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
    
    @validator('profit', always=True)
    def calculate_profit(cls, v, values):
        if 'sale_price' in values and 'purchase_price' in values:
            return values['sale_price'] - values['purchase_price']
        return 0

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    quantity: Optional[int] = None
    purchase_price: Optional[float] = None
    sale_price: Optional[float] = None
    category_id: Optional[int] = None
    profit: Optional[float] = None

class OrderItemCreate(BaseModel):
    product_id: int
    quantity: int

class OrderCreate(BaseModel):
    items: List[OrderItemCreate]

class AnalyticsRequest(BaseModel):
    period: str  # day, week, month, year, all, custom
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
