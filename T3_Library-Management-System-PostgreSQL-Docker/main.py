import psycopg2
import os
import sys
import logging

# Setup logging
log_file = os.getenv('LOG_FILE')
handlers = [logging.StreamHandler(sys.stdout)]

if log_file:
    log_dir = os.path.dirname(log_file)
    if log_dir and not os.path.exists(log_dir):
        try:
            os.makedirs(log_dir, exist_ok=True)
            handlers.append(logging.FileHandler(log_file))
        except:
            pass

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=handlers
)

logger = logging.getLogger(__name__)


class DatabaseApp:
    def __init__(self):
        self.conn = None
        self.tables = ['authors', 'books', 'members', 'borrowings']
        self.table_columns = {
            'authors': ['id', 'name', 'country'],
            'books': ['id', 'title', 'author_id', 'isbn', 'publication_year'],
            'members': ['id', 'name', 'email', 'join_date'],
            'borrowings': ['id', 'book_id', 'member_id', 'borrow_date', 'return_date']
        }
        self.connect()
    
    def connect(self):
        """Connect to database"""
        try:
            self.conn = psycopg2.connect(
                host=os.getenv('DB_HOST', 'localhost'),
                database=os.getenv('DB_NAME', 'library_db'),
                user=os.getenv('DB_USER', 'postgres'),
                password=os.getenv('DB_PASSWORD', 'postgres'),
                port=os.getenv('DB_PORT', 5432)
            )
            logger.info("Connected to database successfully")
            print("✓ Connected to database")
        except Exception as e:
            logger.error(f"Connection failed: {str(e)}")
            print("✗ Cannot connect to database")
            sys.exit(1)
    
    def view_all(self):
        """Option 1: View all records from table"""
        print(f"\nAvailable tables: {', '.join(self.tables)}")
        table = input("Enter table name: ").strip().lower()
        
        if table not in self.tables:
            print("✗ Invalid table name!")
            return
        
        try:
            cursor = self.conn.cursor()
            cursor.execute(f"SELECT * FROM {table}")
            rows = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description]
            cursor.close()
            
            if not rows:
                print(f"→ No records in {table}")
                return
            
            # Print header
            print(f"\n{'|'.join(columns)}")
            print("-" * 80)
            
            # Print rows
            for row in rows:
                print("|".join(str(val) for val in row))
            
            logger.info(f"Viewed {len(rows)} records from {table}")
        except Exception as e:
            print(f"✗ Error: {str(e)}")
            logger.error(f"View error: {str(e)}")
    
    def view_filter_single(self):
        """Option 2: View with single-value filter"""
        print(f"\nAvailable tables: {', '.join(self.tables)}")
        table = input("Enter table name: ").strip().lower()
        
        if table not in self.tables:
            print("✗ Invalid table!")
            return
        
        print(f"Available columns: {', '.join(self.table_columns[table])}")
        column = input("Enter column name: ").strip().lower()
        value = input("Enter filter value: ").strip()
        
        try:
            cursor = self.conn.cursor()
            query = f"SELECT * FROM {table} WHERE {column} = %s"
            cursor.execute(query, (value,))
            rows = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description]
            cursor.close()
            
            if not rows:
                print("→ No records found")
                return
            
            print(f"\n{'|'.join(columns)}")
            print("-" * 80)
            for row in rows:
                print("|".join(str(val) for val in row))
            
            logger.info(f"Filtered {table}: {column}={value}")
        except Exception as e:
            print(f"✗ Error: {str(e)}")
            logger.error(f"Filter error: {str(e)}")
    
    def update_record(self):
        """Option 3: Update existing record"""
        print(f"\nAvailable tables: {', '.join(self.tables)}")
        table = input("Enter table name: ").strip().lower()
        
        if table not in self.tables:
            print("✗ Invalid table!")
            return
        
        columns = self.table_columns[table]
        print(f"\nAvailable columns: {', '.join(columns)}")
        
        record_id = input("Enter record ID to update: ").strip()
        
        # Collect updates
        updates = {}
        print("Enter column and new value (press Enter twice to finish):")
        
        while True:
            col = input("Column name: ").strip().lower()
            if not col:
                break
            
            if col == 'id':
                print("→ Cannot update ID field")
                continue
            
            if col not in columns:
                print(f"→ Invalid column! Options: {', '.join(columns)}")
                continue
            
            val = input(f"New value for {col}: ").strip()
            updates[col] = val
        
        if not updates:
            print("✗ No updates provided")
            return
        
        try:
            cursor = self.conn.cursor()
            
            # Build UPDATE query
            set_parts = []
            values = []
            for col, val in updates.items():
                set_parts.append(f"{col} = %s")
                values.append(val)
            values.append(record_id)
            
            set_clause = ", ".join(set_parts)
            query = f"UPDATE {table} SET {set_clause} WHERE id = %s"
            
            cursor.execute(query, tuple(values))
            self.conn.commit()
            cursor.close()
            
            print("✓ Record updated successfully!")
            logger.info(f"Updated {table}: id={record_id}")
        except Exception as e:
            self.conn.rollback()
            print(f"✗ Error: {str(e)}")
            logger.error(f"Update error: {str(e)}")
    
    def insert_record(self):
        """Option 4: Insert new record"""
        print(f"\nAvailable tables: {', '.join(self.tables)}")
        table = input("Enter table name: ").strip().lower()
        
        if table not in self.tables:
            print("✗ Invalid table!")
            return
        
        columns = self.table_columns[table]
        print(f"\nAvailable columns: {', '.join(columns)}")
        print("(Skip 'id', it's auto-generated)\n")
        
        # Collect data
        data = {}
        print("Enter column and value (press Enter twice to finish):")
        
        while True:
            col = input("Column name: ").strip().lower()
            if not col:
                break
            
            if col == 'id':
                print("→ ID is auto-generated, skip it")
                continue
            
            if col not in columns:
                print(f"→ Invalid column! Options: {', '.join(columns)}")
                continue
            
            val = input(f"Value for {col}: ").strip()
            data[col] = val
        
        if not data:
            print("✗ No data provided")
            return
        
        try:
            cursor = self.conn.cursor()
            
            # Build INSERT query
            col_names = ", ".join(data.keys())
            placeholders = ", ".join(["%s"] * len(data))
            values = list(data.values())
            
            query = f"INSERT INTO {table} ({col_names}) VALUES ({placeholders})"
            
            cursor.execute(query, tuple(values))
            self.conn.commit()
            cursor.close()
            
            print("✓ Record inserted successfully!")
            logger.info(f"Inserted into {table}: {data}")
        except Exception as e:
            self.conn.rollback()
            print(f"✗ Error: {str(e)}")
            logger.error(f"Insert error: {str(e)}")
    
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
            logger.info("Database connection closed")
    
    def run(self):
        """Main menu loop"""
        while True:
            print("\n" + "=" * 60)
            print("LIBRARY MANAGEMENT SYSTEM")
            print("=" * 60)
            print("1. View all records")
            print("2. View with single filter")
            print("3. Update record")
            print("4. Insert record")
            print("5. Exit")
            print("=" * 60)
            
            choice = input("Enter your choice (1-5): ").strip()
            
            if choice == '1':
                self.view_all()
            elif choice == '2':
                self.view_filter_single()
            elif choice == '3':
                self.update_record()
            elif choice == '4':
                self.insert_record()
            elif choice == '5':
                print("\n👋 Exiting application...")
                logger.info("Application closed")
                break
            else:
                print("✗ Invalid choice. Try again.")


if __name__ == '__main__':
    app = DatabaseApp()
    try:
        app.run()
    except KeyboardInterrupt:
        print("\n\n✗ Application interrupted")
        logger.info("Interrupted by user")
    finally:
        app.close()
