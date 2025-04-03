from flask import Flask, render_template, request, redirect, session, jsonify, flash, url_for
import os
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from flask_sqlalchemy import SQLAlchemy
import urllib.parse
# from flask_mail import Mail, Message
from functools import wraps
from flask_migrate import Migrate



# Initialize the Flask application
app = Flask(__name__)

# Secret key for session management (should be kept secret in production)
app.secret_key = 'your_secret_key'



# Configuration for file uploads
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}
# app.config['MAIL_SERVER'] = 'smtp.gmail.com'  # Use Gmail's SMTP server
# app.config['MAIL_PORT'] = 587  # Gmail SMTP port
# app.config['MAIL_USE_TLS'] = True  # Use TLS encryption
# app.config['MAIL_USE_SSL'] = False
# app.config['MAIL_USERNAME'] = ''  # Replace with your email
# app.config['MAIL_PASSWORD'] = ''  # Replace with your email password
# app.config['MAIL_DEFAULT_SENDER'] = 'patelbr5118s@gmail.com'  # Replace with your email


# Database path (Stored locally on PC)
db_path = os.path.join(os.getcwd(), "product_management.db")

# Configure SQLite database connection
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{db_path}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize the SQLAlchemy database instance
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Define the User model for the database
class Address(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(100), nullable=True)
    address_line = db.Column(db.String(255), nullable=True)
    city = db.Column(db.String(100), nullable=True)
    state = db.Column(db.String(100), nullable=True)
    zip_code = db.Column(db.String(20), nullable=True)

    # Relationship with User: one-to-one (each user has one address)
    user = db.relationship('User', backref=db.backref('address', uselist=False))

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # 'admin', 'seller', 'buyer'
    email = db.Column(db.String(100), unique=True, nullable=True)

    orders = db.relationship('Order', backref='buyer', lazy=True)  # Relationship with Order


class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    buyer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    status = db.Column(db.String(50), default="Processing")  # Order status (Processing, Shipped, Delivered)
    date_ordered = db.Column(db.DateTime, default=db.func.current_timestamp())

    product = db.relationship('Product', backref='orders')

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
                # flash('Unauthorized Access!', 'error')
                return redirect(url_for('login'),error_message='Unauthorized Access!')
            return f(*args, **kwargs)
        return decorated_function
    return decorator
# User login route
@app.route('/contact')
def contact():
    return render_template('contact.html')
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
            session['logged_in'] = True  # Add this line if user present

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


@app.route('/store_product_in_session', methods=['POST'])
def store_product_in_session():
    data = request.get_json()
    session['product_id'] = data['id']
    session['product_name'] = data['name']
    session['product_price'] = data['price']
    return jsonify({'success': True}), 200

@app.route('/checkout', methods=['GET', 'POST'])
@role_required('buyer')
def checkout():
    # Retrieve product details from session
    product_id = session.get('product_id')
    product_name = session.get('product_name')
    product_price = session.get('product_price')

    # If no product is found in the session, redirect to product listing page
    if not product_id:
        flash("No product selected.", "danger")
        return redirect(url_for('public_page'))  # Redirect to product listing

    # Fetch product from the database
    product = Product.query.get(product_id)
    if not product:
        flash("Product not found.", "danger")
        return redirect(url_for('public_page'))

    # Handle POST request when user submits the order
    if request.method == 'POST':
        try:
            # Get the quantity from the form
            quantity = int(request.form['quantity'])


            # Create a new order
            new_order = Order(
                buyer_id=session['user_id'],  # The logged-in user ID
                product_id=product_id,        # The product being ordered
                quantity=quantity,            # The quantity being ordered
                status="Processing"           # Initial status of the order
            )

            # Add the order to the database and commit
            db.session.add(new_order)
            db.session.commit()


            # Flash success message and redirect to order history page
            flash("Order placed successfully!", "success")
            return redirect(url_for('order_history'))

        except ValueError:
            flash("Invalid quantity. Please enter a valid number.", "danger")
            return redirect(url_for('checkout'))  # Redirect back to checkout page

    # Render the checkout page with product details
    return render_template('checkout.html', 
                           product_name=product_name, 
                           product_price=product_price)



