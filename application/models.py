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
    products = db.relationship('Product', backref='category', lazy='dynamic')


    def __init__(self, name):
        self.name = name

class Product(db.Model):
    id=db.Column(db.Integer, primary_key=True)
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








