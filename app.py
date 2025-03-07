from flask import Flask, render_template, request, redirect, session, jsonify, flash, url_for
import os
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from flask_sqlalchemy import SQLAlchemy
import urllib.parse
from flask_mail import Mail, Message
from functools import wraps



# Initialize the Flask application
app = Flask(__name__)

# Secret key for session management (should be kept secret in production)
app.secret_key = 'your_secret_key'



# Configuration for file uploads
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}
app.config['MAIL_SERVER'] = 'smtp.gmail.com'  # Use Gmail's SMTP server
app.config['MAIL_PORT'] = 587  # Gmail SMTP port
app.config['MAIL_USE_TLS'] = True  # Use TLS encryption
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_USERNAME'] = ''  # Replace with your email
app.config['MAIL_PASSWORD'] = ''  # Replace with your email password
app.config['MAIL_DEFAULT_SENDER'] = 'patelbr5118s@gmail.com'  # Replace with your email


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
    role = db.Column(db.String(20), nullable=False)  # 'admin', 'seller', 'buyer'

# Define the Product model for the database
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    description = db.Column(db.Text, nullable=False)
    image_path = db.Column(db.String(255), nullable=True)
    seller_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete="CASCADE"), nullable=False)  

    seller = db.relationship('User', backref=db.backref('products', lazy=True, cascade="all, delete"))


# Create database tables if they don't exist
with app.app_context():
    db.create_all()



# Function to check if a file has an allowed extension
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def role_required(required_role):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'logged_in' not in session or session.get('role') != required_role:
                flash('Unauthorized Access!', 'error')
                return redirect(url_for('login'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator
# User login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            session.permanent = True
            session['user_id'] = user.id
            session['role'] = user.role
            session['logged_in'] = True  # Add this line

            flash("Login successful!", "success")


            # Redirect based on role
            if user.role == 'admin':
                return redirect(url_for('admin_dashboard'))
            elif user.role == 'seller':
                return redirect(url_for('seller_dashboard'))
            else:
                return redirect(url_for('buyer_dashboard'))

        else:
            flash("Unauthorized Access!", "error")

    return render_template('login.html')


# Decorator to restrict access to admin routes
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session or session.get('role') != 'admin':
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/manage_users')
def manage_users():
    users = User.query.all()  # Fetch all users
    return render_template('manage_users.html', users=users)

@app.route('/edit_user/<int:user_id>', methods=['GET', 'POST'])
def edit_user(user_id):
    user = User.query.get(user_id)
    if request.method == 'POST':
        user.username = request.form['username']
        user.role = request.form['role']
        db.session.commit()
        flash("User updated successfully", "success")
        return redirect(url_for('manage_users'))
    return render_template('edit_user.html', user=user)

@app.route('/delete_user/<int:user_id>')
def delete_user(user_id):
    user = User.query.get(user_id)
    db.session.delete(user)
    db.session.commit()
    flash("User deleted successfully", "danger")
    return redirect(url_for('manage_users'))


@app.route('/checkout')
def checkout():
    product_id = request.args.get('productId')
    product_name = request.args.get('productName')
    product_price = request.args.get('productPrice')
    return render_template('checkout.html', product_id=product_id, product_name=product_name, product_price=product_price)


@app.route('/admin_dashboard')
@role_required('admin')
def admin_dashboard():
    products = Product.query.all()  # Fetch all products
    return render_template('admin_dashboard.html', products=products)


@app.route('/seller_dashboard')
@role_required('seller')
def seller_dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    seller_id = session.get('user_id')  # Get the logged-in seller's ID
    products = Product.query.filter_by(seller_id=seller_id).all()  # Fetch only seller's products
    
    return render_template('seller_dashboard.html', products=products)

@app.route('/buyer_dashboard')
@role_required('buyer')
def buyer_dashboard():
    return render_template('buyer_dashboard.html')
@app.route('/logout')
def logout():
    session.pop('user_id', None)  # Remove user_id from session
    return redirect(url_for('login'))  # Redirect to the login page


# Create admin user route
@app.route('/create_admin', methods=['GET', 'POST'])
@admin_required
def create_admin():
    if request.method == 'POST':
        username = request.form['new_admin_username']
        password = generate_password_hash(request.form['new_admin_password'])
        new_admin = User(username=username, password=password, role='admin')
        db.session.add(new_admin)
        db.session.commit()
        flash('New admin created successfully!', 'success')
    
    return render_template('create_admin.html')
@app.route('/create_user', methods=['GET', 'POST'])
def create_user():
    if request.method == 'POST':
        username = request.form['username']
        password = generate_password_hash(request.form['password'])
        role = request.form['role']  # Get role from form (admin, seller, buyer)

        new_user = User(username=username, password=password, role=role)
        db.session.add(new_user)
        db.session.commit()
        flash('New user created successfully!', 'success')

    return render_template('register.html')


# Add product route
@app.route('/add_product', methods=['GET', 'POST'])
@role_required('seller')
def add_product():
    if request.method == 'POST':
        name = request.form['name']
        price = float(request.form['price'])
        description = request.form['description']
        seller_id = session.get('user_id')  # Get the seller's ID from session
        
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)

            new_product = Product(name=name, price=price, description=description, image_path="uploads/" + filename, seller_id=seller_id)
            db.session.add(new_product)
            db.session.commit()
            flash('Product added successfully!', 'success')

            return redirect(url_for('seller_dashboard'))

    return render_template('add_product.html')


# Public homepage displaying all products
@app.route('/')
def public_page():
    products = Product.query.all()  # Fetch all products
    return render_template('index.html', products=products)



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
            'image_url': url_for('static', filename=product.image_path)  # Include the full image URL
        })
    return jsonify({'error': 'Product not found'}), 404

