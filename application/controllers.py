import base64
from flask import g, render_template, request, redirect, url_for, session, flash
from application import app
from application.models import Cart, Product, User, Category
from application.database import db

app.secret_key = 'development key'

def convert_to_base64(image_data):
    return base64.b64encode(image_data).decode('utf-8')

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
    for product in products:
        product.image = base64.b64encode(product.image).decode('utf-8')
    if g.user:
        if g.user.role == 'admin':
            return redirect(url_for('adminDashboard'))
        else:
            products = Product.query.all()
            
            return render_template('index.html', products=products, user=session['name'], categories=caegories)  
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
            return redirect(url_for('index'))
        else:
            return render_template('index.html', error='Invalid username or password')
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
            return redirect(url_for('logout'))
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
        products = Product.query.filter_by(category_id=id).all()
        for product in products:
            db.session.delete(product)
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
            image = request.files['image'].read()
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
            product.image = image
            category.quantity = int(category.quantity)+1
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
            product.manufacture = request.form['mnf-date']
            product.expirydate = request.form['exp-date']
            product.rateperunit = request.form['price']
            product.quantity = request.form['quantity']
            product.totalprice = int(product.rateperunit)*int(product.quantity)
            product.unit = request.form['unit']
            db.session.commit()
            return redirect('/viewproduct/{}'.format(product.category_id))
        return render_template('editproduct.html', product=product)
    return redirect(url_for('adminlogin'))


@app.route('/deleteproduct/<int:id>', methods=['GET', 'POST'])
def deleteproduct(id):
    if g.user and session['role'] == 'admin':
        product = Product.query.get(id)
        db.session.delete(product)
        category = Category.query.get(product.category_id)
        category.quantity = int(category.quantity)-1
        db.session.commit()
        return redirect('/viewproduct/{}'.format(product.category_id))
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


# cart

@app.route('/addtocart/<int:id>', methods=['GET', 'POST'])
def addtocart(id):
    if g.user:
        product = Product.query.get(id)
        if request.method == 'POST':
            quantity = request.form['quantity']
            if int(quantity) > int(product.quantity):
                return render_template('addtocart.html', product=product, error='Quantity is not available')
            else:
                if Cart.query.filter_by(product_id=id, user_id=session['id']).first():
                    cart = Cart.query.filter_by(
                        product_id=id, user_id=session['id']).first()
                    cart.quantity = int(cart.quantity)+int(quantity)
                    cart.totalprice = int(cart.quantity)*int(product.rateperunit)
                    db.session.commit()
                    return redirect(url_for('index'))
                cart = Cart(product_id=id, user_id=session['id'], quantity=quantity)
                cart.totalprice = int(quantity)*int(product.rateperunit)
                db.session.add(cart)
                db.session.commit()
                return redirect(url_for('index'))
        return render_template('addtocart.html', product=product)
    return redirect(url_for('login'))

@app.route('/viewcart')
def viewcart():
    if g.user:
        carts = Cart.query.filter_by(user_id=session['id']).all()
        products = []
        for cart in carts: 
            product = Product.query.get(cart.product_id)
            products.append(product)
        return render_template('viewcart.html', carts=carts, products=products)
    return redirect(url_for('login'))

@app.route('/removefromcart/<int:id>')
def deletecart(id):
    cart = Cart.query.get(id)
    db.session.delete(cart)
    db.session.commit()
    return redirect(url_for('viewcart'))


@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    if g.user:
        carts = Cart.query.filter_by(user_id=session['id']).all()
        for cart in carts:
            product = Product.query.get(cart.product_id)
            product.quantity = int(product.quantity)-int(cart.quantity)
            db.session.delete(cart)
            db.session.commit()
        flash('Order Placed Successfully', 'success')
        return redirect(url_for('index'))
    return redirect(url_for('login'))

#Search

@app.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        name = request.form['search']
        products = Product.query.filter(Product.name.like('%'+name+'%')).all()
        return render_template('search.html', products=products)
    return redirect(url_for('index'))
# getproduct by id

@app.route('/getproduct/<int:id>')
def getproduct(id):
    product = Product.query.get(id)
    return render_template('product.html', product=product)
