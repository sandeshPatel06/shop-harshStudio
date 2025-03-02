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
app.config['UPLOAD_FOLDER'] = 'static/uploads'  # Directory to store uploaded images
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}  # Allowed image file extensions

# Database path (Stored locally on PC)
db_path = os.path.join(os.getcwd(), "product_management.db")

# Configure SQLite database connection
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{db_path}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Disable modification tracking

# Initialize the SQLAlchemy database instance
db = SQLAlchemy(app)

# Define the User model for the database
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)  # Primary key
    username = db.Column(db.String(100), unique=True, nullable=False)  # Unique username
    password = db.Column(db.String(100), nullable=False)  # User password
    role = db.Column(db.String(20), nullable=False)  # User role (admin or user)

# Define the Product model for the database
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)  # Primary key
    name = db.Column(db.String(100), nullable=False)  # Product name
    price = db.Column(db.Float, nullable=False)  # Product price
    description = db.Column(db.Text, nullable=False)  # Product description
    image_path = db.Column(db.String(255), nullable=True)  # Path to the product image

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
        # Get username and password from the form
        username = request.form['username']
        password = request.form['password']
        
        # Query the database for the user
        user = User.query.filter_by(username=username, password=password).first()
        
        if user:
            # Store user session information
            session['logged_in'] = True
            session['role'] = user.role
            # Redirect to admin dashboard or public page based on user role
            return redirect('/admin' if user.role == 'admin' else '/')
        else:
            # Render login page with error message
            return render_template('login.html', error='Invalid username or password')

    # Render login page for GET request
    return render_template('login.html', error='')

# Decorator to restrict access to admin routes
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Check if user is logged in and has admin role
        if 'logged_in' not in session or session.get('role') != 'admin':
            return redirect('/login')  # Redirect to login if not authorized
        return f(*args, **kwargs)  # Proceed to the requested function
    return decorated_function

# Create admin user route
@app.route('/create_admin', methods=['GET', 'POST'])
@admin_required  # Ensure only admin can access this route
def create_admin():
    if request.method == 'POST':
        # Get new admin username and password from the form
        username = request.form['new_admin_username']
        password = request.form['new_admin_password']
        
        # Create a new admin user and add to the database
        new_admin = User(username=username, password=password, role='admin')
        db.session.add(new_admin)
        db.session.commit()

        # Render the create admin page with success message
        return render_template('create_admin.html', success='New admin created successfully!')
    
    # Render create admin page for GET request
    return render_template('create_admin.html')

# Add product route
@app.route('/add_product', methods=['GET', 'POST'])
def add_product():
    # Check if user is logged in
    if 'logged_in' in session and session['logged_in']:
        if request.method == 'POST':
            # Get product details from the form
            name = request.form['name']
            price = float(request.form['price'])
            description = request.form['description']
            
            # Check if a file was uploaded
            if 'file' not in request.files:
                return redirect(request.url)  # No file uploaded, redirect back
            file = request.files['file']

            # Check if the file has a valid filename
            if file.filename == '':
                return redirect(request.url)  # No file selected, redirect back

            # Validate the file extension
            if file and allowed_file(file.filename):
                # Secure the filename and save the file
                filename = secure_filename(file.filename)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)

                # Create a new product and add to the database
                new_product = Product(name=name, price=price, description=description, image_path="uploads/"+filename)
                db.session.add(new_product)
                db.session.commit()

                return redirect('/admin')  # Redirect to admin page after adding product
        else:
            # Render add product page for GET request
            return render_template('add_product.html')
    else:
        return redirect('/login')  # Redirect to login if not logged in

# Public homepage displaying all products
@app.route('/')
def public_page():
    # Query all products from the database
    products = Product.query.all()
    # Render the homepage with the list of products
    return render_template('index.html', products=products)

# Admin dashboard
@app.route('/admin')
def admin():
    
    # Check if user is logged in
    if 'logged_in' in session and session['logged_in']:
        # Query all products for the admin dashboard
        products = Product.query.all()
        return render_template('admin.html', products=products)  # Render admin page
    else:
        return redirect('/login')  # Redirect to login if not logged in

# View product details
@app.route('/product/<int:product_id>', methods=['GET'])
def product_details(product_id):
    # Query the product by ID
    product = Product.query.get(product_id)
    if product:
        # Return product details as JSON
        return jsonify({
            'id': product.id,
            'name': product.name,
            'price': product.price,
            'description': product.description,
            'image_path': product.image_path
        })
    else:
        # Return error if product not found
        return jsonify({'error': 'Product not found'}), 404

# Delete product route
@app.route('/delete_product/<int:product_id>', methods=['POST'])
def delete_product(product_id):
    # Check if user is logged in
    if 'logged_in' in session and session['logged_in']:
        # Query the product by ID
        product = Product.query.get(product_id)

        if product:
            # Remove the product image file if it exists
            if product.image_path:
                os.remove("static/"+product.image_path)

            # Delete the product from the database
            db.session.delete(product)
            db.session.commit()
        
        return redirect('/admin')  # Redirect to admin page after deletion
    else:
        return redirect('/login')  # Redirect to login if not logged in

# Add product to cart
@app.route('/add_to_cart/<int:product_id>', methods=['POST'])
def add_to_cart(product_id):
    # Query the product by ID
    product = Product.query.get(product_id)
    
    if not product:
        return jsonify({'message': 'Product not found'}), 404  # Return error if product not found
    
    # Initialize cart in session if it doesn't exist
    if 'cart' not in session:
        session['cart'] = {}

    cart = session['cart']
    # Check if product is already in the cart
    if str(product_id) in cart:
        # Increase quantity if product is already in the cart
        cart[str(product_id)]['quantity'] += 1
    else:
        # Add new product to the cart
        cart[str(product_id)] = {'name': product.name, 'price': product.price, 'quantity': 1}
    
    session.modified = True  # Mark session as modified
    return jsonify({'message': 'Product added to cart', 'cart': cart})  # Return updated cart

# View cart
@app.route('/cart')
def cart():
    # Retrieve all products from the database
    products = Product.query.all()
    
    # Get the current cart from the session, defaulting to an empty dictionary if it doesn't exist
    cart = session.get('cart', {})
    
    # Render the cart page with current cart contents and available products
    return render_template('cart.html', products=products, cart=cart)

# Remove product from cart
@app.route('/remove_from_cart/<int:product_id>', methods=['POST'])
def remove_from_cart(product_id):
    # Check if cart exists in session and product is in the cart
    if 'cart' in session and str(product_id) in session['cart']:
        del session['cart'][str(product_id)]  # Remove product from cart
        session.modified = True  # Mark session as modified
        return jsonify({'message': 'Product removed from cart', 'cart': session['cart']})
    
    return jsonify({'message': 'Product not found in cart'}), 404  # Return error if product not found in cart

# Clear entire cart
@app.route('/clear_cart', methods=['POST'])
def clear_cart():
    session.pop('cart', None)  # Remove cart from session
    return render_template('cart.html', cart=session.get('cart', {}))  # Render cart page

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
