import os
import time
import psycopg2
from psycopg2 import OperationalError
from datetime import datetime

def log_message(message, stream="stdout"):
    """Print message to stdout/stderr and optionally write to log file."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    formatted_message = f"[{timestamp}] {message}"
    
    if stream == "stdout":
        print(formatted_message)
    else:
        print(formatted_message, file=os.sys.stderr)
    
    log_file = os.getenv("LOG_FILE")
    if log_file:
        try:
            with open(log_file, "a") as f:
                f.write(formatted_message + "\n")
        except Exception as e:
            print(f"[{timestamp}] Could not write to log file: {e}", file=os.sys.stderr)

def check_database():
    """Try connecting to database and run SELECT version()."""
    conn_params = {
        "host": os.getenv("DB_HOST", "localhost"),
        "port": int(os.getenv("DB_PORT", 5432)),  # FIXED: Convert to int
        "dbname": os.getenv("DB_NAME", "mydb"),
        "user": os.getenv("DB_USER"),
        "password": os.getenv("DB_PASSWORD"),
    }

    try:
        conn = psycopg2.connect(**conn_params)
        cur = conn.cursor()
        cur.execute("SELECT version();")
        version = cur.fetchone()[0]
        conn.close()

        # Parse PostgreSQL version number
        if "PostgreSQL" in version:
            try:
                # Extract major version number
                version_str = version.split("PostgreSQL")[1]
                major_version = int(version_str.split(".")[0].strip().split()[0])
                if major_version in (16, 17):
                    log_message(f"OK — Connected successfully. Version: {version}", "stdout")
                else:
                    log_message(f"WARNING — Atypical PostgreSQL version detected: {version}", "stdout")
            except (ValueError, IndexError):
                # Cannot parse version number
                log_message(f"WARNING — Unexpected version format: {version}", "stdout")
        else:
            # Not a standard PostgreSQL version response
            log_message(f"WARNING — Non-standard response: {version}", "stdout")

    except OperationalError as e:
        log_message(f"ERROR — Connection failed: {e}", "stderr")
    except Exception as e:
        log_message(f"ERROR — Unexpected error: {e}", "stderr")

def main():
    """Main loop that runs every PING_INTERVAL seconds."""
    try:
        interval = int(os.getenv("PING_INTERVAL", 20))  # default: 5 minutes
    except ValueError:
        log_message("ERROR — Invalid PING_INTERVAL value, using default 20 seconds", "stderr")
        interval = 20
    
    log_message(f"Starting pinger — interval {interval} seconds.", "stdout")

    while True:
        check_database()
        time.sleep(interval)

if __name__ == "__main__":
    main()