import json
import psycopg2
import getpass
import sys

# Load connection settings from config.json (only allowed keys will be used)
with open("config.json", "r", encoding="utf-8") as f:
    config = json.load(f)

# Ask user for username (visible) and password (hidden)
username = input("Enter PostgreSQL username: ")
password = getpass.getpass("Enter PostgreSQL password: ")  # <-- hidden input

# Whitelist the config keys that we allow from the file (prevents user injection)
allowed_keys = {
    "host": "localhost",
    "port": 5432,
    "dbname": None
}

# Build connection parameters safely from allowed keys only
conn_params = {}

# host
conn_params["host"] = config.get("host", allowed_keys["host"])
# port (ensure int)
try:
    conn_params["port"] = int(config.get("port", allowed_keys["port"]))
except (TypeError, ValueError):
    print("Invalid port in config.json. Using default 5432.")
    conn_params["port"] = allowed_keys["port"]
# dbname (required)
conn_params["dbname"] = config.get("dbname", allowed_keys["dbname"])
if not conn_params["dbname"]:
    print("Error: dbname must be set in config.json")
    sys.exit(1)

# Add user/password from interactive input (user cannot add extra connection options)
conn_params["user"] = username
conn_params["password"] = password

# Connect and run query
try:
    conn = psycopg2.connect(**conn_params)
    cur = conn.cursor()
    cur.execute("SELECT version();")
    version = cur.fetchone()
    print("Database version:", version[0])
    cur.close()
    conn.close()
except Exception as e:
    print("Error connecting to database:", e)