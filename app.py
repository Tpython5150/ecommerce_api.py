from flask import Flask, reuest, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from marshmallow import ValidationError
from sqlalchemy.orm import DeclarativeBase, mapped_column, Mapped, relationship, Session
from sqlalchemy import ForeignKey, Table, String, Column, select, DateTime, Float
from typing import List
from datetime import datetime
import os


# Intiailize Flask app
app = Flask(__name__)

# MySQL database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:Nissan5150@localhost/ecommerce_api'

# #Creating our base model
class Base(DeclarativeBase):
    pass
db = SQLAlchemy(model_class=Base)
db.init_app(app)
ma = Marshmallow(app)


#=============== User Table ==================

order_product = Table(
    "order_product",
    Base.metadata,
    Column("order_id", ForeignKey("order.id")),
    Column("product_id", ForeignKey("product.id"))
)


class User(Base):
    __tablename__ = "users"
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(50))
    address: Mapped[str] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(200), unique=True)
    
    # One-to-Many relationship with Order 
    orders: Mapped[List['Order']] = relationship("Order", back_populates="user")
    
class Order(Base):
    __tablename__ = "orders"
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    order_date: Mapped[datetime] = mapped_column(DateTime.now(datetime.timezone.utc))
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))

    
    # Many-to-One relationship with User 
    user: Mapped['User'] = relationship("User", back_populates="orders")
    
    # Many-to-Many relationship with Product 
    products: Mapped[List['Product']] = relationship(secondary=order_product, back_populates="orders")
    
    
class Product(Base):
    __tablename__ = "products"    
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    product_name: Mapped[str] = mapped_column(String(50))
    price: Mapped[float] = mapped_column(Float(1))

    # Many-to-Many relationship with Order 
    orders: Mapped[List["Order"]] = relationship(secondary=order_product, back_populates="products")
    
    #===================== Schemas =======================
    
class UserSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = User
            
class OrderSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Order
            
class ProductSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Product
       