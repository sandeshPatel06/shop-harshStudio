from flask import Flask, render_template, request, redirect, session, jsonify
import os
import platform
from werkzeug.utils import secure_filename
from functools import wraps
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Secret key for session management
app.config['UPLOAD_FOLDER'] = 'static/uploads'  # Folder for uploaded images
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}  # Allowed file extensions

# Database path (Stored locally on PC)
db_path = os.path.join(os.getcwd(), "product_management.db")

# Configure SQLite database
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{db_path}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database
db = SQLAlchemy(app)

# Define User model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # Role can be 'admin' or 'user'

# Define Product model
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    description = db.Column(db.Text, nullable=False)
    image_path = db.Column(db.String(255), nullable=True)  # Image file path

# Create database tables
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
        user = User.query.filter_by(username=username, password=password).first()
        
        if user:
            session['logged_in'] = True
            session['role'] = user.role
            return redirect('/admin' if user.role == 'admin' else '/')
        else:
            return render_template('login.html', error='Invalid username or password')

    return render_template('login.html', error='')

# Decorator to restrict access to admin routes
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session or session.get('role') != 'admin':
            return redirect('/login')
        return f(*args, **kwargs)
    return decorated_function

# Create admin user route
@app.route('/create_admin', methods=['GET', 'POST'])
@admin_required
def create_admin():
    if request.method == 'POST':
        username = request.form['new_admin_username']
        password = request.form['new_admin_password']
        
        new_admin = User(username=username, password=password, role='admin')
        db.session.add(new_admin)
        db.session.commit()

        return render_template('create_admin.html', success='New admin created successfully!')
    
    return render_template('create_admin.html')

# Add product route
@app.route('/add_product', methods=['GET', 'POST'])
def add_product():
    if 'logged_in' in session and session['logged_in']:
        if request.method == 'POST':
            name = request.form['name']
            price = float(request.form['price'])
            description = request.form['description']
            
            if 'file' not in request.files:
                return redirect(request.url)
            file = request.files['file']

            if file.filename == '':
                return redirect(request.url)

            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)

                new_product = Product(name=name, price=price, description=description, image_path="uploads/"+filename)
                db.session.add(new_product)
                db.session.commit()

                return redirect('/admin')
        else:
            return render_template('add_product.html')
    else:
        return redirect('/login')

# Public homepage displaying all products
@app.route('/')
def public_page():
    products = Product.query.all()
    return render_template('index.html', products=products)

# Admin dashboard
@app.route('/admin')
def admin():
    if 'logged_in' in session and session['logged_in']:
        products = Product.query.all()
        return render_template('admin.html', products=products)
    else:
        return redirect('/login')

# View product details
@app.route('/product/<int:product_id>', methods=['GET'])
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
    else:
        return jsonify({'error': 'Product not found'}), 404

# Delete product route
@app.route('/delete_product/<int:product_id>', methods=['POST'])
def delete_product(product_id):
    if 'logged_in' in session and session['logged_in']:
        product = Product.query.get(product_id)

        if product:
            if product.image_path:
                os.remove("static/"+product.image_path)

            db.session.delete(product)
            db.session.commit()
        
        return redirect('/admin')
    else:
        return redirect('/login')

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

# Run Flask app
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)