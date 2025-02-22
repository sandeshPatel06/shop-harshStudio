from flask import Flask, render_template, request, redirect, session, jsonify
import os
import mysql.connector  # Add this import statement
from werkzeug.utils import secure_filename
from functools import wraps


app = Flask(__name__)
app.secret_key = 'your_secret_key'
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}

# Function to connect to the MySQL database
def connect_db():
    return mysql.connector.connect(
        host='localhost',
        user='root',
        password='',
        database='product_management_system'
    )

# Check if a file has an allowed extension
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Connect to the database
        db = connect_db()
        cursor = db.cursor(dictionary=True)

        cursor.execute('SELECT * FROM users WHERE username = %s AND password = %s', (username, password))
        user = cursor.fetchone()
        
        if user:
            session['logged_in'] = True
            session['role'] = user['role']  # Assign user role from the database
            return redirect('/admin' if user['role'] == 'admin' else '/')
        else:
            return render_template('login.html', error='Invalid username or password')

    return render_template('login.html', error='')



def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session or session.get('role') != 'admin':
            return redirect('/login')
        return f(*args, **kwargs)
    return decorated_function


@app.route('/create_admin', methods=['GET', 'POST'])
@admin_required
def create_admin():
    if request.method == 'POST':
        username = request.form['new_admin_username']
        password = request.form['new_admin_password']
        
        # Connect to the database
        db = connect_db()
        cursor = db.cursor()

        # Insert new admin into the database
        cursor.execute('INSERT INTO users (username, password, role) VALUES (%s, %s, %s)', (username, password, 'admin'))
        db.commit()
        
        # Close the database connection
        db.close()

        return render_template('create_admin.html', success='New admin created successfully!')
    
    return render_template('create_admin.html')



# Route for adding a product
@app.route('/add_product', methods=['GET', 'POST'])
def add_product():
    if 'logged_in' in session and session['logged_in']:
        if request.method == 'POST':
            name = request.form['name']
            price = float(request.form['price'])
            description = request.form['description']
            
            # Check if the post request has the file part
            if 'file' not in request.files:
                return redirect(request.url)
            file = request.files['file']

            # If the user does not select a file, the browser submits an empty part without a filename
            if file.filename == '':
                return redirect(request.url)

            # Check if the file is allowed
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)

                # Connect to the database
                db = connect_db()
                cursor = db.cursor()

                # Insert product data into the database
                cursor.execute('INSERT INTO products (name, price, description, image_path) VALUES (%s, %s, %s, %s)', (name, price, description, "uploads/"+filename))
                db.commit()

                # Close the database connection
                db.close()

                return redirect('/admin')
            else:
                return redirect(request.url)
        else:
            return render_template('add_product.html')
    else:
        return redirect('/login')

# Route for public page
@app.route('/')
def public_page():
    # Connect to the database
    db = connect_db()
    cursor = db.cursor(dictionary=True)
    
    # Fetch products data from the database
    cursor.execute('SELECT * FROM products')
    products = cursor.fetchall()
    
    # Close the database connection
    db.close()

    return render_template('index.html', products=products)
@app.route('/test')
def page():
  

    return render_template('test.html')

# Route for admin page
@app.route('/admin')
def admin():
    if 'logged_in' in session and session['logged_in']:
        # Connect to the database
        db = connect_db()
        cursor = db.cursor(dictionary=True)
        
        # Fetch products data from the database
        cursor.execute('SELECT * FROM products')
        products = cursor.fetchall()
        
        # Close the database connection
        db.close()

        return render_template('admin.html', products=products)
    else:
        return redirect('/login')

# Route for deleting a product
@app.route('/delete_product/<int:product_id>', methods=['POST'])
def delete_product(product_id):
    if 'logged_in' in session and session['logged_in']:
        # Connect to the database
        db = connect_db()
        cursor = db.cursor()

        # Get the image path of the product to be deleted
        cursor.execute('SELECT image_path FROM products WHERE id = %s', (product_id,))
        result = cursor.fetchone()
        image_path = result[0]

        # Delete product data from the database
        cursor.execute('DELETE FROM products WHERE id = %s', (product_id,))
        db.commit()

        # Close the database connection
        db.close()

        # Delete the image file from the server
        if image_path:
            os.remove("static/"+image_path)
        
        return redirect('/admin')
    else:
        return redirect('/login')

# Add the rest of the routes and functions as before
@app.route('/add_to_cart/<int:product_id>', methods=['POST'])
def add_to_cart(product_id):
    db = connect_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute('SELECT * FROM products WHERE id = %s', (product_id,))
    product = cursor.fetchone()
    db.close()
    
    if not product:
        return jsonify({'message': 'Product not found'}), 404
    
    if 'cart' not in session:
        session['cart'] = {}

    cart = session['cart']
    if str(product_id) in cart:
        cart[str(product_id)]['quantity'] += 1
    else:
        cart[str(product_id)] = {'name': product['name'], 'price': product['price'], 'quantity': 1}
    
    session.modified = True
    return jsonify({'message': 'Product added to cart', 'cart': cart})

@app.route('/cart')
def cart():
    return render_template('cart.html', cart=session.get('cart', {}))
@app.route('/remove_from_cart/<int:product_id>', methods=['POST'])
def remove_from_cart(product_id):
    if 'cart' in session and str(product_id) in session['cart']:
        del session['cart'][str(product_id)]  # Remove product from cart
        session.modified = True
        return jsonify({'message': 'Product removed from cart', 'cart': session['cart']})
    
    return jsonify({'message': 'Product not found in cart'}), 404

@app.route('/clear_cart', methods=['POST'])
def clear_cart():
    session.pop('cart', None)
    
    return render_template('cart.html', cart=session.get('cart', {}))


if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0')