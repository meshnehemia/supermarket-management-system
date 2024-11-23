import mysql.connector
from mysql.connector import errorcode

# MySQL connection configuration
db_config = {
    'user': 'root',      # Change as needed
    'password': '',      # Add your password if necessary
    'host': 'localhost',
    'database': 'supermarket'  # Database name
}

# Tables definition
TABLES = {}

# Customers table for storing customer details, including face encodings
TABLES['customers'] = (
    """
    CREATE TABLE IF NOT EXISTS customers (
        customer_id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(255) NOT NULL,
        phone VARCHAR(20),
        id_number VARCHAR(20),
        area VARCHAR(255),
        face_encoding LONGBLOB,  -- To store face encodings
        image_path VARCHAR(255)  -- Path to the stored face image
    ) ENGINE=InnoDB
    """
)

# Transactions table for storing each customer's transactions (if needed later)
TABLES['transactions'] = (
    """
    CREATE TABLE IF NOT EXISTS transactions (
        transaction_id INT AUTO_INCREMENT PRIMARY KEY,
        customer_id INT,
        total_amount DECIMAL(10, 2),
        transaction_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (customer_id) REFERENCES customers(customer_id) ON DELETE CASCADE
    ) ENGINE=InnoDB
    """
)

# Function to connect to MySQL
def connect_to_db():
    try:
        return mysql.connector.connect(**db_config)
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return None

# Function to create the tables
def create_tables():
    connection = connect_to_db()
    if connection is None:
        return
    cursor = connection.cursor()

    # Try to create each table
    for table_name, table_sql in TABLES.items():
        try:
            print(f"Creating table {table_name}... ", end='')
            cursor.execute(table_sql)
            print("OK")
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_TABLE_EXISTS_ERROR:
                print(f"Table {table_name} already exists.")
            else:
                print(f"Error creating table {table_name}: {err}")
    
    cursor.close()
    connection.close()

if __name__ == "__main__":
    create_tables()
