create_my_db = "CREATE DATABASE IF NOT EXISTS bookstore_anton_t"
use_my_db = "USE bookstore_anton_t"

create_table_books = """CREATE TABLE IF NOT EXISTS books
                        (
                            id     int auto_increment primary key,
                            title  varchar(50),
                            author varchar(50),
                            price float,
                            stock int
                        )"""

create_table_users = """CREATE TABLE IF NOT EXISTS users
                        (
                            id         int auto_increment primary key,
                            name varchar(50),
                            password  varchar(50),
                            balance    float
                        )"""

insert_books = """INSERT INTO books (title, author, price, stock)
                  VALUES (%s, %s, %s, %s)"""

if_book_already_exists = """
SELECT title, author FROM books WHERE title = %s and author = %s"""

update_books_quantity = """UPDATE books
                           SET stock = stock + %s
                           WHERE title = %s
                             and author = %s"""

insert_new_user_into_users = """INSERT INTO users (name, password, balance)
                                VALUES (%s, %s, %s)"""

if_user_exists = """SELECT name FROM users WHERE name = %s"""