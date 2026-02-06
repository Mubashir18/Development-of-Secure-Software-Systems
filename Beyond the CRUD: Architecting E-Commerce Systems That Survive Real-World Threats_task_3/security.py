import psycopg2
from psycopg2 import sql
import re
from typing import List, Tuple, Any

class QueryBuilder:
    """Secure SQL query builder to prevent SQL injection"""
    
    # Whitelist of allowed SQL identifiers (tables and columns)
    VALID_IDENTIFIERS = {
        'categories': ['category_id', 'category_name', 'description', 'created_at'],
        'suppliers': ['supplier_id', 'supplier_name', 'contact_person', 'email', 
                     'phone', 'address', 'created_at'],
        'products': ['product_id', 'product_name', 'category_id', 'supplier_id',
                    'price', 'cost', 'quantity', 'sku', 'description', 
                    'created_at', 'updated_at'],
        'inventory_transactions': ['transaction_id', 'product_id', 'transaction_type',
                                  'quantity_change', 'previous_quantity', 'new_quantity',
                                  'reference', 'notes', 'created_at', 'created_by']
    }
    
    @staticmethod
    def validate_identifier(table: str, column: str = None) -> bool:
        """Validate table and column names against whitelist"""
        if table not in QueryBuilder.VALID_IDENTIFIERS:
            return False
        if column and column not in QueryBuilder.VALID_IDENTIFIERS[table]:
            return False
        return True
    
    @staticmethod
    def build_select_query(table: str, filters: List[Tuple[str, str, Any]] = None) -> sql.Composed:
        """Build SELECT query with parameterized filters"""
        if not QueryBuilder.validate_identifier(table):
            raise ValueError(f"Invalid table name: {table}")
        
        query = sql.SQL("SELECT * FROM {}").format(sql.Identifier(table))
        
        if filters:
            conditions = []
            for col, op, val in filters:
                if not QueryBuilder.validate_identifier(table, col):
                    raise ValueError(f"Invalid column name: {col}")
                
                if op.upper() == 'IN':
                    # Handle IN clause with multiple values
                    placeholders = sql.SQL(', ').join([sql.Placeholder()] * len(val))
                    conditions.append(
                        sql.SQL("{} IN ({})").format(
                            sql.Identifier(col),
                            placeholders
                        )
                    )
                else:
                    conditions.append(
                        sql.SQL("{} {} {}").format(
                            sql.Identifier(col),
                            sql.SQL(op),
                            sql.Placeholder()
                        )
                    )
            
            query = sql.SQL("{} WHERE {}").format(
                query,
                sql.SQL(" AND ").join(conditions)
            )
        
        return query
    
    @staticmethod
    def build_update_query(table: str, set_clauses: List[Tuple[str, Any]], 
                          where_clauses: List[Tuple[str, str, Any]]) -> sql.Composed:
        """Build UPDATE query with parameterized values"""
        if not QueryBuilder.validate_identifier(table):
            raise ValueError(f"Invalid table name: {table}")
        
        # Build SET clause
        set_parts = []
        for col, val in set_clauses:
            if not QueryBuilder.validate_identifier(table, col):
                raise ValueError(f"Invalid column name: {col}")
            set_parts.append(
                sql.SQL("{} = {}").format(
                    sql.Identifier(col),
                    sql.Placeholder()
                )
            )
        
        # Build WHERE clause
        where_parts = []
        for col, op, val in where_clauses:
            if not QueryBuilder.validate_identifier(table, col):
                raise ValueError(f"Invalid column name: {col}")
            
            if op.upper() == 'IN':
                placeholders = sql.SQL(', ').join([sql.Placeholder()] * len(val))
                where_parts.append(
                    sql.SQL("{} IN ({})").format(
                        sql.Identifier(col),
                        placeholders
                    )
                )
            else:
                where_parts.append(
                    sql.SQL("{} {} {}").format(
                        sql.Identifier(col),
                        sql.SQL(op),
                        sql.Placeholder()
                    )
                )
        
        query = sql.SQL("UPDATE {} SET {} WHERE {}").format(
            sql.Identifier(table),
            sql.SQL(", ").join(set_parts),
            sql.SQL(" AND ").join(where_parts)
        )
        
        return query
    
    @staticmethod
    def build_insert_query(table: str, columns: List[str], 
                          values_list: List[List[Any]]) -> sql.Composed:
        """Build INSERT query with parameterized values"""
        if not QueryBuilder.validate_identifier(table):
            raise ValueError(f"Invalid table name: {table}")
        
        # Validate all columns
        for col in columns:
            if not QueryBuilder.validate_identifier(table, col):
                raise ValueError(f"Invalid column name: {col}")
        
        # Build column identifiers
        columns_sql = sql.SQL(', ').join(map(sql.Identifier, columns))
        
        # Build values placeholders
        values_placeholders = []
        for values in values_list:
            placeholders = sql.SQL(', ').join([sql.Placeholder()] * len(values))
            values_placeholders.append(sql.SQL("({})").format(placeholders))
        
        query = sql.SQL("INSERT INTO {} ({}) VALUES {} RETURNING *").format(
            sql.Identifier(table),
            columns_sql,
            sql.SQL(', ').join(values_placeholders)
        )
        
        return query
    
    @staticmethod
    def sanitize_value(value: Any) -> Any:
        """Sanitize input values"""
        if isinstance(value, str):
            # Remove potentially dangerous characters
            value = re.sub(r'[;\'"\\]', '', value)
        return value