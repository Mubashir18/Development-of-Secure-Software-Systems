-- Sample data insertion

INSERT INTO authors (name, country) VALUES
('George Orwell', 'UK'),
('Jane Austen', 'UK'),
('Leo Tolstoy', 'Russia'),
('Mark Twain', 'USA');

INSERT INTO books (title, author_id, isbn, publication_year) VALUES
('1984', 1, '9780451524935', 1949),
('Pride and Prejudice', 2, '9780141439518', 1813),
('War and Peace', 3, '9780199232765', 1869),
('The Adventures of Tom Sawyer', 4, '9780486400778', 1876);

INSERT INTO members (name, email, join_date) VALUES
('Alice Johnson', 'alice@example.com', '2024-01-15'),
('Bob Smith', 'bob@example.com', '2024-02-20'),
('Carol White', 'carol@example.com', '2024-03-10'),
('David Brown', 'david@example.com', '2024-03-25');

INSERT INTO borrowings (book_id, member_id, borrow_date, return_date) VALUES
(1, 1, '2024-03-01', '2024-03-15'),
(2, 2, '2024-03-05', NULL),
(3, 1, '2024-03-20', NULL),
(4, 3, '2024-03-10', '2024-03-20');