# Delete product route

@app.route('/manage_products')
@role_required('admin')
def manage_products():
    products = Product.query.all()  # Get all products
    return render_template('manage_products.html', products=products)


@app.route('/admin/view_products')
@role_required('admin')
def admin_view_products():
    products = Product.query.all()
    return render_template('view_products.html', products=products)

@app.route('/admin/delete_product/<int:product_id>', methods=['POST'])
@role_required('admin')
def delete_product(product_id):
    product = Product.query.get_or_404(product_id)
    db.session.delete(product)
    db.session.commit()
    flash("Product deleted successfully!", "success")
    return redirect(url_for('admin_view_products'))

@app.route('/admin/edit_product/<int:product_id>', methods=['GET', 'POST'])
@role_required('admin')
def edit_product(product_id):
    product = Product.query.get_or_404(product_id)
    if request.method == 'POST':
        product.name = request.form['name']
        product.price = request.form['price']
        product.description = request.form['description']
        db.session.commit()
        flash("Product updated successfully!", "success")
        return redirect(url_for('admin_view_products'))
    return render_template('edit_product.html', product=product)


# Function to get the total number of items in the cart
@app.route("/cart_count")
def cart_count():
    cart = session.get("cart", {})
    count = sum(item["quantity"] for item in cart.values())
    return jsonify({"count": count})

# Route to add an item to the cart dynamically
@app.route("/add_to_cart/<product_id>", methods=["POST"])
def add_to_cart(product_id):
    cart = session.get("cart", {})
    if product_id in cart:
        cart[product_id]["quantity"] += 1
    else:
        # Example product data, replace with actual database fetch
        cart[product_id] = {"name": "Product " + product_id, "price": 10, "quantity": 1}
    
    session["cart"] = cart
    return jsonify({"success": True, "cart": cart})
# View Cart Route
@app.route("/cart")
def cart():
    cart = session.get("cart", {})
    return render_template("cart.html", cart=cart)

# Remove Item from Cart
# Remove an item from the cart dynamically
@app.route("/remove_from_cart/<product_id>", methods=["POST"])
def remove_from_cart(product_id):
    cart = session.get("cart", {})
    if product_id in cart:
        del cart[product_id]
        session["cart"] = cart
    return jsonify({"success": True})

# Clear the cart dynamically
@app.route("/clear_cart", methods=["POST"])
def clear_cart():
    session["cart"] = {}
    return jsonify({"success": True})

# Run the application


if __name__ == '__main__':
    app.run(host='0.0.0.0')
    
