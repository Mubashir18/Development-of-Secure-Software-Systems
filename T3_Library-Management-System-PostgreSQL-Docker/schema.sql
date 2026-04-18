-- Library Management System Database Schema

CREATE TABLE authors (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    country VARCHAR(50)
);

CREATE TABLE books (
    id SERIAL PRIMARY KEY,
    title VARCHAR(100) NOT NULL,
    author_id INTEGER NOT NULL REFERENCES authors(id),
    isbn VARCHAR(13) UNIQUE,
    publication_year INTEGER
);

CREATE TABLE members (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE,
    join_date DATE NOT NULL
);

CREATE TABLE borrowings (
    id SERIAL PRIMARY KEY,
    book_id INTEGER NOT NULL REFERENCES books(id),
    member_id INTEGER NOT NULL REFERENCES members(id),
    borrow_date DATE NOT NULL,
    return_date DATE
);
