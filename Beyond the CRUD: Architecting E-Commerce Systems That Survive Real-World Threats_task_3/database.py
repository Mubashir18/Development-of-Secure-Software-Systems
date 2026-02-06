import psycopg2
import psycopg2.extras
from psycopg2 import sql
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import sys
import os
from datetime import datetime
from typing import Optional, List, Tuple, Dict, Any
import logging

class DatabaseManager:
    def __init__(self, log_file: Optional[str] = None):
        self.connection = None
        self.cursor = None
        self.log_file = log_file
        self.setup_logging()
        
    def setup_logging(self):
        """Setup logging to stdout/stderr and file if specified"""
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)
        
        # File handler if log file specified
        if self.log_file:
            file_handler = logging.FileHandler(self.log_file)
            file_handler.setLevel(logging.INFO)
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)
    
    def log_success(self, message: str):
        """Log successful operations"""
        self.logger.info(f"✅ SUCCESS: {message}")
    
    def log_error(self, message: str, error: Optional[Exception] = None):
        """Log errors with user-friendly messages"""
        error_msg = message
        if error:
            # Hide technical details for user-friendly errors
            if "password authentication failed" in str(error):
                error_msg = "Connection failed: Invalid username or password"
            elif "could not connect" in str(error):
                error_msg = "Connection failed: Cannot connect to database server"
            elif "duplicate key" in str(error):
                error_msg = "Operation failed: Record with this value already exists"
            else:
                # Generic error message for security
                error_msg = f"Operation failed: {message}"
        
        self.logger.error(f"❌ ERROR: {error_msg}")
        if error:
            # Log technical details to stderr
            sys.stderr.write(f"Technical details: {str(error)}\n")
    
    def connect(self, host: str, port: str, database: str, 
                username: str, password: str) -> bool:
        """Connect to PostgreSQL database"""
        try:
            self.connection = psycopg2.connect(
                host=host,
                port=port,
                database=database,
                user=username,
                password=password
            )
            self.connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            self.cursor = self.connection.cursor(
                cursor_factory=psycopg2.extras.DictCursor
            )
            self.log_success(f"Connected to database '{database}' as user '{username}'")
            return True
        except Exception as e:
            self.log_error("Failed to connect to database", e)
            return False
    
    def disconnect(self):
        """Disconnect from database"""
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()
            self.log_success("Disconnected from database")
    
    def execute_query(self, query: str, params: Tuple = None) -> Optional[List[Dict]]:
        """Execute a query and return results"""
        try:
            self.cursor.execute(query, params or ())
            if query.strip().upper().startswith(('SELECT', 'SHOW', 'DESC')):
                results = self.cursor.fetchall()
                return [dict(row) for row in results]
            else:
                self.connection.commit()
                return None
        except Exception as e:
            self.log_error("Query execution failed", e)
            return None
    
    def get_table_names(self) -> List[str]:
        """Get list of all tables in the database"""
        try:
            query = """
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                ORDER BY table_name
            """
            tables = self.execute_query(query)
            return [table['table_name'] for table in tables] if tables else []
        except Exception as e:
            self.log_error("Failed to get table names", e)
            return []
    
    def get_table_columns(self, table_name: str) -> List[str]:
        """Get column names for a specific table"""
        try:
            query = """
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_schema = 'public' 
                AND table_name = %s
                ORDER BY ordinal_position
            """
            columns = self.execute_query(query, (table_name,))
            return [col['column_name'] for col in columns] if columns else []
        except Exception as e:
            self.log_error(f"Failed to get columns for table '{table_name}'", e)
            return []
    
    def validate_column_name(self, table_name: str, column_name: str) -> bool:
        """Validate that column exists in table (security measure)"""
        valid_columns = self.get_table_columns(table_name)
        return column_name in valid_columns