#!/usr/bin/env python3
# app.py
import json
import sys
import getpass
import psycopg2
from psycopg2 import sql
from psycopg2.extras import RealDictCursor

def load_config():
    """Load configuration from JSON file"""
    try:
        with open("config.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        print("Error: config.json not found!")
        sys.exit(1)
    except json.JSONDecodeError:
        print("Error: Invalid JSON in config.json!")
        sys.exit(1)

def get_user_credentials():
    """Get username and password from user"""
    print("=== PostgreSQL Connection ===")
    username = input("Username: ").strip()
    password = getpass.getpass("Password: ")
    return username, password

def create_connection(config, username, password):
    """Create secure database connection"""
    
    # Allowed configuration keys (prevent injection)
    ALLOWED_KEYS = {
        "host": "localhost",
        "port": 5432,
        "dbname": None,
        "sslmode": "prefer",
        "connect_timeout": 10,
        "client_encoding": "UTF8"
    }
    
    # Build connection parameters
    conn_params = {}
    
    # Copy only allowed keys from config
    for key in ALLOWED_KEYS:
        if key in config:
            conn_params[key] = config[key]
        elif ALLOWED_KEYS[key] is not None:
            conn_params[key] = ALLOWED_KEYS[key]
    
    # Add user credentials (only these come from user)
    conn_params["user"] = username
    conn_params["password"] = password
    
    # Validate required fields
    if "dbname" not in conn_params:
        print("Error: Database name (dbname) must be specified in config.json")
        sys.exit(1)
    
    try:
        # Convert port to integer
        conn_params["port"] = int(conn_params.get("port", 5432))
    except ValueError:
        print("Error: Invalid port number")
        sys.exit(1)
    
    return conn_params

def test_connection(conn_params):
    """Test database connection and execute version query"""
    try:
        print("\nConnecting to database...")
        connection = psycopg2.connect(**conn_params)
        
        with connection.cursor(cursor_factory=RealDictCursor) as cursor:
            # Execute version query
            cursor.execute("SELECT version();")
            result = cursor.fetchone()
            print(f"\n✅ PostgreSQL Version: {result['version']}")
            
            # Additional verification: Check authentication method
            cursor.execute("SHOW password_encryption;")
            auth_method = cursor.fetchone()
            print(f"✅ Authentication Method: {auth_method['password_encryption']}")
            
            # Check database encoding
            cursor.execute("SELECT datname, encoding FROM pg_database WHERE datname = %s;", 
                         (conn_params['dbname'],))
            db_info = cursor.fetchone()
            if db_info:
                # Convert encoding number to name
                cursor.execute("SELECT pg_encoding_to_char(%s);", (db_info['encoding'],))
                encoding_name = cursor.fetchone()
                print(f"✅ Database Encoding: {encoding_name['pg_encoding_to_char']}")
        
        connection.close()
        print("\n✅ Connection successful!")
        return True
        
    except psycopg2.OperationalError as e:
        print(f"\n❌ Connection failed: {e}")
        print("\nTroubleshooting tips:")
        print("1. Check if PostgreSQL Docker container is running")
        print("2. Verify username/password")
        print("3. Check config.json settings")
        return False
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return False

def main():
    """Main function"""
    # Load configuration from file
    config = load_config()
    
    # Get credentials from user
    username, password = get_user_credentials()
    
    # Create secure connection parameters
    conn_params = create_connection(config, username, password)
    
    # Display connection info (without password)
    display_params = conn_params.copy()
    display_params["password"] = "***hidden***"
    print(f"\nConnection parameters: {display_params}")
    
    # Test connection
    success = test_connection(conn_params)
    
    if success:
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()