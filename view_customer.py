import mysql.connector
from flask import Blueprint, jsonify, render_template

view_customer_bp = Blueprint('view_customer', __name__)

# MySQL database connection
db_config = {
    'user': 'root',
    'password': '',
    'host': 'localhost',
    'database': 'supermarket'
}

# Function to connect to the database
def connect_to_db():
    return mysql.connector.connect(**db_config)

# Function to view customers
@view_customer_bp.route('/view_customers', methods=['GET'])
def view_customers():
    connection = connect_to_db()
    cursor = connection.cursor()
    cursor.execute("SELECT name, phone, id_number, area, image_path FROM customers")
    customers = cursor.fetchall()
    
    customer_data = []
    for customer in customers:
        customer_info = {
            'name': customer[0],
            'phone': customer[1],
            'id_number': customer[2],
            'area': customer[3],
            'image_path': customer[4]  # Path to the customer's image
        }
        customer_data.append(customer_info)
    
    cursor.close()
    connection.close()

    return render_template('view_customer.html', customers=customer_data)
