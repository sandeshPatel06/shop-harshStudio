# Shop Harsh Studio - E-commerce Platform

A professional e-commerce platform built with Flask, featuring user roles (admin, seller, buyer), product management, order processing, and secure authentication.

## Features

- **User Management**
  - Role-based access control (Admin, Seller, Buyer)
  - Secure authentication and authorization
  - User profile management
  - Address management

- **Product Management**
  - Product listing and details
  - Image upload support
  - Product categorization
  - Price and inventory management

- **Order Processing**
  - Order creation and management
  - Order status tracking
  - Order history
  - Custom order instructions

- **Admin Dashboard**
  - User management
  - Order management
  - Product oversight
  - Analytics and reporting

## Tech Stack

- **Backend**: Flask 3.0.3
- **Database**: SQLite with SQLAlchemy ORM
- **Frontend**: Bootstrap 5, HTML5, CSS3
- **Authentication**: Flask-Login
- **File Handling**: Werkzeug
- **Environment Management**: python-dotenv

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/shop-harshStudio.git
cd shop-harshStudio
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

5. Initialize the database:
```bash
flask db upgrade
```

6. Run the application:
```bash
flask run
```

## Project Structure

```
shop-harshStudio/
├── app.py              # Main application file
├── requirements.txt    # Project dependencies
├── .env               # Environment variables
├── .gitignore         # Git ignore file
├── static/            # Static files (CSS, JS, images)
│   └── uploads/       # User uploaded files
├── templates/         # HTML templates
│   ├── errors/        # Error pages
│   └── ...           # Other templates
└── logs/             # Application logs
```

## Security Features

- Secure password hashing
- CSRF protection
- Session management
- Role-based access control
- File upload validation
- Input sanitization
- Error handling

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support, email support@harshstudio.com or open an issue in the repository.

## Acknowledgments

- Flask team for the amazing framework
- Bootstrap team for the UI components
- All contributors who have helped improve this project
