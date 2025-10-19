"""
Script to create the test database for running tests
"""
import mysql.connector
from mysql.connector import Error

def create_test_database():
    """Create the test database if it doesn't exist"""
    try:
        # Connect to MySQL server (without specifying a database)
        connection = mysql.connector.connect(
            host='127.0.0.1',
            user='root',
            password='password'
        )
        
        if connection.is_connected():
            cursor = connection.cursor()
            
            # Create test database if it doesn't exist
            cursor.execute("CREATE DATABASE IF NOT EXISTS mechanic_shop_v4_test")
            print("✓ Test database 'mechanic_shop_v4_test' created successfully")
            
            cursor.close()
            connection.close()
            print("✓ Database connection closed")
            return True
            
    except Error as e:
        print(f"✗ Error creating test database: {e}")
        return False

if __name__ == "__main__":
    print("Creating test database...")
    success = create_test_database()
    exit(0 if success else 1)