# Decorator to restrict access to admin routes
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session or session.get('role') != 'admin':
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function
def seller_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session or session.get('role') != 'seller':
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function
def get_current_user_role():
    return session.get('role')  # Returns 'admin', 'seller', or None
def role_required(allowed_roles):
    def wrapper(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'logged_in' not in session or session.get('role') not in allowed_roles:
                return redirect(url_for('login'))
            return f(*args, **kwargs)
        return decorated_function
    return wrapper
@app.route('/admin/orders')
@role_required('admin')  # Ensure the user is an admin
def admin_orders():
    orders = Order.query.all()  # Admin can view all orders
    return render_template('admin_orders.html', orders=orders)

@app.route('/seller/orders')
@role_required('seller')  # Ensure the user is a seller
def seller_orders():
    seller_id = session.get('user_id')
    orders = Order.query.join(Product).filter(Product.seller_id == seller_id).all()  # Filter by seller ID
    return render_template('seller_orders.html', orders=orders)


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


@app.route('/update_order/<int:order_id>', methods=['POST'])
@role_required(['admin', 'seller'])  # Ensure the user is either admin or seller
def update_order(order_id):
    order = Order.query.get_or_404(order_id)
    
    # Ensure that a seller can only update orders for products they have sold
    if session['role'] == 'seller' and order.product.seller_id != session['user_id']:
        flash("You are not authorized to update this order.", "error")
        return redirect(url_for('seller_orders'))
    
    # Update the order status
    order.status = request.form['status']
    db.session.commit()
    flash("Order status updated!", "success")
    
    # Redirect based on the user's role
    if session['role'] == 'admin':
        return redirect(url_for('admin_orders'))
    else:
        return redirect(url_for('seller_orders'))


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
     products = Product.query.all()  # Fetch all products
     return render_template('buyer_dashboard.html', products=products)
@app.route('/logout')
def logout():
    session.pop('user_id', None)  # Remove user_id from session
    return redirect(url_for('login'))  # Redirect to the login page

@app.route('/profile', methods=['GET', 'POST'])
@role_required('buyer')
def profile():
    user = User.query.get(session['user_id'])

    if request.method == 'POST':
        user.username = request.form['username']
        user.email = request.form['email']
        user.address = request.form['address']
        db.session.commit()
        flash("Profile updated successfully!", "success")

    return render_template('profile.html', user=user)

@app.route('/order_history')
@role_required('buyer')
def order_history():
    orders = Order.query.filter_by(buyer_id=session['user_id']).all()
    return render_template('order_history.html', orders=orders)



# Create admin user route
@app.route('/create_user', methods=['GET', 'POST'])
def create_user():
    if request.method == 'POST':
        # Get data from the form
        username = request.form['username']
        password = generate_password_hash(request.form['password'])  # Hash the password
        role = request.form['role']  # Get role from form (admin, seller, buyer)
        email = request.form.get('email')  # Optional field
        name = request.form['name']
        address_line = request.form['address_line']
        city = request.form['city']
        state = request.form['state']
        zip_code = request.form['zip_code']

        # Create a new User object
        new_user = User(
            username=username,
            password=password,
            role=role,
            email=email,
            name=name,
            address_line=address_line,
            city=city,
            state=state,
            zip_code=zip_code
        )

        # Add user to the database
        db.session.add(new_user)
        db.session.commit()

        flash('New user created successfully!', 'success')
        return redirect(url_for('login'))  # Redirect to login page after creation

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
    try:
        product = Product.query.get(product_id)
        if product:
            return jsonify({
                'id': product.id,
                'name': product.name,
                'price': product.price,
                'description': product.description,
                'image_url': url_for('static', filename=product.image_path)  # Full URL to image
            })
        else:
            # Product not found
            return jsonify({'error': 'Product not found'}), 404
    except Exception as e:
        # Log the error (optional)
        app.logger.error(f"Error fetching product {product_id}: {e}")
        return jsonify({'error': 'An error occurred while fetching product details'}), 500
# Delete product route


@app.route('/manage_products')
@role_required(['admin', 'seller'])  # Allows access for both admin and seller roles
def manage_products():
    products = Product.query.all()  # Get all products
    user_role = get_current_user_role()  # Get the role of the current user
    return render_template('manage_products.html', products=products, user_role=user_role)
@app.route('/user/delete_product/<int:product_id>', methods=['POST'])
@role_required(['admin', 'seller'])  # Allow both admin and seller roles
def delete_product(product_id):
    product = Product.query.get_or_404(product_id)
    
    # Check additional conditions if needed (e.g., sellers can only delete their own products)
    if session.get('role') == 'seller' and product.seller_id != session.get('user_id'):
        flash("You are not authorized to delete this product.", "error")
        return redirect(url_for('manage_products'))  # Redirect to a safer route

    db.session.delete(product)
    db.session.commit()
    flash("Product deleted successfully!", "success")
    return redirect(url_for('manage_products'))

@app.route('/admin/view_products')
@role_required('admin')
def admin_view_products():
    products = Product.query.all()
    return render_template('view_products.html', products=products)

@app.route('/seller/view_products')
@role_required('seller')
def seller_view_products():
    products = Product.query.all()
    return render_template('view_products.html', products=products)


def handle_product_edit(product_id):
    product = Product.query.get_or_404(product_id)
    if request.method == 'POST':
        product.name = request.form['name']
        product.price = request.form['price']
        product.description = request.form['description']
        db.session.commit()
        flash("Product updated successfully!", "success")
        return True, product
    return False, product

@app.route('/admin/edit_product/<int:product_id>', methods=['GET', 'POST'])
@role_required('admin')
def edit_product(product_id):
    updated, product = handle_product_edit(product_id)
    if updated:
        return redirect(url_for('admin_view_products'))
    return render_template('edit_product.html', product=product)

@app.route('/seller/edit_product/<int:product_id>', methods=['GET', 'POST'])
@role_required('seller')
def seller_edit_product(product_id):
    updated, product = handle_product_edit(product_id)
    if updated:
        return redirect(url_for('seller_view_products'))
    return render_template('edit_product.html', product=product)


# Function to get the total number of items in the cart
@app.route("/cart_count")
def cart_count():
    cart = session.get("cart", {})
    count = sum(item["quantity"] for item in cart.values())
    return jsonify({"count": count})

# Route to add an item to the cart dynamically
@app.route("/add_to_cart/<int:product_id>", methods=["POST"])
def add_to_cart(product_id):
    cart = session.get("cart", {})

    # Check if the product is already in the cart
    if product_id in cart:
        cart[product_id]["quantity"] += 1  # Increase quantity if already in cart
    else:
        # Fetch product details from the database
        product = Product.query.get(product_id)
        if product:
            cart[product_id] = {"name": product.name, "price": product.price, "quantity": 1}

    session["cart"] = cart
    return jsonify({"success": True, "cart": cart})

# Update Address in Cart
@app.route('/update_address', methods=['POST'])
def update_address():
    # Get user from database using session['user_id']
    user = User.query.get(session.get('user_id'))  # Fetch user by session user_id

    if user:
        # Update the user's address
        user.address = request.form['address']
        user.city = request.form['city']
        user.state = request.form['state']
        user.zip = request.form['zip']

        # Commit the changes to the database
        db.session.commit()

        # Flash a success message
        flash('Address updated successfully!', 'success')
    else:
        flash('User not found!', 'danger')

    # Redirect back to the cart page
    return redirect(url_for('cart'))


# View Cart Route
@app.route('/cart', methods=['GET', 'POST'])
@role_required('buyer')
def cart():
    # Retrieve the current user's data (including their address) using session['user_id']
    user = User.query.get(session.get('user_id'))  # Fetch user by session user_id
    cart = session.get("cart", {})
    if request.method == 'POST':
        # Update address functionality
        new_address = request.form['address']
        if user:
            user.address = new_address
            db.session.commit()
            flash('Address updated successfully!', 'success')
        else:
            flash('User not found!', 'danger')

        return redirect(url_for('cart'))  # Redirect back to cart page after update

    return render_template('cart.html', user=user,cart=cart)

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
    app.run(host='0.0.0.0',debug=True)
    
