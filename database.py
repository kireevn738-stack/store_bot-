from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, ForeignKey, Boolean, Text, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import enum

Base = declarative_base()
engine = create_engine("sqlite:///store_bot.db")
SessionLocal = sessionmaker(bind=engine)


class UserLanguage(str, enum.Enum):
    ENGLISH = "en"
    RUSSIAN = "ru"
    UKRAINIAN = "uk"


class User(Base):
    tablename = "users"
    
    id = Column(Integer, primary_key=True)
    telegram_id = Column(Integer, unique=True, nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    language = Column(Enum(UserLanguage), default=UserLanguage.ENGLISH)
    store_name = Column(String(255))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    categories = relationship("Category", back_populates="user")
    products = relationship("Product", back_populates="user")
    transactions = relationship("Transaction", back_populates="user")


class Category(Base):
    tablename = "categories"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="categories")
    products = relationship("Product", back_populates="category")


class Product(Base):
    tablename = "products"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
    name = Column(String(255), nullable=False)
    purchase_price = Column(Float, nullable=False)
    sale_price = Column(Float, nullable=False)
    quantity = Column(Integer, default=0)
    sku = Column(String(100), unique=True)
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    user = relationship("User", back_populates="products")
    category = relationship("Category", back_populates="products")
    transactions = relationship("Transaction", back_populates="product")
    
    @property
    def profit_per_unit(self):
        return self.sale_price - self.purchase_price
    
    @property
    def total_profit(self):
        return self.profit_per_unit * self.quantity


class TransactionType(str, enum.Enum):
    PURCHASE = "purchase"  # Buying for stock
    SALE = "sale"          # Selling to customer
    ADJUSTMENT = "adjustment"


class Transaction(Base):
    tablename = "transactions"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    transaction_type = Column(Enum(TransactionType), nullable=False)
    quantity = Column(Integer, nullable=False)
    price = Column(Float, nullable=False)
    total_amount = Column(Float, nullable=False)
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="transactions")
    product = relationship("Product", back_populates="transactions")


def init_db():
    Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
