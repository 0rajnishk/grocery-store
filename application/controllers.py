from flask import g, render_template, request, redirect, url_for, session, flash
from application import app
from application.models import Product, User, Category
from application.database import db

app.secret_key = 'development key'


@app.before_request
def load_user():
    g.user = None
    if 'id' in session:
        g.user = User.query.get(session['id'])


def addadmin():
    if User.query.filter_by(role='admin').first():
        return
    user = User('abc@gmail.com', '123', 'admin1', 'chennai', 'admin')
    db.session.add(user)
    db.session.commit()


@app.route('/')
def index():
    caegories = Category.query.all()
    products = Product.query.all()
    if g.user:
        if g.user.role == 'admin':
            return redirect(url_for('adminDashboard'))
        else:
            return render_template('userDashboard.html', products=viewproduct())
    return render_template('index.html', products=products, categories=caegories)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        name = request.form['name']
        city = request.form['city']
        role = "user"
        user = User(email, password, name, city, role)
        db.session.add(user)
        db.session.commit()
        flash('You were successfully registered', 'success')
        return redirect(url_for('index'))
    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email, role='user').first()
        if user and user.password == password:
            session['id'] = user.id
            session['email'] = user.email
            session['name'] = user.name
            session['city'] = user.city
            session['role'] = user.role
            flash('You were successfully logged in', 'success')
            return redirect(url_for('userDashboard'))
        else:
            return render_template('login.html', error='Invalid username or password')
    else:
        return render_template('login.html')


@app.route('/adminlogin', methods=['GET', 'POST'])
def adminlogin():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email, role='admin').first()
        if user is not None and user.password == password:
            session['id'] = user.id
            session['email'] = user.email
            session['name'] = user.name
            session['city'] = user.city
            session['role'] = user.role
            return redirect(url_for('adminDashboard'))
        else:
            return render_template('adminlogin.html', error='Invalid username or password')

    return render_template('adminlogin.html')


@app.route('/adminDashboard', methods=['GET', 'POST'])
def adminDashboard():
    if g.user:
        if g.user.role == 'admin':
            return render_template('adminDashboard.html', categories=viewcategory())
        else:
            return redirect(url_for('userDashboard'))
    return redirect(url_for('adminlogin'))


@app.route('/addcategory', methods=['GET', 'POST'])
def addcategory():
    if g.user and session['role'] == 'admin':
        if request.method == 'POST':
            name = request.form['name']
            category = Category(name)
            db.session.add(category)
            db.session.commit()
            return redirect(url_for('adminDashboard'))
        return render_template('addcategory.html')
    return redirect(url_for('adminlogin'))


@app.route('/editcategory/<int:id>', methods=['GET', 'POST'])
def editcategory(id):
    if g.user and session['role'] == 'admin':
        category = Category.query.get(id)
        if request.method == 'POST':
            category.name = request.form['name']
            db.session.commit()
            return redirect(url_for('adminDashboard'))
        return render_template('editcategory.html', category=category)
    return redirect(url_for('adminlogin'))


@app.route('/deletecategory/<int:id>', methods=['GET', 'POST'])
def deletecategory(id):
    if g.user and session['role'] == 'admin':
        category = Category.query.get(id)
        db.session.delete(category)
        db.session.commit()
        return redirect(url_for('adminDashboard'))
    return redirect(url_for('adminlogin'))


@app.route('/viewcategory')
def viewcategory():
    return Category.query.all()


@app.route('/addproduct/<int:id>', methods=['GET', 'POST'])
def addproduct(id):
    if g.user and session['role'] == 'admin':
        category = Category.query.get(id)
        if request.method == 'POST':
            name = request.form['name']
            manufacture = request.form['mnf-date']
            expirydate = request.form['exp-date']
            rateperunit = request.form['price']
            quantity = request.form['quantity']
            category_id = id
            totalprice = int(rateperunit)*int(quantity)
            unit = request.form['unit']
            product = Product(name, manufacture, expirydate,
                              rateperunit, quantity, category_id, unit)
            product.totalprice = totalprice
            db.session.add(product)
            db.session.commit()
            return redirect(url_for('adminDashboard'))
        return render_template('addproduct.html', category=category)
    return redirect(url_for('adminlogin'))


@app.route('/editproduct/<int:id>', methods=['GET', 'POST'])
def editproduct(id):
    if g.user and session['role'] == 'admin':
        product = Product.query.get(id)
        if request.method == 'POST':
            product.name = request.form['name']
            product.price = request.form['price']
            product.category = request.form['category']
            db.session.commit()
            return redirect(url_for('adminDashboard'))
        return render_template('editproduct.html', product=product)
    return redirect(url_for('adminlogin'))


@app.route('/deleteproduct/<int:id>', methods=['GET', 'POST'])
def deleteproduct(id):
    if g.user and session['role'] == 'admin':
        product = Product.query.get(id)
        db.session.delete(product)
        db.session.commit()
        return redirect(url_for('adminDashboard'))
    return redirect(url_for('adminlogin'))


@app.route('/viewproduct/<int:id>')
def viewproduct(id):
    products = Product.query.filter_by(category_id=id).all()
    return render_template('viewproduct.html', products=products)


@app.route('/logout')
def logout():
    session.pop('id', None)
    session.pop('email', None)
    session.pop('name', None)
    session.pop('city', None)
    session.pop('role', None)
    return redirect(url_for('index'))
