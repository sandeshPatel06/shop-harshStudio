# Product Management System

Welcome to the Product Management System! This system allows administrators to manage products and display them to the public.

## Installation

### 1. Install Python and pip
1. **Download Python:**
   - Go to the [Python official website](https://www.python.org/).
   - Download the latest version of Python for Windows.

2. **Run the Installer:**
   - Open the downloaded installer.
   - Make sure to check the box that says "Add Python to PATH".
   - Click "Install Now" and follow the prompts to complete the installation.

3. **Verify pip Installation:**
   - Open Command Prompt and run:
     ```bash
     pip --version
     ```
   - If pip is not installed, you can install it using:
     ```bash
     python -m ensurepip --upgrade
     ```

### 2. Install phpMyAdmin
(skip 1 to 4 if you are using XAMPP)

1. **Download phpMyAdmin:**
   - Go to the [phpMyAdmin official website](https://www.phpmyadmin.net/).
   - Download the latest version of phpMyAdmin for Windows.

2. **Extract phpMyAdmin:**
   - Extract the downloaded zip file to your web server's root directory (e.g., `C:\xampp\htdocs\` if using XAMPP).

3. **Configure phpMyAdmin:**
   - Open the `config.inc.php` file in the extracted phpMyAdmin directory.
   - Configure the database settings, such as setting the `auth_type` to `cookie` and providing the MySQL username and password.

4. **Start Your Web Server:**
   - If using XAMPP, start Apache and MySQL from the XAMPP control panel.

5. **Access phpMyAdmin:**
   - Open your web browser and navigate to:
     ```
     http://localhost/phpmyadmin
     ```

### 3. Clone the Repository
Clone the repository from GitHub:

```bash
git clone https://github.com/sandeshPatel06/shop-harshStudio.git
```

### 4. Set Up Virtual Environment
Navigate to the project directory:

```bash
cd shop-harshStudio
```

Create a virtual environment:

```bash
python -m venv venv
```

### 5. Activate Virtual Environment
Activate the virtual environment:

```bash
.\venv\Scripts\activate.ps1
```

### 6. Install Dependencies
Install the required dependencies:

```bash
pip install -r requirements.txt
```


### 7. Run the Application
Run the application:

```bash
python app.py
```

### 8. Access the Application
Open your web browser and navigate to:

```
http://localhost:5000
```

## Usage

### Admin Interface
1. Navigate to `http://localhost:5000/login` to access the admin login page.
2. Use the default admin credentials:
   - Username: `Harsh`
   - Password: `5654`
3. Once logged in, you can add, edit, and delete products using the admin dashboard at `http://localhost:5000/admin`.

### Public Interface
1. The public interface displays the list of available products.
2. Access the public interface at `http://localhost:5000/`.
3. Click on a product to view its details, including an option to contact via WhatsApp for purchase inquiries.

## Database Structure
The database structure consists of the following tables:

- **products**: Stores information about products, including name, price, description, image path, and WhatsApp number for purchase inquiries.

```sql
CREATE TABLE products (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    price DECIMAL(10, 2) NOT NULL,
    description TEXT,
    image_path VARCHAR(255)
);
```

## Dependencies
- **Flask**: Web framework for building the application.
- **MySQL Connector**: Python driver for MySQL database connection.

---

By following these steps, you should be able to set up, configure, and run your Product Management System on Windows using Python 3 and phpMyAdmin.

