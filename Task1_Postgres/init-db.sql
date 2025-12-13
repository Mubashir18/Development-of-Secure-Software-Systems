-- init-db.sql
-- Create database with proper locale
CREATE DATABASE mydb
  WITH ENCODING='UTF8'
       LC_COLLATE='ru_RU.UTF-8'
       LC_CTYPE='ru_RU.UTF-8'
       TEMPLATE=template0;

-- Connect to new database
\c mydb;

-- Create limited user for application
CREATE ROLE app_user LOGIN PASSWORD 'AppUserPass1';

-- Grant minimal permissions
GRANT CONNECT ON DATABASE mydb TO app_user;
GRANT USAGE ON SCHEMA public TO app_user;

-- Optional: Create a test table
CREATE TABLE IF NOT EXISTS test_table (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

GRANT SELECT ON test_table TO app_user;