from flask import Flask, render_template, request, redirect, session, jsonify, flash, url_for
import os
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from flask_sqlalchemy import SQLAlchemy

# Initialize the Flask application
app = Flask(__name__)

# Secret key for session management (should be kept secret in production)
app.secret_key = 'your_secret_key'

# Configuration for file uploads
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}

# Database path (Stored locally on PC)
db_path = os.path.join(os.getcwd(), "product_management.db")

# Configure SQLite database connection
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{db_path}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize the SQLAlchemy database instance
db = SQLAlchemy(app)

# Define the User model for the database
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(20), nullable=False)

# Define the Product model for the database
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    description = db.Column(db.Text, nullable=False)
    image_path = db.Column(db.String(255), nullable=True)

# Create database tables if they don't exist
with app.app_context():
    db.create_all()

# Function to check if a file has an allowed extension
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

# User login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            session['logged_in'] = True
            session['role'] = user.role
            return redirect(url_for('admin') if user.role == 'admin' else url_for('public_page'))
        else:
            flash('Invalid username or password', 'error')

    return render_template('login.html')

# Decorator to restrict access to admin routes
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session or session.get('role') != 'admin':
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Create admin user route
@app.route('/create_admin', methods=['GET', 'POST'])
# @admin_required
def create_admin():
    if request.method == 'POST':
        username = request.form['new_admin_username']
        password = generate_password_hash(request.form['new_admin_password'])
        new_admin = User(username=username, password=password, role='admin')
        db.session.add(new_admin)
        db.session.commit()
        flash('New admin created successfully!', 'success')
    
    return render_template('create_admin.html')

# Create user route
@app.route('/create_user', methods=['GET', 'POST'])
def create_user():
    if request.method == 'POST':
        username = request.form['new_username']
        password = generate_password_hash(request.form['new_password'])
        new_user = User(username=username, password=password, role='user')
        db.session.add(new_user)
        db.session.commit()
        flash('New user created successfully!', 'success')
    
    return render_template('create_user.html')

# Add product route
@app.route('/add_product', methods=['GET', 'POST'])
@admin_required
def add_product():
    if request.method == 'POST':
        name = request.form['name']
        price = float(request.form['price'])
        description = request.form['description']
        
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)

            new_product = Product(name=name, price=price, description=description, image_path="uploads/" + filename)
            db.session.add(new_product)
            db.session.commit()
            flash('Product added successfully!', 'success')

            return redirect(url_for('admin'))

    return render_template('add_product.html')

# Public homepage displaying all products
@app.route('/')
def public_page():
    products = Product.query.all()
    return render_template('index.html', products=products)

# Admin dashboard
@app.route('/admin')
@admin_required
def admin():
    products = Product.query.all()
    return render_template('admin.html', products=products)

# View product details
@app.route('/product/<int:product_id>')
def product_details(product_id):
    product = Product.query.get(product_id)
    if product:
        return jsonify({
            'id': product.id,
            'name': product.name,
            'price': product.price,
            'description': product.description,
            'image_path': product.image_path
        })
    return jsonify({'error': 'Product not found'}), 404

# Delete product route
@app.route('/delete_product/<int:product_id>', methods=['POST'])
@admin_required
def delete_product(product_id):
    product = Product.query.get(product_id)
    if product:
        if product.image_path and os.path.exists("static/" + product.image_path):
            os.remove("static/" + product.image_path)
        db.session.delete(product)
        db.session.commit()
        flash('Product deleted successfully!', 'success')

    return redirect(url_for('admin'))

# Add product to cart
@app.route('/add_to_cart/<int:product_id>', methods=['POST'])
def add_to_cart(product_id):
    product = Product.query.get(product_id)
    if not product:
        return jsonify({'message': 'Product not found'}), 404

    if 'cart' not in session:
        session['cart'] = {}

    cart = session['cart']
    if str(product_id) in cart:
        cart[str(product_id)]['quantity'] += 1
    else:
        cart[str(product_id)] = {'name': product.name, 'price': product.price, 'quantity': 1}

    session.modified = True
    return jsonify({'message': 'Product added to cart', 'cart': cart})

# View cart
@app.route('/cart')
def cart():
    return render_template('cart.html', cart=session.get('cart', {}))

# Remove product from cart
@app.route('/remove_from_cart/<int:product_id>', methods=['POST'])
def remove_from_cart(product_id):
    if 'cart' in session and str(product_id) in session['cart']:
        del session['cart'][str(product_id)]
        session.modified = True
        return jsonify({'message': 'Product removed from cart', 'cart': session['cart']})

    return jsonify({'message': 'Product not found in cart'}), 404

# Clear entire cart
@app.route('/clear_cart', methods=['POST'])
def clear_cart():
    session.pop('cart', None)
    return render_template('cart.html', cart=session.get('cart', {}))

if __name__ == '__main__':
    app.run(debug=True, port=5000)
