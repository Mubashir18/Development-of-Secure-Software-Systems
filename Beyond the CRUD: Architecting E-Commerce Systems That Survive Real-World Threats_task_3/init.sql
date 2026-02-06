-- Main initialization script
\i /docker-entrypoint-initdb.d/01_create_tables.sql
\i /docker-entrypoint-initdb.d/02_insert_test_data.sql
\i /docker-entrypoint-initdb.d/03_create_users.sql