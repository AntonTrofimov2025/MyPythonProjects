import os

from dotenv import load_dotenv
import pymysql
from pymysql.cursors import DictCursor
from sql import *

load_dotenv(".env_edit")


class DB:
    def __init__(self):
        self.__config = {"host": os.environ.get("DB_HOST", "localhost"),
                         "user": os.environ.get("DB_USER", "username"),
                         "password": os.environ.get("DB_PASSWORD", "password"),
                         "cursorclass": DictCursor}
        # self.__conn = None
        # self.__cursor = None
        self.user_data = None

    def __enter__(self):
        self.__conn = pymysql.connect(**self.__config)
        self.__cursor = self.__conn.cursor()
        print("Connection successful!")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.__cursor:
            self.__cursor.close()
        if self.__conn:
            if exc_type:
                self.__conn.rollback()
            else:
                self.__conn.commit()
            self.__conn.close()

    @property
    def cursor(self):
        return self.__cursor

    def use_bookstore(self):
        self.__cursor.execute(use_my_db)

    def create_db(self):
        self.__cursor.execute(create_my_db)
        self.__cursor.execute("SHOW DATABASES LIKE 'bookstore_anton_t'")
        db_check = self.__cursor.fetchone()
        if db_check:
            print("Database 'bookstore' created or already exists.")
        else:
            print("Database was not created (unknown reason).")

    def create_table_book(self):
        return self.__cursor.execute(create_table_books)

    def create_table_users(self):
        return self.__cursor.execute(create_table_users)

    def upload_your_books(self, books_file_name_csv):
        file_lines_into_list = []
        update_count = 0
        with open(books_file_name_csv, "r", encoding="utf-8") as file:
            for line in file:
                line = line.strip().split(",")
                if len(line) != 4:
                    print("Use only these fields: title, author, price, stock")
                    break
                title, author, price, stock = line
                line = (title, author, float(price), int(stock))
                if self.__cursor.execute(if_book_already_exists, (title, author)):
                    self.__cursor.execute(update_books_quantity, (stock, title, author))
                    update_count += 1
                else:
                    file_lines_into_list.append(line)
        self.__cursor.executemany(insert_books, file_lines_into_list)
        self.__conn.commit()
        print(f"{len(file_lines_into_list)} books uploaded. {update_count} updated.")
        file_lines_into_list.clear()

    def upload_one_book(self):
        while True:
            try:
                book_title = input("Please enter a book's title: ")
                if len(book_title) < 3:
                    raise IndexError("Book title must be at least 3 symbols in length!!")
                book_author = input("Please enter its author name: ")
                if len(book_author) < 2:
                    raise IndexError("Book author must be at least 2 symbols in length!!")

                if self.__cursor.execute(if_book_already_exists, (book_title, book_author)):
                    while True:
                        try:
                            book_in_stock = int(input("How many do you have?: "))
                            break
                        except ValueError:
                            print("For price and stock please use numbers only!!")
                    self.__cursor.execute(update_books_quantity, (book_in_stock, book_title, book_author))
                    self.__conn.commit()
                    print("The quantity of your book has been successfully updated :)")
                    return

                book_price = float(input("Please enter its price: "))
                book_in_stock = int(input("How many do you have?: "))

                break
            except IndexError as e:
                print(e)
            except ValueError:
                print("For price and stock please use numbers only!!")

        self.__cursor.execute(insert_books, (book_title, book_author, book_price, book_in_stock))
        self.__conn.commit()
        print("Your book has been successfully added to the bookstore :)")

    def show_me_books_in_file(self, books_file_name_csv):
        with open(books_file_name_csv, "r", encoding="utf-8") as file:
            print("Presented books in file: ")
            for line in file:
                line = line.strip().split(",")
                title, author, price, stock = line
                print(f" - {title} {author}, {price}€ {stock} Available.")

    def show_me_available_books(self):
        self.__cursor.execute(show_available_books)
        print("Presented books in our store: ")
        for num, book in enumerate(self.__cursor, 1):
            print(f" {num}. {book["title"]} by {book["author"]} - {book["price"]}€ ({book["stock"]} Available.)")

    def show_book_like(self):
        which_book = input("Enter full book's title or partially: ")
        self.__cursor.execute(find_book_like, (f"%{which_book}%", ))
        books_found = self.__cursor.fetchall()
        if books_found:
            for book in books_found:
                print(f" - {book["title"]} by {book["author"]} - {book["price"]}€ ({book["stock"]} Available.)")
        else:
            print("No matching books found.")

    def buy_book(self, user_data):
        self.user_data = user_data
        desired_book = input("Please enter a title of desired book: ")
        if self.__cursor.execute(find_book_like, (f"%{desired_book}%", )):
            print("We found such books: ",
                  *(f' {book["id"]}. {book["title"]} {book["author"]}, {book["price"]}€ {book["stock"]} Available.' for book in
                    self.__cursor), sep="\n")
        else:
            print('The book not found.')
            return
        while True:
            try:
                choose_book_id = int(input("Please select book's id: "))
                quantity = int(input("How many would you like to buy?: "))
                if not quantity:
                    raise IndexError("The quantity cannot be negative or equal zero!!")
                break
            except ValueError:
                print('Use numbers to select your book (book_id) and quantity.')
            except IndexError as e:
                print(e)
        self.__cursor.execute(find_book_by_id, (choose_book_id,))
        selected_book = self.__cursor.fetchone()
        if not selected_book:
            print("'book_id' not found. We are so sorry. :'(((")
            return
        if quantity <= selected_book['stock']:
            try:
                if self.user_data['balance'] >= selected_book['price'] * quantity:
                    self.__cursor.execute("""UPDATE users
                                             SET balance = balance - %s
                                             WHERE id = %s""", (selected_book['price'] * quantity, self.user_data['id']))
                    self.__cursor.execute("""UPDATE books
                                             SET stock = stock - %s
                                             WHERE id = %s""", (quantity, selected_book['id'],))
                    self.__conn.commit()
                    print("Thank you for your purchase!! :)))")
                    return
                else:
                    print("Not enough cash to buy a book, we are sorry.")
                    return
            except Exception as e:
                print(f"Something went wrong: {e}")
                self.__conn.rollback()

        else:
            print('The desired book is currently not available.')
            return

    def user_registration(self):
        while True:
            try:
                your_credentials = input("Enter your login: ").lower()
                if len(your_credentials) < 4:
                    raise ValueError("Login must contain at least 4 symbols!!")
                if self.__cursor.execute(if_user_exists, your_credentials):
                    print("Such a user already exists in our system. We are really sorry.")
                    return
                break
            except ValueError as e:
                print(e)
        while True:
            try:
                your_pass = input("Set your unique password: ").lower()
                if len(your_pass) < 5:
                    raise ValueError("Password must be longer!! at least 5 symbols!!")
                break
            except ValueError as e:
                print(e)
        while True:
            try:
                init_balance = int(input("Choose your initial balance (EUR): "))
                break
            except ValueError:
                print("To set the balance use only numbers!!")
        self.__cursor.execute(insert_new_user_into_users, (your_credentials, your_pass, float(init_balance)))
        self.__conn.commit()
        print("Thank you for your registration! :)")

    def user_authorization(self):
        while True:
            login = input("Enter your login: ")
            password = input("Enter your password: ")
            if self.__cursor.execute(user_auth, (login, password)):
                print("Successful authorization!")
                return self.__cursor.fetchone()
            print("Invalid username or password")
            break
