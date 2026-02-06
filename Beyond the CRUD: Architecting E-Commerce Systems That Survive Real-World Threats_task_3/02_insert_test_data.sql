-- Insert sample data for testing
INSERT INTO categories (category_name, description) VALUES
('Electronics', 'Electronic devices and accessories'),
('Clothing', 'Apparel and fashion items'),
('Books', 'Books and publications'),
('Home & Kitchen', 'Home appliances and kitchenware'),
('Sports', 'Sports equipment and accessories');

INSERT INTO suppliers (supplier_name, contact_person, email, phone, address) VALUES
('TechSupplies Inc.', 'John Doe', 'john@techsupplies.com', '+1234567890', '123 Tech Street, Silicon Valley'),
('FashionHub Ltd.', 'Jane Smith', 'jane@fashionhub.com', '+1987654321', '456 Fashion Ave, New York'),
('BookWorld Distributors', 'Robert Brown', 'robert@bookworld.com', '+1122334455', '789 Knowledge Road, Boston'),
('HomeEssentials Co.', 'Sarah Johnson', 'sarah@homeessentials.com', '+1555666777', '321 Comfort Lane, Chicago');

INSERT INTO products (product_name, category_id, supplier_id, price, cost, quantity, sku, description) VALUES
('Smartphone X10', 1, 1, 999.99, 700.00, 50, 'SKU-ELEC-001', 'Latest smartphone with advanced features'),
('Laptop Pro 15', 1, 1, 1499.99, 1100.00, 30, 'SKU-ELEC-002', 'High-performance laptop for professionals'),
('T-Shirt Casual', 2, 2, 29.99, 15.00, 200, 'SKU-CLOTH-001', 'Comfortable cotton t-shirt'),
('Programming Book', 3, 3, 49.99, 25.00, 100, 'SKU-BOOK-001', 'Learn programming from scratch'),
('Coffee Maker', 4, 4, 89.99, 50.00, 75, 'SKU-HOME-001', 'Automatic coffee maker with timer');

INSERT INTO inventory_transactions (product_id, transaction_type, quantity_change, previous_quantity, new_quantity, reference, notes, created_by) VALUES
(1, 'PURCHASE', 50, 0, 50, 'PO-001', 'Initial stock purchase', 'admin'),
(2, 'PURCHASE', 30, 0, 30, 'PO-002', 'Initial stock purchase', 'admin'),
(3, 'PURCHASE', 200, 0, 200, 'PO-003', 'Initial stock purchase', 'admin'),
(1, 'SALE', -5, 50, 45, 'SO-001', 'Sold to retail customer', 'sales'),
(2, 'SALE', -3, 30, 27, 'SO-002', 'Corporate sale', 'sales');