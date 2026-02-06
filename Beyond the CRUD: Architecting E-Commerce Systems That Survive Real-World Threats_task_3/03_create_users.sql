-- Create different users with specific permissions
-- App user with limited permissions
CREATE USER app_user WITH PASSWORD 'app_password123';
GRANT CONNECT ON DATABASE ecommerce_db TO app_user;
GRANT USAGE ON SCHEMA public TO app_user;
GRANT SELECT, INSERT, UPDATE ON ALL TABLES IN SCHEMA public TO app_user;
GRANT USAGE ON ALL SEQUENCES IN SCHEMA public TO app_user;

-- Read-only user for reporting
CREATE USER report_user WITH PASSWORD 'report_pass456';
GRANT CONNECT ON DATABASE ecommerce_db TO report_user;
GRANT USAGE ON SCHEMA public TO report_user;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO report_user;

-- Admin user (not the superuser)
CREATE USER inventory_admin WITH PASSWORD 'admin_pass789';
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO inventory_admin;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO inventory_admin;