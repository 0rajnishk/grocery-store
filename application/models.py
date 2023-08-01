import datetime
from application.database import db

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(128), unique=True)
    password = db.Column(db.String(128))
    name = db.Column(db.String(128))
    city = db.Column(db.String(128))
    role = db.Column(db.String(128),default='user')

    def __init__(self, email, password, name, city, role):
        self.email = email
        self.password = password
        self.name = name
        self.city = city
        self.role = role
        

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), unique=True)
    quantity = db.Column(db.Integer,default=0)
    products = db.relationship('Product', backref='category', lazy='dynamic')


    def __init__(self, name):
        self.name = name

class Product(db.Model):
    id=db.Column(db.Integer, primary_key=True)
    image = db.Column(db.BLOB)
    name=db.Column(db.String(128), unique=True)
    manufacture=db.Column(db.String(128))
    expirydate=db.Column(db.String(128))
    rateperunit=db.Column(db.Integer)
    quantity=db.Column(db.Integer)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'))
    totalprice=db.Column(db.Integer,default=0)
    unit=db.Column(db.Integer,default=0)


    def __init__(self, name, manufacture, expirydate, rateperunit, quantity, category_id,unit):
        self.name = name
        self.manufacture = manufacture
        self.expirydate = expirydate
        self.rateperunit = rateperunit
        self.quantity = quantity
        self.category_id = category_id
        self.unit=unit


class Cart(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    product_id=db.Column(db.Integer, db.ForeignKey('product.id'))
    quantity=db.Column(db.Integer)
    totalprice=db.Column(db.Integer)

    def __init__(self, user_id, product_id, quantity):
        self.user_id = user_id
        self.product_id = product_id
        self.quantity = quantity

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    cart_id = db.Column(db.Integer, db.ForeignKey('cart.id'))
    date = db.Column(db.Date)

    def __init__(self, user_id, cart_id):
        self.user_id = user_id
        self.cart_id = cart_id