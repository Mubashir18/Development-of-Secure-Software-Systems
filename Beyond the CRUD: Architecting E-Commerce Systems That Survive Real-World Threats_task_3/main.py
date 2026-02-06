#!/usr/bin/env python3
"""
E-Commerce Inventory Management System
Database CRUD Operations with Docker Support
"""

import sys
import os
from colorama import init, Fore, Style
from tabulate import tabulate
from getpass import getpass
from typing import Optional

# Initialize colorama for colored output
init(autoreset=True)

# Add app directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import DatabaseManager
from operations import InventoryOperations
from security import QueryBuilder

class InventoryCLI:
    def __init__(self, log_file: Optional[str] = None):
        self.db_manager = DatabaseManager(log_file)
        self.operations = None
        self.current_user = None
        
    def print_header(self):
        """Print application header"""
        print(Fore.CYAN + "=" * 80)
        print(Fore.GREEN + "🛒 E-COMMERCE INVENTORY MANAGEMENT SYSTEM")
        print(Fore.CYAN + "=" * 80)
        print(Fore.YELLOW + "📊 Database CRUD Operations with Docker Support")
        print(Fore.CYAN + "-" * 80)
    
    def print_menu(self):
        """Print main menu"""
        print("\n" + Fore.MAGENTA + "📋 MAIN MENU")
        print(Fore.CYAN + "1.  📤 View Tables")
        print("2.  🔍 Filter Records (Single Value)")
        print("3.  🔎 Filter Records (Multiple Values)")
        print("4.  ✏️  Update Single Record")
        print("5.  📝 Update Multiple Records")
        print("6.  ➕ Insert Single Record")
        print("7.  🔗 Insert Related Records")
        print("8.  🗃️  Insert Multiple Records")
        print("9.  📋 Show Database Schema")
        print("10. 🔄 Switch User")
        print("0.  🚪 Exit")
        print(Fore.CYAN + "-" * 80)
    
    def get_database_credentials(self):
        """Get database credentials from user"""
        print(Fore.YELLOW + "\n🔐 DATABASE CONNECTION")
        print(Fore.CYAN + "-" * 40)
        
        # Get credentials from user
        host = input("Host [localhost]: ").strip() or "localhost"
        port = input("Port [5432]: ").strip() or "5432"
        database = input("Database [ecommerce_db]: ").strip() or "ecommerce_db"
        username = input("Username: ").strip()
        password = getpass("Password: ").strip()
        
        return host, port, database, username, password
    
    def connect_to_database(self):
        """Connect to database with user credentials"""
        host, port, database, username, password = self.get_database_credentials()
        
        if self.db_manager.connect(host, port, database, username, password):
            self.operations = InventoryOperations(self.db_manager)
            self.current_user = username
            print(Fore.GREEN + f"\n✅ Connected as user: {username}")
            return True
        return False
    
    def show_database_schema(self):
        """Display database schema and table information"""
        tables = self.db_manager.get_table_names()
        
        print(Fore.CYAN + "\n📊 DATABASE SCHEMA")
        print("-" * 60)
        
        for table in tables:
            columns = self.db_manager.get_table_columns(table)
            print(Fore.YELLOW + f"\n📋 Table: {table}")
            print(Fore.WHITE + f"Columns: {', '.join(columns)}")
            
            # Show sample data
            query = f"SELECT * FROM {table} LIMIT 3"
            results = self.db_manager.execute_query(query)
            if results:
                print(Fore.GREEN + f"Sample data (first 3 rows):")
                print(tabulate(results, headers="keys", tablefmt="simple"))
    
    def view_tables_menu(self):
        """Menu for viewing tables"""
        tables = self.db_manager.get_table_names()
        
        print(Fore.CYAN + "\n📤 VIEW TABLES")
        print("-" * 40)
        
        for i, table in enumerate(tables, 1):
            print(f"{i}. {table}")
        print("0. Back to Main Menu")
        
        choice = input("\nSelect table to view: ").strip()
        
        if choice == '0':
            return
        
        try:
            table_idx = int(choice) - 1
            if 0 <= table_idx < len(tables):
                self.operations.display_table(tables[table_idx])
            else:
                print(Fore.RED + "Invalid selection")
        except ValueError:
            print(Fore.RED + "Please enter a valid number")
    
    def filter_single_value_menu(self):
        """Menu for single value filtering"""
        tables = self.db_manager.get_table_names()
        
        print(Fore.CYAN + "\n🔍 FILTER BY SINGLE VALUE")
        print("-" * 40)
        
        # Select table
        for i, table in enumerate(tables, 1):
            print(f"{i}. {table}")
        
        table_choice = input("\nSelect table: ").strip()
        
        try:
            table_idx = int(table_choice) - 1
            if not (0 <= table_idx < len(tables)):
                print(Fore.RED + "Invalid table selection")
                return
            
            table_name = tables[table_idx]
            columns = self.db_manager.get_table_columns(table_name)
            
            # Show columns
            print(Fore.YELLOW + f"\nAvailable columns for '{table_name}':")
            for i, col in enumerate(columns, 1):
                print(f"{i}. {col}")
            
            col_choice = input("\nSelect column to filter by: ").strip()
            col_idx = int(col_choice) - 1
            
            if not (0 <= col_idx < len(columns)):
                print(Fore.RED + "Invalid column selection")
                return
            
            column_name = columns[col_idx]
            value = input(f"Enter value for {column_name}: ").strip()
            
            # Convert numeric values
            if column_name.endswith('_id') or column_name in ['quantity', 'price', 'cost']:
                try:
                    if '.' in value:
                        value = float(value)
                    else:
                        value = int(value)
                except ValueError:
                    pass
            
            self.operations.filter_single_value(table_name, column_name, value)
            
        except ValueError:
            print(Fore.RED + "Please enter valid numbers")
    
    def filter_multiple_values_menu(self):
        """Menu for multiple values filtering"""
        tables = self.db_manager.get_table_names()
        
        print(Fore.CYAN + "\n🔎 FILTER BY MULTIPLE VALUES")
        print("-" * 40)
        
        # Select table
        for i, table in enumerate(tables, 1):
            print(f"{i}. {table}")
        
        table_choice = input("\nSelect table: ").strip()
        
        try:
            table_idx = int(table_choice) - 1
            if not (0 <= table_idx < len(tables)):
                print(Fore.RED + "Invalid table selection")
                return
            
            table_name = tables[table_idx]
            columns = self.db_manager.get_table_columns(table_name)
            
            filters = []
            print(Fore.YELLOW + "\nEnter filter conditions (enter empty when done):")
            
            while True:
                # Show columns
                print(Fore.WHITE + "\nAvailable columns:")
                for i, col in enumerate(columns, 1):
                    print(f"{i}. {col}")
                
                col_choice = input("\nSelect column (or press Enter to finish): ").strip()
                if not col_choice:
                    break
                
                col_idx = int(col_choice) - 1
                if not (0 <= col_idx < len(columns)):
                    print(Fore.RED + "Invalid column selection")
                    continue
                
                column_name = columns[col_idx]
                
                print(Fore.WHITE + "\nAvailable operators: =, !=, >, <, >=, <=, LIKE, IN")
                operator = input("Enter operator: ").strip().upper()
                
                if operator == 'IN':
                    values = input("Enter comma-separated values: ").strip().split(',')
                    values = [v.strip() for v in values]
                    
                    # Convert numeric values
                    if column_name.endswith('_id') or column_name in ['quantity', 'price', 'cost']:
                        converted_values = []
                        for v in values:
                            try:
                                if '.' in v:
                                    converted_values.append(float(v))
                                else:
                                    converted_values.append(int(v))
                            except ValueError:
                                converted_values.append(v)
                        values = converted_values
                    
                    filters.append((column_name, operator, values))
                else:
                    value = input(f"Enter value for {column_name}: ").strip()
                    
                    # Convert numeric values
                    if column_name.endswith('_id') or column_name in ['quantity', 'price', 'cost']:
                        try:
                            if '.' in value:
                                value = float(value)
                            else:
                                value = int(value)
                        except ValueError:
                            pass
                    
                    filters.append((column_name, operator, value))
            
            if filters:
                self.operations.filter_multiple_values(table_name, filters)
            else:
                print(Fore.YELLOW + "No filters specified")
                
        except ValueError:
            print(Fore.RED + "Please enter valid numbers")
    
    def update_single_record_menu(self):
        """Menu for updating single record"""
        tables = self.db_manager.get_table_names()
        
        print(Fore.CYAN + "\n✏️ UPDATE SINGLE RECORD")
        print("-" * 40)
        
        # Select table
        for i, table in enumerate(tables, 1):
            print(f"{i}. {table}")
        
        table_choice = input("\nSelect table: ").strip()
        
        try:
            table_idx = int(table_choice) - 1
            if not (0 <= table_idx < len(tables)):
                print(Fore.RED + "Invalid table selection")
                return
            
            table_name = tables[table_idx]
            columns = self.db_manager.get_table_columns(table_name)
            
            # Get record ID
            id_column = f"{table_name[:-1]}_id" if table_name.endswith('s') else f"{table_name}_id"
            record_id = input(f"\nEnter {id_column} to update: ").strip()
            
            # Convert to appropriate type
            try:
                record_id = int(record_id)
            except ValueError:
                print(Fore.RED + f"{id_column} must be a number")
                return
            
            # Show current record
            print(Fore.YELLOW + f"\nCurrent record (ID: {record_id}):")
            self.operations.filter_single_value(table_name, id_column, record_id)
            
            # Get updates
            updates = {}
            print(Fore.YELLOW + "\nEnter fields to update (enter empty when done):")
            
            # Remove ID column from updatable columns
            updatable_columns = [col for col in columns if col != id_column]
            
            while True:
                print(Fore.WHITE + "\nAvailable columns:")
                for i, col in enumerate(updatable_columns, 1):
                    print(f"{i}. {col}")
                
                col_choice = input("\nSelect column to update (or press Enter to finish): ").strip()
                if not col_choice:
                    break
                
                col_idx = int(col_choice) - 1
                if not (0 <= col_idx < len(updatable_columns)):
                    print(Fore.RED + "Invalid column selection")
                    continue
                
                column_name = updatable_columns[col_idx]
                new_value = input(f"Enter new value for {column_name}: ").strip()
                
                # Convert numeric values
                if column_name.endswith('_id') or column_name in ['quantity', 'price', 'cost']:
                    try:
                        if '.' in new_value:
                            new_value = float(new_value)
                        else:
                            new_value = int(new_value)
                    except ValueError:
                        pass
                
                updates[column_name] = new_value
            
            if updates:
                self.operations.update_single_record(table_name, record_id, updates)
            else:
                print(Fore.YELLOW + "No updates specified")
                
        except ValueError:
            print(Fore.RED + "Please enter valid numbers")
    
    def run(self):
        """Main application loop"""
        self.print_header()
        
        # Connect to database
        if not self.connect_to_database():
            print(Fore.RED + "\n❌ Failed to connect to database. Exiting...")
            return
        
        while True:
            self.print_menu()
            choice = input(Fore.GREEN + "\nEnter your choice: ").strip()
            
            if choice == '0':
                print(Fore.YELLOW + "\n👋 Goodbye!")
                break
            
            elif choice == '1':
                self.view_tables_menu()
            
            elif choice == '2':
                self.filter_single_value_menu()
            
            elif choice == '3':
                self.filter_multiple_values_menu()
            
            elif choice == '4':
                self.update_single_record_menu()
            
            elif choice == '5':
                self.update_multiple_records_menu()
            
            elif choice == '6':
                self.insert_single_record_menu()
            
            elif choice == '7':
                self.insert_related_records_menu()
            
            elif choice == '8':
                self.insert_multiple_records_menu()
            
            elif choice == '9':
                self.show_database_schema()
            
            elif choice == '10':
                self.switch_user_menu()
            
            else:
                print(Fore.RED + "Invalid choice. Please try again.")
            
            input(Fore.CYAN + "\nPress Enter to continue...")
        
        self.db_manager.disconnect()
    
    def update_multiple_records_menu(self):
        """Menu for updating multiple records"""
        tables = self.db_manager.get_table_names()
        
        print(Fore.CYAN + "\n📝 UPDATE MULTIPLE RECORDS")
        print("-" * 40)
        
        # Select table
        for i, table in enumerate(tables, 1):
            print(f"{i}. {table}")
        
        table_choice = input("\nSelect table: ").strip()
        
        try:
            table_idx = int(table_choice) - 1
            if not (0 <= table_idx < len(tables)):
                print(Fore.RED + "Invalid table selection")
                return
            
            table_name = tables[table_idx]
            columns = self.db_manager.get_table_columns(table_name)
            
            # Select filter column
            print(Fore.YELLOW + "\nSelect column to filter by:")
            for i, col in enumerate(columns, 1):
                print(f"{i}. {col}")
            
            filter_col_choice = input("\nSelect filter column: ").strip()
            filter_col_idx = int(filter_col_choice) - 1
            
            if not (0 <= filter_col_idx < len(columns)):
                print(Fore.RED + "Invalid column selection")
                return
            
            filter_column = columns[filter_col_idx]
            
            # Get filter values
            values_input = input(f"Enter comma-separated values for {filter_column}: ").strip()
            filter_values = [v.strip() for v in values_input.split(',')]
            
            # Convert numeric values
            if filter_column.endswith('_id') or filter_column in ['quantity', 'price', 'cost']:
                converted_values = []
                for v in filter_values:
                    try:
                        if '.' in v:
                            converted_values.append(float(v))
                        else:
                            converted_values.append(int(v))
                    except ValueError:
                        converted_values.append(v)
                filter_values = converted_values
            
            # Select update column
            print(Fore.YELLOW + "\nSelect column to update:")
            updatable_columns = [col for col in columns if not col.endswith('_id')]
            for i, col in enumerate(updatable_columns, 1):
                print(f"{i}. {col}")
            
            update_col_choice = input("\nSelect column to update: ").strip()
            update_col_idx = int(update_col_choice) - 1
            
            if not (0 <= update_col_idx < len(updatable_columns)):
                print(Fore.RED + "Invalid column selection")
                return
            
            update_column = updatable_columns[update_col_idx]
            
            # Get new value
            new_value = input(f"Enter new value for {update_column}: ").strip()
            
            # Convert numeric value
            if update_column in ['quantity', 'price', 'cost']:
                try:
                    if '.' in new_value:
                        new_value = float(new_value)
                    else:
                        new_value = int(new_value)
                except ValueError:
                    pass
            
            self.operations.update_multiple_records(
                table_name, filter_column, filter_values,
                update_column, new_value
            )
            
        except ValueError:
            print(Fore.RED + "Please enter valid numbers")
    
    def insert_single_record_menu(self):
        """Menu for inserting single record"""
        tables = self.db_manager.get_table_names()
        
        print(Fore.CYAN + "\n➕ INSERT SINGLE RECORD")
        print("-" * 40)
        
        # Select table
        for i, table in enumerate(tables, 1):
            print(f"{i}. {table}")
        
        table_choice = input("\nSelect table: ").strip()
        
        try:
            table_idx = int(table_choice) - 1
            if not (0 <= table_idx < len(tables)):
                print(Fore.RED + "Invalid table selection")
                return
            
            table_name = tables[table_idx]
            columns = self.db_manager.get_table_columns(table_name)
            
            # Remove auto-generated columns
            insertable_columns = [
                col for col in columns 
                if col not in ['created_at', 'updated_at'] and 
                   not col.endswith('_id')  # Don't ask for IDs (auto-generated)
            ]
            
            print(Fore.YELLOW + f"\nInserting into '{table_name}'")
            data = {}
            
            for col in insertable_columns:
                value = input(f"Enter value for {col}: ").strip()
                
                # Convert numeric values
                if col in ['quantity', 'price', 'cost']:
                    try:
                        if '.' in value:
                            value = float(value)
                        else:
                            value = int(value)
                    except ValueError:
                        pass
                
                data[col] = value
            
            self.operations.insert_single_record(table_name, data)
            
        except ValueError:
            print(Fore.RED + "Please enter valid numbers")
    
    def insert_related_records_menu(self):
        """Menu for inserting related records"""
        print(Fore.CYAN + "\n🔗 INSERT RELATED RECORDS")
        print("-" * 40)
        print(Fore.YELLOW + "Example: Insert product and its inventory transaction")
        
        # Example: Insert product and transaction
        print(Fore.WHITE + "\nExample data for 'products' table:")
        product_data = {
            'product_name': 'Test Product',
            'category_id': 1,
            'supplier_id': 1,
            'price': 99.99,
            'cost': 60.00,
            'quantity': 100,
            'sku': 'TEST-001',
            'description': 'Test product for demonstration'
        }
        print(product_data)
        
        print(Fore.WHITE + "\nExample data for 'inventory_transactions' table:")
        transaction_data = {
            'product_id': 0,  # Will be replaced with actual product_id
            'transaction_type': 'PURCHASE',
            'quantity_change': 100,
            'previous_quantity': 0,
            'new_quantity': 100,
            'reference': 'TEST-001',
            'notes': 'Initial stock',
            'created_by': self.current_user
        }
        print(transaction_data)
        
        confirm = input(Fore.YELLOW + "\nInsert example data? (y/n): ").strip().lower()
        
        if confirm == 'y':
            tables_data = [
                ('products', product_data, 'product_id'),
                ('inventory_transactions', transaction_data, 'transaction_id')
            ]
            
            result = self.operations.insert_related_records(tables_data)
            if result:
                print(Fore.GREEN + f"\n✅ Inserted records with IDs: {result}")
    
    def insert_multiple_records_menu(self):
        """Menu for inserting multiple records"""
        tables = self.db_manager.get_table_names()
        
        print(Fore.CYAN + "\n🗃️ INSERT MULTIPLE RECORDS")
        print("-" * 40)
        
        # Select table
        for i, table in enumerate(tables, 1):
            print(f"{i}. {table}")
        
        table_choice = input("\nSelect table: ").strip()
        
        try:
            table_idx = int(table_choice) - 1
            if not (0 <= table_idx < len(tables)):
                print(Fore.RED + "Invalid table selection")
                return
            
            table_name = tables[table_idx]
            columns = self.db_manager.get_table_columns(table_name)
            
            # Remove auto-generated columns
            insertable_columns = [
                col for col in columns 
                if col not in ['created_at', 'updated_at'] and 
                   not col.endswith('_id')  # Don't ask for IDs (auto-generated)
            ]
            
            print(Fore.YELLOW + f"\nInserting multiple records into '{table_name}'")
            print(Fore.WHITE + f"Available columns: {', '.join(insertable_columns)}")
            
            records = []
            record_count = input("\nHow many records to insert? ").strip()
            
            try:
                count = int(record_count)
                if count <= 0:
                    print(Fore.RED + "Please enter a positive number")
                    return
                
                for i in range(count):
                    print(Fore.CYAN + f"\n--- Record {i+1} ---")
                    data = {}
                    
                    for col in insertable_columns:
                        value = input(f"Enter value for {col}: ").strip()
                        
                        # Convert numeric values
                        if col in ['quantity', 'price', 'cost']:
                            try:
                                if '.' in value:
                                    value = float(value)
                                else:
                                    value = int(value)
                            except ValueError:
                                pass
                        
                        data[col] = value
                    
                    records.append(data)
                
                if records:
                    self.operations.insert_multiple_records(table_name, records)
                
            except ValueError:
                print(Fore.RED + "Please enter a valid number")
            
        except ValueError:
            print(Fore.RED + "Please enter valid numbers")
    
    def switch_user_menu(self):
        """Menu for switching database user"""
        print(Fore.CYAN + "\n🔄 SWITCH USER")
        print("-" * 40)
        
        print(Fore.YELLOW + "Available users:")
        print("1. app_user (Read/Write access)")
        print("2. report_user (Read-only access)")
        print("3. inventory_admin (Full access)")
        print("4. Custom user")
        
        choice = input("\nSelect user type: ").strip()
        
        if choice == '1':
            username = 'app_user'
            password = 'app_password123'
        elif choice == '2':
            username = 'report_user'
            password = 'report_pass456'
        elif choice == '3':
            username = 'inventory_admin'
            password = 'admin_pass789'
        elif choice == '4':
            username = input("Enter username: ").strip()
            password = getpass("Enter password: ").strip()
        else:
            print(Fore.RED + "Invalid choice")
            return
        
        # Disconnect and reconnect with new credentials
        self.db_manager.disconnect()
        
        # Get current connection details
        host = "localhost"  # Default for Docker
        port = "5432"
        database = "ecommerce_db"
        
        if self.db_manager.connect(host, port, database, username, password):
            self.operations = InventoryOperations(self.db_manager)
            self.current_user = username
            print(Fore.GREEN + f"\n✅ Switched to user: {username}")
        else:
            print(Fore.RED + "\n❌ Failed to switch user")


def main():
    """Main entry point"""
    # Check if log file path is provided via environment variable
    log_file = os.getenv('APP_LOG_FILE')
    
    if log_file:
        print(f"📝 Logging to file: {log_file}")
    
    try:
        cli = InventoryCLI(log_file)
        cli.run()
    except KeyboardInterrupt:
        print(Fore.YELLOW + "\n\n👋 Interrupted by user. Goodbye!")
    except Exception as e:
        print(Fore.RED + f"\n❌ Unexpected error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()