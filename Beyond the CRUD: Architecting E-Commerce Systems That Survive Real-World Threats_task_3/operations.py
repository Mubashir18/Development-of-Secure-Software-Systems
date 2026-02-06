import psycopg2
from psycopg2 import sql
from typing import List, Dict, Any, Optional, Tuple
from tabulate import tabulate
from security import QueryBuilder
from database import DatabaseManager

class InventoryOperations:
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
    
    def display_table(self, table_name: str):
        """Display all records from a table"""
        try:
            query = QueryBuilder.build_select_query(table_name)
            results = self.db.execute_query(query.as_string(self.db.cursor))
            
            if results:
                print(f"\n📊 Table: {table_name.upper()}")
                print("-" * 80)
                print(tabulate(results, headers="keys", tablefmt="grid"))
                print(f"Total records: {len(results)}")
            else:
                print(f"No records found in table '{table_name}'")
                
        except Exception as e:
            print(f"Error displaying table: {str(e)}")
    
    def filter_single_value(self, table_name: str, column_name: str, value: Any):
        """Filter records by single column value"""
        try:
            if not QueryBuilder.validate_identifier(table_name, column_name):
                print(f"Error: Invalid column '{column_name}' for table '{table_name}'")
                return
            
            query = QueryBuilder.build_select_query(
                table_name, 
                [(column_name, '=', value)]
            )
            
            results = self.db.execute_query(
                query.as_string(self.db.cursor), 
                (QueryBuilder.sanitize_value(value),)
            )
            
            if results:
                print(f"\n🔍 Filtered Results ({column_name} = {value})")
                print("-" * 80)
                print(tabulate(results, headers="keys", tablefmt="grid"))
                print(f"Found: {len(results)} records")
            else:
                print(f"No records found with {column_name} = {value}")
                
        except Exception as e:
            print(f"Error filtering data: {str(e)}")
    
    def filter_multiple_values(self, table_name: str, filters: List[Tuple[str, str, Any]]):
        """Filter records by multiple conditions"""
        try:
            # Validate all filters
            for col, op, val in filters:
                if not QueryBuilder.validate_identifier(table_name, col):
                    print(f"Error: Invalid column '{col}' for table '{table_name}'")
                    return
            
            query = QueryBuilder.build_select_query(table_name, filters)
            
            # Prepare parameters
            params = []
            for col, op, val in filters:
                if op.upper() == 'IN':
                    params.extend([QueryBuilder.sanitize_value(v) for v in val])
                else:
                    params.append(QueryBuilder.sanitize_value(val))
            
            results = self.db.execute_query(query.as_string(self.db.cursor), tuple(params))
            
            if results:
                print(f"\n🔍 Filtered Results (Multiple Conditions)")
                print("-" * 80)
                print(tabulate(results, headers="keys", tablefmt="grid"))
                print(f"Found: {len(results)} records")
            else:
                print("No records found matching all conditions")
                
        except Exception as e:
            print(f"Error filtering data: {str(e)}")
    
    def update_single_record(self, table_name: str, record_id: int, 
                           updates: Dict[str, Any]):
        """Update single record by ID"""
        try:
            # Don't allow updating ID columns
            if 'id' in updates or f'{table_name[:-1]}_id' in updates:
                print("Error: Cannot update ID columns")
                return
            
            # Validate columns
            for col in updates.keys():
                if not QueryBuilder.validate_identifier(table_name, col):
                    print(f"Error: Invalid column '{col}' for table '{table_name}'")
                    return
            
            # Prepare SET clause
            set_clauses = [(col, val) for col, val in updates.items()]
            
            # Prepare WHERE clause (always use primary key)
            id_column = f"{table_name[:-1]}_id" if table_name.endswith('s') else f"{table_name}_id"
            where_clauses = [(id_column, '=', record_id)]
            
            query = QueryBuilder.build_update_query(table_name, set_clauses, where_clauses)
            
            # Prepare parameters (SET values first, then WHERE values)
            params = [QueryBuilder.sanitize_value(val) for col, val in updates.items()]
            params.append(QueryBuilder.sanitize_value(record_id))
            
            result = self.db.execute_query(query.as_string(self.db.cursor), tuple(params))
            
            if self.db.cursor.rowcount > 0:
                print(f"✅ Successfully updated record with {id_column} = {record_id}")
                print(f"Rows affected: {self.db.cursor.rowcount}")
            else:
                print(f"No record found with {id_column} = {record_id}")
                
        except Exception as e:
            print(f"Error updating record: {str(e)}")
    
    def update_multiple_records(self, table_name: str, 
                              filter_column: str, filter_values: List[Any],
                              update_column: str, new_value: Any):
        """Update multiple records with common value"""
        try:
            # Validate columns
            if not QueryBuilder.validate_identifier(table_name, filter_column):
                print(f"Error: Invalid filter column '{filter_column}'")
                return
            if not QueryBuilder.validate_identifier(table_name, update_column):
                print(f"Error: Invalid update column '{update_column}'")
                return
            
            # Don't allow updating ID columns
            if update_column.endswith('_id'):
                print("Error: Cannot update ID columns")
                return
            
            set_clauses = [(update_column, new_value)]
            where_clauses = [(filter_column, 'IN', filter_values)]
            
            query = QueryBuilder.build_update_query(table_name, set_clauses, where_clauses)
            
            # Prepare parameters
            params = [QueryBuilder.sanitize_value(new_value)]
            params.extend([QueryBuilder.sanitize_value(v) for v in filter_values])
            
            result = self.db.execute_query(query.as_string(self.db.cursor), tuple(params))
            
            print(f"✅ Successfully updated {self.db.cursor.rowcount} records")
            print(f"Set '{update_column}' = '{new_value}' for records where '{filter_column}' IN {filter_values}")
            
        except Exception as e:
            print(f"Error updating records: {str(e)}")
    
    def insert_single_record(self, table_name: str, data: Dict[str, Any]):
        """Insert single record into table"""
        try:
            columns = list(data.keys())
            values = list(data.values())
            
            # Validate columns
            for col in columns:
                if not QueryBuilder.validate_identifier(table_name, col):
                    print(f"Error: Invalid column '{col}' for table '{table_name}'")
                    return
            
            query = QueryBuilder.build_insert_query(table_name, columns, [values])
            
            # Sanitize values
            sanitized_values = [QueryBuilder.sanitize_value(v) for v in values]
            
            result = self.db.execute_query(query.as_string(self.db.cursor), tuple(sanitized_values))
            
            if result:
                print(f"✅ Successfully inserted record into '{table_name}'")
                print(f"Inserted data: {data}")
                return result[0]  # Return the inserted record with generated ID
            
        except Exception as e:
            print(f"Error inserting record: {str(e)}")
            return None
    
    def insert_related_records(self, tables_data: List[Tuple[str, Dict[str, Any], str]]):
        """Insert records into multiple related tables"""
        try:
            inserted_ids = []
            
            for i, (table_name, data, id_column) in enumerate(tables_data):
                # If this is not the first table, we might need to use previous ID
                if i > 0 and id_column:
                    # Find foreign key column that references previous table
                    for col in data.keys():
                        if col.endswith('_id'):
                            # Use the ID from previous insertion
                            prev_table = tables_data[i-1][0]
                            if col == f"{prev_table[:-1]}_id":
                                data[col] = inserted_ids[-1]
                
                result = self.insert_single_record(table_name, data)
                if result and id_column:
                    inserted_ids.append(result[id_column])
                elif result:
                    # If no specific ID column, try common ones
                    for key in result.keys():
                        if key.endswith('_id'):
                            inserted_ids.append(result[key])
                            break
            
            print(f"✅ Successfully inserted related records across {len(tables_data)} tables")
            return inserted_ids
            
        except Exception as e:
            print(f"Error inserting related records: {str(e)}")
            return None
    
    def insert_multiple_records(self, table_name: str, records: List[Dict[str, Any]]):
        """Insert multiple records into single table"""
        try:
            if not records:
                print("No records to insert")
                return
            
            # Get columns from first record
            columns = list(records[0].keys())
            
            # Validate all records have same columns
            for record in records:
                if set(record.keys()) != set(columns):
                    print("Error: All records must have the same columns")
                    return
            
            # Validate columns
            for col in columns:
                if not QueryBuilder.validate_identifier(table_name, col):
                    print(f"Error: Invalid column '{col}' for table '{table_name}'")
                    return
            
            # Prepare values list
            values_list = [list(record.values()) for record in records]
            
            query = QueryBuilder.build_insert_query(table_name, columns, values_list)
            
            # Flatten values and sanitize
            flat_values = []
            for values in values_list:
                flat_values.extend([QueryBuilder.sanitize_value(v) for v in values])
            
            result = self.db.execute_query(query.as_string(self.db.cursor), tuple(flat_values))
            
            print(f"✅ Successfully inserted {len(records)} records into '{table_name}'")
            print(f"Rows affected: {self.db.cursor.rowcount}")
            
            return result
            
        except Exception as e:
            print(f"Error inserting multiple records: {str(e)}")
            return None