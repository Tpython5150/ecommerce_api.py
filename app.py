from flask import Flask, request, jsonify
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
db = SQLAlchemy(app, model_class=Base)
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
    price: Mapped[float] = mapped_column(Float)

    # Many-to-Many relationship with Order 
    orders: Mapped[List["Order"]] = relationship(secondary=order_product, back_populates="products")
    
    #===================== Schemas =======================
    
class UserSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = User
        load_instnace = True
            
class OrderSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Order
        load_instance = True
            
class ProductSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Product
        load_instance = True
        
user_schema = UserSchema()
users_schema = UserSchema(many=True)
order_schema = OrderSchema()
orders_schema = OrderSchema(many=True)
product_schema = ProductSchema()
products_schema = ProductSchema(many=True)

#====================== Routes =========================
# Create a user
@app.route('/users', methods=['POST'])
def create_user():
    try:
        user_data = user_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    new_user = User(name=user_data['name'], email=user_data['email'], phone_number=user_data['phone_number'])
    db.session.add(new_user)
    db.session.commit()
    
    return user_schema.jsonify(new_user), 201

# Read retrieve all users
@app.route('/users', methods=['GET'])
def get_users():
    query = select(User)
    users = db.session.execute(query).scalars().all()
    
    return users_schema.jsonify(users), 200

# Retrieve a user by ID
@app.route('/users/<int:id>', methods=['Get'])
def get_user(id):
    user = db.session.get(User, id)
    return user_schema.jsonify(user), 200

# Update a user
@app.route('/users/<int:id>', methods=['PUT'])
def update_user(id):
    user = db.session.get(User, id)
    
    if not user:
        return jsonify({"message": "Invalid user id"}), 400
    
    try:
        user_data = user_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400
    user.name = user_data['name']
    user.email = user_data['email']
    
    db.session.commit()
    return user_schema.jsonify(user), 200

# Delete a user
@app.route('/users/<int:id>', methods=['DELETE'])
def delete_user(id):
    user = db.session.get(User, id)
    
    if not user:
        return jsonify({"message": "Invalid user id"}), 400
    db.session.delete(user)
    db.session.commit()
    return jsonify({"message": f"successfully deleted user {id}"}), 200

# Create Product
@app.route('/products/<int:id', methods=['POST'])
def create_product():
    try:
        product_data= product_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    new_product = Product(name=product_data['name'], phone=product_data['phone'])
    db.session.add(new_product)
    db.session.commit()
    
# Retrieve all products
@app.route('/products', methods=['GET'])
def get_products():
    query = select(Product)
    users = db.session.execute(query).scalars().all()
    
    return users_schema.jsonify(users), 200
    
# Retrieve products by ID
@app.route('/products/<int:id>', methods=['Get'])
def get_product(id):
    product = db.session.get(Product, id)
    return user_schema.jsonify(product), 200   

# Update a product by ID    
@app.route('/products/<int:id>', methods=['PUT'])
def update_product(id):
    product = db.session.get(Product, id)
    
    if not product:
        return jsonify({"message": "Invalid user id"}), 400
    
    try:
        product_data = product_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400
    product.name = product_data['name']
    
    db.session.commit()
    return user_schema.jsonify(product), 200   

# Delete a product
@app.route('/products/<int:id>', methods=['DELETE'])
def delete_product(id):
    product = db.session.get(Product, id)
    
    if not product:
        return jsonify({"message": "Invalid user id"}), 400
    db.session.delete(product)
    db.session.commit()
    return jsonify({"message": f"successfully deleted user {id}"}), 200

# Create Order
@app.route('/orders', methods=['POST'])
def create_order():
    try:
        order_data= order_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    new_order = Order(order_date = order_data['order_date'], user_id = order_data['user_id'])
    db.session.add(new_order)
    db.session.commit()
    
# Add a product to an order
@app.route('/orders/<int:order_id>/add_product', methods=['POST'])
def add_product_to_order(order_id):
    try:
         product_data = request.json
         product_id = product_data['product_id']
    except KeyError:
        return jsonify({"message": "Invalid"})
    
    order = db.session.get(Order, order_id)
    product = db.session.get(Product, product_id)
    
    if not order or not product:
        return jsonify({"message": "Invalid order or product ID"})
    
    order.products.append(product)
    db.session.commit()
    return order_schema.jsonify(order)

# Delete a order
@app.route('/orders/<int:order_id>/remove_product', methods=['DELETE'])
def delete_order(order_id):
    order = db.session.get(Order, order_id)
    
    if not order:
        return jsonify({"message": "Invalid order id"}), 400
    db.session.delete(order)
    db.session.commit()
    return jsonify({"message": f"successfully deleted order {id}"}), 200

# Get all order
@app.route('/orders/<int:order_id>/products', methods=['GET'])
def get_products(order_id):
    order = db.session.get(Order, order_id)
    return jsonify(order.products), 200
    
    