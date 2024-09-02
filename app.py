from flask import Flask, render_template, request, redirect, session
import os
import mysql.connector
from werkzeug.utils import secure_filename

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
# Route for logging out
@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect('/login')
# Route for login page
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Check if the credentials are correct (static for demonstration)
        if username == 'admin' and password == '1234':
            session['logged_in'] = True
            return redirect('/admin')
        else:
            return render_template('login.html', error='Invalid username or password')
    return render_template('login.html', error='')

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

if __name__ == '__main__':
    app.run(debug=True)